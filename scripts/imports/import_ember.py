#!/usr/bin/env python3
"""
Import Ember Climate electricity data for Category 7 indicators

MAPPING EMBER → IRC:
1. Electricity generation (Hydro, %) → EG.ELC.HYRO.ZS
2. Electricity generation (Nuclear, %) → EG.ELC.NUCL.ZS  
3. Electricity generation (Total, TWh) → EG.ELC.PROD.KH (convertir TWh → kWh)
4. Electricity generation (Renewables, %) → EG.FEC.RNEW.ZS
5. Electricity demand (Demand per capita, MWh) → EG.USE.ELEC.KH.PC (convertir MWh → kWh)
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
    """Get country_id from ISO3 code"""
    cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_id(cursor, indicator_code):
    """Get indicator_id from code"""
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    """Check if value exists"""
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

def update_source(cursor, indicator_code):
    """Update indicator source to include Ember"""
    cursor.execute("SELECT source FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    if result and 'Ember' not in result[0]:
        new_source = result[0] + ' + Ember Climate'
        cursor.execute("UPDATE indicator SET source = %s WHERE code = %s", (new_source, indicator_code))

def import_ember_data(cursor, filepath):
    """Import all Ember indicators"""
    
    # Mapping: (Category, Subcategory, Variable, Unit) → (IRC_code, conversion_factor)
    mappings = {
        ('Electricity generation', 'Fuel', 'Hydro', '%'): ('EG.ELC.HYRO.ZS', 1.0),
        ('Electricity generation', 'Fuel', 'Nuclear', '%'): ('EG.ELC.NUCL.ZS', 1.0),
        ('Electricity generation', 'Total', 'Total Generation', 'TWh'): ('EG.ELC.PROD.KH', 1e9),  # TWh → kWh
        ('Electricity generation', 'Aggregate fuel', 'Renewables', '%'): ('EG.FEC.RNEW.ZS', 1.0),
        ('Electricity demand', 'Demand per capita', 'Demand per capita', 'MWh'): ('EG.USE.ELEC.KH.PC', 1000.0),  # MWh → kWh
    }
    
    # Stats per indicator
    stats = {}
    for _, (code, _) in mappings.items():
        stats[code] = {'new': 0, 'averaged': 0, 'skipped': 0, 'unmapped': 0}
    
    print("\n📊 Processing Ember Climate data...")
    print(f"   File: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract fields
            iso3 = row['ISO 3 code'].strip()
            year_str = row['Year'].strip()
            category = row['Category'].strip()
            subcategory = row['Subcategory'].strip()
            variable = row['Variable'].strip()
            unit = row['Unit'].strip()
            value_str = row['Value'].strip()
            
            # Check if this row matches a mapping
            key = (category, subcategory, variable, unit)
            if key not in mappings:
                continue
            
            irc_code, conversion = mappings[key]
            
            # Validate year
            try:
                year = int(year_str)
            except ValueError:
                stats[irc_code]['skipped'] += 1
                continue
            
            # Validate value
            if not value_str or value_str == '':
                stats[irc_code]['skipped'] += 1
                continue
            
            try:
                value = float(value_str) * conversion
            except ValueError:
                stats[irc_code]['skipped'] += 1
                continue
            
            # Get country ID
            country_id = get_country_id(cursor, iso3)
            if not country_id:
                stats[irc_code]['unmapped'] += 1
                continue
            
            # Get indicator ID
            indicator_id = get_indicator_id(cursor, irc_code)
            if not indicator_id:
                print(f"   ⚠️ Indicator {irc_code} not found in database")
                continue
            
            # Insert or average
            result = insert_or_average(cursor, country_id, indicator_id, year, value)
            if result == 'new':
                stats[irc_code]['new'] += 1
            else:
                stats[irc_code]['averaged'] += 1
    
    # Update sources
    for _, (code, _) in mappings.items():
        update_source(cursor, code)
    
    # Print results
    print("\n📈 RÉSULTATS PAR INDICATEUR:")
    print("="*100)
    
    indicator_names = {
        'EG.ELC.HYRO.ZS': 'Électricité hydroélectrique (%)',
        'EG.ELC.NUCL.ZS': 'Électricité nucléaire (%)',
        'EG.ELC.PROD.KH': 'Production électricité (kWh)',
        'EG.FEC.RNEW.ZS': 'Énergies renouvelables (%)',
        'EG.USE.ELEC.KH.PC': 'Consommation électricité/hab (kWh)'
    }
    
    total_new = 0
    total_avg = 0
    total_skip = 0
    
    for code in sorted(stats.keys()):
        s = stats[code]
        total_imported = s['new'] + s['averaged']
        total_new += s['new']
        total_avg += s['averaged']
        total_skip += s['skipped']
        
        print(f"\n🔹 {code} - {indicator_names.get(code, code)}")
        print(f"   ✓ {total_imported:,} valeurs importées ({s['new']:,} nouvelles + {s['averaged']:,} moyennées)")
        print(f"   Ignorées: {s['skipped']:,} valeurs manquantes, {s['unmapped']:,} pays non mappés")
    
    print("\n" + "="*100)
    print(f"📊 TOTAL: {total_new + total_avg:,} valeurs ({total_new:,} nouvelles + {total_avg:,} moyennées)")
    print(f"   Ignorées: {total_skip:,} au total")
    print("="*100)

def main():
    print("="*100)
    print("EMBER CLIMATE DATA IMPORT - CATEGORY 7 (ENERGY)")
    print("="*100)
    
    filepath = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/yearly_full_release_long_format.csv'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        import_ember_data(cursor, filepath)
        conn.commit()
        
        print("\n✅ Import completed successfully!")
        
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
