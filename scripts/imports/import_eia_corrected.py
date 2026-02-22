#!/usr/bin/env python3
"""
Import EIA fossil fuel data using direct series IDs
CORRECTED VERSION - Uses proper series ID pattern
"""

import psycopg2
import requests
import json
import time
from collections import defaultdict

API_KEY = "r7QTdgdAdzPDc5gO9SwuvzeEpkQaVpadNpnpDmN8"

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

def fetch_eia_series_batch(series_ids):
    """Fetch multiple series at once (max 100 per request)"""
    series_param = ';'.join(series_ids)
    url = f"https://api.eia.gov/v2/seriesid/{series_param}?api_key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=60)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        return data.get('series', [])
        
    except Exception as e:
        print(f"      ⚠️  Error: {e}")
        return None

def fetch_all_fuel_data(countries, series_pattern, fuel_name):
    """Fetch data for all countries using series pattern"""
    
    print(f"\n   📥 {fuel_name}...")
    
    all_data = defaultdict(dict)  # {iso3: {year: value}}
    iso3_list = sorted(countries.keys())
    
    # Process in batches of 100
    for i in range(0, len(iso3_list), 100):
        batch = iso3_list[i:i+100]
        series_ids = [series_pattern.replace('<ISO3>', iso3) for iso3 in batch]
        
        series_data = fetch_eia_series_batch(series_ids)
        
        if series_data:
            for series in series_data:
                series_id = series.get('series_id', '')
                # Extract ISO3 from series_id: INTL.44-2-USA-QBTU.A -> USA
                parts = series_id.split('-')
                if len(parts) >= 3:
                    iso3 = parts[2]
                    
                    for point in series.get('data', []):
                        year_str = point[0]
                        value = point[1]
                        
                        # Skip non-numeric values
                        if isinstance(value, str) or value is None:
                            continue
                        
                        try:
                            year = int(year_str)
                            all_data[iso3][year] = float(value)
                        except (ValueError, TypeError):
                            continue
        
        processed = min(i + 100, len(iso3_list))
        if (i // 100 + 1) % 5 == 0:
            print(f"      {processed}/{len(iso3_list)} countries processed...")
        
        time.sleep(0.3)  # Rate limiting
    
    total_records = sum(len(years) for years in all_data.values())
    print(f"      ✅ {len(all_data)} countries, {total_records} records")
    
    return all_data

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
            
            fossil_percentages.append({
                'country': iso3,
                'year': year,
                'percentage': round(fossil_pct, 2)
            })
    
    print(f"   ✅ {len(fossil_percentages):,} country-year percentages calculated")
    
    # Statistics
    years = [r['year'] for r in fossil_percentages]
    countries_set = set(r['country'] for r in fossil_percentages)
    
    print(f"   📊 Countries: {len(countries_set)}")
    print(f"   📅 Years: {min(years)}-{max(years)}")
    
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
    
    for record in fossil_percentages:
        iso3 = record['country']
        year = record['year']
        value = record['percentage']
        
        # Get country ID
        if iso3 not in countries_map:
            skip_count += 1
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
        print(f"   ⚠️  {skip_count:,} skipped (country not in DB)")
    
    return final_countries

def main():
    print("="*80)
    print("EIA FOSSIL FUEL IMPORT - CORRECTED VERSION")
    print("Using direct series IDs for accurate data retrieval")
    print("="*80)
    
    # Get all countries
    print("\n📋 Loading countries from database...")
    countries = get_all_countries()
    print(f"   ✅ {len(countries)} countries loaded")
    
    # Series ID patterns
    print(f"\n📡 Fetching EIA data for 4 fuel types...")
    print("   Series patterns:")
    print("   - Total:  INTL.44-2-<ISO3>-QBTU.A")
    print("   - Coal:   INTL.4411-2-<ISO3>-QBTU.A")
    print("   - Oil:    INTL.4412-2-<ISO3>-QBTU.A")
    print("   - Gas:    INTL.4413-2-<ISO3>-QBTU.A")
    
    total_data = fetch_all_fuel_data(countries, 'INTL.44-2-<ISO3>-QBTU.A', 'Total Primary Energy')
    coal_data = fetch_all_fuel_data(countries, 'INTL.4411-2-<ISO3>-QBTU.A', 'Coal Consumption')
    oil_data = fetch_all_fuel_data(countries, 'INTL.4412-2-<ISO3>-QBTU.A', 'Petroleum Consumption')
    gas_data = fetch_all_fuel_data(countries, 'INTL.4413-2-<ISO3>-QBTU.A', 'Natural Gas Consumption')
    
    if not total_data:
        print("\n❌ Failed to fetch total energy data")
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

if __name__ == '__main__':
    main()
