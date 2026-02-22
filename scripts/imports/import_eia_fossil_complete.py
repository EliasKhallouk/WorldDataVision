#!/usr/bin/env python3
"""
Import EIA fossil fuel data and calculate % of total primary energy
Semantic: Fossil fuels (coal + oil + gas) as % of TOTAL primary energy consumption
"""

import psycopg2
import requests
import json
import time
from collections import defaultdict

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_country_id(cursor, iso3_code):
    """Get country ID from ISO3 code"""
    cursor.execute("SELECT id, name FROM country WHERE iso3 = %s", (iso3_code,))
    result = cursor.fetchone()
    return result if result else None

def get_indicator_id(cursor, indicator_code):
    """Get indicator ID"""
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    """Check if value already exists"""
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    return cursor.fetchone()

def insert_or_average(cursor, country_id, indicator_id, year, new_value):
    """Insert new value or average with existing"""
    existing = value_exists(cursor, country_id, indicator_id, year)
    
    if existing:
        avg_value = (existing[0] + new_value) / 2
        cursor.execute("""
            UPDATE indicator_value 
            SET value = %s 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (avg_value, country_id, indicator_id, year))
        return 'averaged'
    else:
        cursor.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (country_id, indicator_id, year, new_value))
        return 'new'

def fetch_eia_data(api_key, product_id, activity_id, product_name):
    """
    Fetch EIA data for specific product and activity
    
    Product IDs:
    - 44 = Total primary energy consumption
    - 47 = Coal consumption  
    - 54 = Petroleum and other liquids consumption
    - 35 = Natural gas consumption
    
    Activity IDs:
    - 1 = Total consumption
    """
    
    print(f"   Fetching: {product_name}...")
    
    base_url = "https://api.eia.gov/v2/international/data/"
    
    params = {
        'api_key': api_key,
        'frequency': 'annual',
        'data[0]': 'value',
        'facets[productId][]': product_id,
        'facets[activityId][]': activity_id,
        'start': '1980',
        'end': '2023',
        'offset': 0,
        'length': 5000
    }
    
    all_data = []
    offset = 0
    
    while True:
        params['offset'] = offset
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"      ❌ Error {response.status_code}")
                break
            
            data = response.json()
            
            if 'response' not in data or 'data' not in data['response']:
                break
            
            records = data['response']['data']
            if not records:
                break
            
            all_data.extend(records)
            
            # Check if there's more data
            total = data['response'].get('total', 0)
            try:
                total = int(total)
            except (ValueError, TypeError):
                total = len(all_data)
            
            print(f"      Downloaded {len(all_data)}/{total} records...")
            
            if len(all_data) >= total:
                break
            
            offset += 5000
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            break
    
    print(f"      ✅ Total: {len(all_data)} records")
    return all_data

def calculate_fossil_percentages(coal_data, oil_data, gas_data, total_data):
    """
    Calculate fossil fuel % for each country/year
    Fossil % = (Coal + Oil + Gas) / Total * 100
    """
    
    print("\n📊 Calculating fossil fuel percentages...")
    
    # Organize data by country and year
    totals = defaultdict(dict)
    coal = defaultdict(dict)
    oil = defaultdict(dict)
    gas = defaultdict(dict)
    
    # Process total primary energy
    for record in total_data:
        country = record.get('countryRegionId')
        year_str = record.get('period')
        value = record.get('value')
        
        if not country or not year_str or value is None:
            continue
        
        try:
            year = int(year_str)
            totals[country][year] = float(value)
        except (ValueError, TypeError):
            continue
    
    # Process coal
    for record in coal_data:
        country = record.get('countryRegionId')
        year_str = record.get('period')
        value = record.get('value')
        
        if not country or not year_str or value is None:
            continue
        
        try:
            year = int(year_str)
            coal[country][year] = float(value)
        except (ValueError, TypeError):
            continue
    
    # Process oil
    for record in oil_data:
        country = record.get('countryRegionId')
        year_str = record.get('period')
        value = record.get('value')
        
        if not country or not year_str or value is None:
            continue
        
        try:
            year = int(year_str)
            oil[country][year] = float(value)
        except (ValueError, TypeError):
            continue
    
    # Process gas
    for record in gas_data:
        country = record.get('countryRegionId')
        year_str = record.get('period')
        value = record.get('value')
        
        if not country or not year_str or value is None:
            continue
        
        try:
            year = int(year_str)
            gas[country][year] = float(value)
        except (ValueError, TypeError):
            continue
    
    # Calculate percentages
    fossil_percentages = []
    
    for country in totals:
        for year in totals[country]:
            total = totals[country][year]
            
            if total <= 0:
                continue
            
            coal_val = coal.get(country, {}).get(year, 0)
            oil_val = oil.get(country, {}).get(year, 0)
            gas_val = gas.get(country, {}).get(year, 0)
            
            fossil_total = coal_val + oil_val + gas_val
            fossil_pct = (fossil_total / total) * 100
            
            fossil_percentages.append({
                'country': country,
                'year': year,
                'percentage': round(fossil_pct, 2)
            })
    
    print(f"   ✅ Calculated {len(fossil_percentages)} country-year percentages")
    print(f"   📊 Countries: {len(set(r['country'] for r in fossil_percentages))}")
    print(f"   📅 Years: {min(r['year'] for r in fossil_percentages)}-{max(r['year'] for r in fossil_percentages)}")
    
    return fossil_percentages

def import_to_database(cursor, fossil_percentages, indicator_id):
    """Import calculated percentages to database"""
    
    print("\n💾 Importing to database...")
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    unmapped_countries = set()
    
    for record in fossil_percentages:
        iso3 = record['country']
        year = record['year']
        value = record['percentage']
        
        # Get country ID
        country_info = get_country_id(cursor, iso3)
        if not country_info:
            skip_count += 1
            unmapped_countries.add(iso3)
            continue
        
        country_id = country_info[0]
        
        # Insert or average
        result = insert_or_average(cursor, country_id, indicator_id, year, value)
        if result == 'new':
            new_count += 1
        else:
            avg_count += 1
    
    total = new_count + avg_count
    print(f"   ✅ {total:,} values imported ({new_count:,} new + {avg_count:,} averaged)")
    
    if unmapped_countries:
        print(f"\n   ⚠️  {skip_count:,} values skipped from {len(unmapped_countries)} unmapped countries:")
        # Show first 20 unmapped countries
        for country in sorted(unmapped_countries)[:20]:
            print(f"      - {country}")
        if len(unmapped_countries) > 20:
            print(f"      ... and {len(unmapped_countries) - 20} more")
    
    return new_count, avg_count, unmapped_countries

def main():
    print("="*80)
    print("EIA FOSSIL FUEL DATA IMPORT - COMPLETE")
    print("Fossil fuels (coal + oil + gas) as % of TOTAL primary energy")
    print("="*80)
    
    api_key = input("\nEnter your EIA API key: ").strip()
    
    if not api_key or len(api_key) < 10:
        print("❌ Invalid API key")
        return
    
    print("\n📥 Downloading EIA data...")
    print("   This will download 4 datasets and calculate percentages")
    print()
    
    # Download all necessary data
    # Product IDs from EIA documentation
    total_data = fetch_eia_data(api_key, '44', '1', 'Total Primary Energy Consumption')
    coal_data = fetch_eia_data(api_key, '47', '1', 'Coal Consumption')
    oil_data = fetch_eia_data(api_key, '54', '1', 'Petroleum Consumption')
    gas_data = fetch_eia_data(api_key, '35', '1', 'Natural Gas Consumption')
    
    if not total_data:
        print("\n❌ Failed to download total energy data")
        return
    
    # Calculate percentages
    fossil_percentages = calculate_fossil_percentages(coal_data, oil_data, gas_data, total_data)
    
    if not fossil_percentages:
        print("\n❌ No data to import")
        return
    
    # Import to database
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        indicator_code = 'EG.USE.COMM.FO.ZS'
        indicator_id = get_indicator_id(cursor, indicator_code)
        
        if not indicator_id:
            print(f"\n❌ Indicator {indicator_code} not found in database")
            return
        
        new_count, avg_count, unmapped_countries = import_to_database(cursor, fossil_percentages, indicator_id)
        
        conn.commit()
        
        # Count final coverage
        cursor.execute("""
            SELECT COUNT(DISTINCT country_id) 
            FROM indicator_value 
            WHERE indicator_id = %s
        """, (indicator_id,))
        countries = cursor.fetchone()[0]
        
        print(f"\n✅ Import completed!")
        print(f"   Final coverage: {countries} countries")
        print(f"   Source: World Bank + OWID + EIA")
        
        # Suggest adding missing countries
        if unmapped_countries:
            print(f"\n💡 To improve coverage by {len(unmapped_countries)} countries:")
            print(f"   Add these ISO3 codes to the 'country' table")
            print(f"   (use scripts/add_missing_countries.py if available)")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
