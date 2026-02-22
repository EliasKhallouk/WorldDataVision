#!/usr/bin/env python3
"""
Import OWID fossil_share_energy data for EG.USE.COMM.FO.ZS
This is the correct semantic match: fossil fuels in TOTAL energy (not just electricity)
"""

import psycopg2
import csv
import os

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_country_id(cursor, iso3_code):
    cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_id(cursor, indicator_code):
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    return cursor.fetchone()

def insert_or_average(cursor, country_id, indicator_id, year, new_value):
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

def update_source(cursor, indicator_code):
    cursor.execute("SELECT source FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    if result:
        # Source already has "World Bank + Our World in Data..."
        # Just ensure it says the right thing
        new_source = "World Bank + Our World in Data (Fossil fuel energy consumption %)"
        cursor.execute("UPDATE indicator SET source = %s WHERE code = %s", (new_source, indicator_code))

def import_owid_fossil(cursor, filepath):
    """
    Import OWID fossil_share_energy → EG.USE.COMM.FO.ZS
    This is energy TOTAL, not just electricity (semantically correct!)
    """
    
    indicator_code = 'EG.USE.COMM.FO.ZS'
    indicator_id = get_indicator_id(cursor, indicator_code)
    
    if not indicator_id:
        print(f"❌ Indicator {indicator_code} not found")
        return
    
    print(f"\n📊 Processing OWID fossil_share_energy → {indicator_code}")
    print("   ✅ Sémantique: Fossiles dans ÉNERGIE TOTALE (correct!)")
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    unmapped_count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            iso3 = row.get('iso_code', '').strip()
            year_str = row.get('year', '').strip()
            value_str = row.get('fossil_share_energy', '').strip()
            
            # Skip if missing
            if not iso3 or not year_str or not value_str:
                skip_count += 1
                continue
            
            # Validate year
            try:
                year = int(year_str)
            except ValueError:
                skip_count += 1
                continue
            
            # Validate value
            try:
                value = float(value_str)
            except ValueError:
                skip_count += 1
                continue
            
            # Get country
            country_id = get_country_id(cursor, iso3)
            if not country_id:
                unmapped_count += 1
                continue
            
            # Insert or average
            result = insert_or_average(cursor, country_id, indicator_id, year, value)
            if result == 'new':
                new_count += 1
            else:
                avg_count += 1
    
    update_source(cursor, indicator_code)
    
    total = new_count + avg_count
    print(f"   ✓ {total:,} valeurs importées ({new_count:,} nouvelles + {avg_count:,} moyennées)")
    print(f"   Ignorées: {skip_count:,} valeurs manquantes, {unmapped_count:,} pays non mappés")

def main():
    print("="*80)
    print("OWID FOSSIL SHARE ENERGY IMPORT - EG.USE.COMM.FO.ZS")
    print("="*80)
    
    filepath = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/OWID/owid-energy-data.csv'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        import_owid_fossil(cursor, filepath)
        conn.commit()
        
        # Count final coverage
        cursor.execute("""
            SELECT COUNT(DISTINCT country_id) FROM indicator_value 
            WHERE indicator_id = (SELECT id FROM indicator WHERE code = 'EG.USE.COMM.FO.ZS')
        """)
        countries = cursor.fetchone()[0]
        
        print(f"\n✅ Import completed!")
        print(f"   Couverture finale: {countries} pays")
        
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
