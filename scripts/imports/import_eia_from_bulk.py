#!/usr/bin/env python3
"""
Parse EIA bulk file directly to extract fossil fuel data
Most reliable method - no API limits or issues
"""

import psycopg2
import json
import re
from collections import defaultdict

BULK_FILE = '/tmp/INTL.txt'

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_all_countries():
    """Get all ISO3 codes from database"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT iso3, id, name 
        FROM country 
        WHERE iso3 IS NOT NULL AND iso3 != '' AND LENGTH(iso3) = 3
        ORDER BY iso3
    """)
    countries = {row[0]: {'id': row[1], 'name': row[2]} for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return countries

def parse_bulk_file():
    """Parse EIA bulk file to extract fossil fuel consumption data"""
    
    print("\n📥 Parsing EIA bulk file...")
    print(f"   File: {BULK_FILE}")
    
    # Data structures
    total_data = defaultdict(dict)  # {iso3: {year: value}}
    coal_data = defaultdict(dict)
    oil_data = defaultdict(dict)
    gas_data = defaultdict(dict)
    
    # Series patterns we want (annual data in QBTU)
    patterns = {
        'total': re.compile(r'"series_id":"INTL\.44-2-([A-Z]{3})-QBTU\.A"'),
        'coal': re.compile(r'"series_id":"INTL\.4411-2-([A-Z]{3})-QBTU\.A"'),
        'oil': re.compile(r'"series_id":"INTL\.5-2-([A-Z]{3})-QBTU\.A"'),  # CORRECTED: 5-2 for petroleum
        'gas': re.compile(r'"series_id":"INTL\.4413-2-([A-Z]{3})-QBTU\.A"')
    }
    
    counters = {k: 0 for k in patterns}
    
    with open(BULK_FILE, 'r') as f:
        for i, line in enumerate(f):
            if (i + 1) % 50000 == 0:
                print(f"      Processed {i+1:,} lines...")
            
            # Check if this line matches any pattern
            for fuel_type, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    iso3 = match.group(1)
                    counters[fuel_type] += 1
                    
                    # Parse the JSON
                    try:
                        series = json.loads(line)
                        data_points = series.get('data', [])
                        
                        # Store each year-value pair
                        for point in data_points:
                            year_str = point[0]
                            value = point[1]
                            
                            # Skip non-numeric values
                            if isinstance(value, str) or value is None:
                                continue
                            
                            try:
                                year = int(year_str)
                                value_float = float(value)
                                
                                if fuel_type == 'total':
                                    total_data[iso3][year] = value_float
                                elif fuel_type == 'coal':
                                    coal_data[iso3][year] = value_float
                                elif fuel_type == 'oil':
                                    oil_data[iso3][year] = value_float
                                elif fuel_type == 'gas':
                                    gas_data[iso3][year] = value_float
                            except (ValueError, TypeError):
                                continue
                    
                    except json.JSONDecodeError:
                        continue
                    
                    break  # Found match, no need to check other patterns
    
    print(f"\n   ✅ Parsing complete!")
    print(f"   📊 Series found:")
    for fuel_type, count in counters.items():
        records = 0
        if fuel_type == 'total':
            records = sum(len(years) for years in total_data.values())
        elif fuel_type == 'coal':
            records = sum(len(years) for years in coal_data.values())
        elif fuel_type == 'oil':
            records = sum(len(years) for years in oil_data.values())
        elif fuel_type == 'gas':
            records = sum(len(years) for years in gas_data.values())
        
        print(f"      {fuel_type:6s}: {count:3d} countries, {records:,} records")
    
    return total_data, coal_data, oil_data, gas_data

def calculate_fossil_percentages(total_data, coal_data, oil_data, gas_data):
    """Calculate fossil % = (coal + oil + gas) / total * 100"""
    
    print(f"\n📊 Calculating fossil fuel percentages...")
    
    fossil_percentages = []
    
    for iso3 in total_data:
        for year in total_data[iso3]:
            total = total_data[iso3][year]
            
            if total <= 0:
                continue
            
            coal = coal_data.get(iso3, {}).get(year, 0)
            oil = oil_data.get(iso3, {}).get(year, 0)
            gas = gas_data.get(iso3, {}).get(year, 0)
            
            fossil_total = coal + oil + gas
            fossil_pct = (fossil_total / total) * 100
            
            # Cap at 100% (in case of rounding errors)
            fossil_pct = min(fossil_pct, 100.0)
            
            fossil_percentages.append({
                'country': iso3,
                'year': year,
                'percentage': round(fossil_pct, 2)
            })
    
    print(f"   ✅ {len(fossil_percentages):,} country-year percentages")
    
    # Statistics
    years = [r['year'] for r in fossil_percentages]
    countries_set = set(r['country'] for r in fossil_percentages)
    percentages = [r['percentage'] for r in fossil_percentages]
    
    print(f"   📊 Countries: {len(countries_set)}")
    print(f"   📅 Years: {min(years)}-{max(years)}")
    print(f"   📈 Fossil %: {min(percentages):.1f}% - {max(percentages):.1f}%")
    
    return fossil_percentages

def import_to_database(fossil_percentages, countries_map):
    """Import calculated percentages"""
    
    print(f"\n💾 Importing to database...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get indicator ID
    cursor.execute("SELECT id FROM indicator WHERE code = 'EG.USE.COMM.FO.ZS'")
    indicator_id = cursor.fetchone()[0]
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    skipped_countries = set()
    
    for record in fossil_percentages:
        iso3 = record['country']
        year = record['year']
        value = record['percentage']
        
        # Get country ID
        if iso3 not in countries_map:
            skip_count += 1
            skipped_countries.add(iso3)
            continue
        
        country_id = countries_map[iso3]['id']
        
        # Check if exists
        cursor.execute("""
            SELECT value FROM indicator_value 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (country_id, indicator_id, year))
        
        existing = cursor.fetchone()
        
        if existing:
            # Average with existing
            avg_value = (existing[0] + value) / 2
            cursor.execute("""
                UPDATE indicator_value 
                SET value = %s 
                WHERE country_id = %s AND indicator_id = %s AND year = %s
            """, (avg_value, country_id, indicator_id, year))
            avg_count += 1
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                VALUES (%s, %s, %s, %s)
            """, (country_id, indicator_id, year, value))
            new_count += 1
    
    conn.commit()
    
    # Final coverage
    cursor.execute("""
        SELECT COUNT(DISTINCT country_id) 
        FROM indicator_value 
        WHERE indicator_id = %s
    """, (indicator_id,))
    final_countries = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    total = new_count + avg_count
    print(f"   ✅ {total:,} values imported ({new_count:,} new + {avg_count:,} averaged)")
    
    if skip_count > 0:
        # Filter out region codes
        real_countries = [c for c in skipped_countries if len(c) == 3 and not any(x in c for x in ['OECD', 'OPEC', 'EURO', 'AFRC', 'ASOC', 'MIDE', 'CSAM', 'NOAM', 'DEUW', 'NOEC'])]
        
        if real_countries:
            print(f"\n   ⚠️  {len(real_countries)} unmapped countries:")
            for iso3 in sorted(real_countries)[:20]:
                print(f"      - {iso3}")
            if len(real_countries) > 20:
                print(f"      ... and {len(real_countries) - 20} more")
        
        regions = [c for c in skipped_countries if c not in real_countries]
        if regions:
            print(f"   ℹ️  {len(regions)} regional aggregations skipped (normal)")
    
    return final_countries

def main():
    print("="*80)
    print("EIA FOSSIL FUEL IMPORT - BULK FILE METHOD")
    print("Direct parsing of EIA bulk file (most reliable)")
    print("="*80)
    
    # Get countries
    print("\n📋 Loading countries from database...")
    countries = get_all_countries()
    print(f"   ✅ {len(countries)} countries loaded")
    
    # Parse bulk file
    total_data, coal_data, oil_data, gas_data = parse_bulk_file()
    
    if not total_data:
        print("\n❌ No total energy data found")
        return
    
    # Calculate percentages
    fossil_percentages = calculate_fossil_percentages(total_data, coal_data, oil_data, gas_data)
    
    if not fossil_percentages:
        print("\n❌ No data to import")
        return
    
    # Import
    final_countries = import_to_database(fossil_percentages, countries)
    
    print(f"\n{'='*80}")
    print("✅ IMPORT COMPLETED!")
    print(f"{'='*80}")
    print(f"Final coverage: {final_countries} countries")
    print(f"Source: World Bank + OWID + EIA")
    print(f"Data completeness: All 4 fuel types (total, coal, oil, gas)")

if __name__ == '__main__':
    main()
