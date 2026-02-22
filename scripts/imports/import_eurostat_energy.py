#!/usr/bin/env python3
"""
Import Eurostat energy data for Category 7 indicators
"""

import psycopg2
import csv
import os
from datetime import datetime

# Database connection
def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user=os.getenv('USER', 'elias'),
        password="MaBaseDeDonnee",
        host="localhost"
    )

# Country mapping Eurostat (ISO2) to IRC (ISO3)
EUROSTAT_TO_ISO3 = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP',
    'CZ': 'CZE', 'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA',
    'DE': 'DEU', 'EL': 'GRC', 'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA',
    'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX', 'MT': 'MLT', 'NL': 'NLD',
    'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK', 'SI': 'SVN',
    'ES': 'ESP', 'SE': 'SWE', 'UK': 'GBR',
    'IS': 'ISL', 'NO': 'NOR', 'CH': 'CHE', 'LI': 'LIE',  # EFTA
    'TR': 'TUR', 'RS': 'SRB', 'ME': 'MNE', 'MK': 'MKD',  # Candidates
    'AL': 'ALB', 'BA': 'BIH', 'XK': 'XKX',
    'UA': 'UKR', 'MD': 'MDA', 'GE': 'GEO'  # Eastern Europe
}

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
    """Check if value exists for country/indicator/year"""
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    return cursor.fetchone()

def insert_or_average(cursor, country_id, indicator_id, year, new_value):
    """Insert new value or average with existing"""
    existing = value_exists(cursor, country_id, indicator_id, year)
    
    if existing:
        # Average with existing value
        avg_value = (existing[0] + new_value) / 2
        cursor.execute("""
            UPDATE indicator_value 
            SET value = %s 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (avg_value, country_id, indicator_id, year))
        return 'averaged'
    else:
        # Insert new value
        cursor.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (country_id, indicator_id, year, new_value))
        return 'new'

def update_source(cursor, indicator_code):
    """Update indicator source to include Eurostat"""
    cursor.execute("SELECT source FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    if result and 'Eurostat' not in result[0]:
        new_source = result[0] + ' + Eurostat'
        cursor.execute("UPDATE indicator SET source = %s WHERE code = %s", (new_source, indicator_code))

def parse_eurostat_tsv(filepath):
    """Parse Eurostat TSV format and extract years and data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        
        # Extract year columns (all columns after first)
        year_columns = []
        for col in header[1:]:
            try:
                year = int(col.strip())
                year_columns.append(year)
            except ValueError:
                continue
        
        # Read data rows
        data_rows = []
        for row in reader:
            if len(row) > 1:
                data_rows.append(row)
        
        return year_columns, data_rows

def import_energy_dependence(cursor, filepath):
    """Import nrg_ind_id: Energy dependency rate → EG.IMP.CONS.ZS"""
    print("\n📊 Processing Energy Dependency (nrg_ind_id)...")
    
    indicator_code = 'EG.IMP.CONS.ZS'
    indicator_id = get_indicator_id(cursor, indicator_code)
    
    if not indicator_id:
        print(f"   ✗ Indicator {indicator_code} not found")
        return
    
    year_columns, data_rows = parse_eurostat_tsv(filepath)
    print(f"   Found {len(year_columns)} years: {min(year_columns)}-{max(year_columns)}")
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    unmapped_count = 0
    
    for row in data_rows:
        # Parse dimensions from first column (freq,indic_nrg,geo)
        dimensions = row[0].split(',')
        if len(dimensions) < 3:
            continue
        
        geo_code = dimensions[-1].strip()  # Last element is country
        
        # Map to ISO3
        iso3 = EUROSTAT_TO_ISO3.get(geo_code)
        if not iso3:
            unmapped_count += 1
            continue
        
        country_id = get_country_id(cursor, iso3)
        if not country_id:
            continue
        
        # Process each year column
        for year_idx, year in enumerate(year_columns):
            value_str = row[year_idx + 1].strip()  # +1 because first column is dimensions
            
            if value_str == ':' or value_str == '':
                skip_count += 1
                continue
            
            try:
                # Remove flags and convert to float
                value = float(value_str.split()[0].replace(',', '.'))
                
                result = insert_or_average(cursor, country_id, indicator_id, year, value)
                if result == 'new':
                    new_count += 1
                else:
                    avg_count += 1
                    
            except (ValueError, IndexError):
                skip_count += 1
    
    update_source(cursor, indicator_code)
    
    print(f"   ✓ {new_count + avg_count:,} values imported ({new_count:,} new + {avg_count:,} averaged)")
    print(f"   Skipped: {skip_count:,} missing values, {unmapped_count:,} unmapped countries")

def import_energy_consumption(cursor, filepath):
    """Import nrg_cb_e: Energy consumption → EG.USE.PCAP.KG.OE"""
    print("\n📊 Processing Energy Consumption (nrg_cb_e)...")
    
    indicator_code = 'EG.USE.PCAP.KG.OE'
    indicator_id = get_indicator_id(cursor, indicator_code)
    
    if not indicator_id:
        print(f"   ✗ Indicator {indicator_code} not found")
        return
    
    year_columns, data_rows = parse_eurostat_tsv(filepath)
    print(f"   Found {len(year_columns)} years: {min(year_columns)}-{max(year_columns)}")
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    unmapped_count = 0
    
    for row in data_rows:
        # Parse dimensions: freq,unit,siec,geo
        dimensions = row[0].split(',')
        if len(dimensions) < 4:
            continue
        
        unit = dimensions[1].strip()
        siec = dimensions[2].strip()  # Energy product
        geo_code = dimensions[-1].strip()
        
        # Filter: only KGOE (kilograms of oil equivalent) per capita
        if unit != 'KGOE_HAB':
            continue
        
        # Only total energy (TOE)
        if siec != 'TOTAL':
            continue
        
        iso3 = EUROSTAT_TO_ISO3.get(geo_code)
        if not iso3:
            unmapped_count += 1
            continue
        
        country_id = get_country_id(cursor, iso3)
        if not country_id:
            continue
        
        for year_idx, year in enumerate(year_columns):
            value_str = row[year_idx + 1].strip()
            
            if value_str == ':' or value_str == '':
                skip_count += 1
                continue
            
            try:
                value = float(value_str.split()[0].replace(',', '.'))
                
                result = insert_or_average(cursor, country_id, indicator_id, year, value)
                if result == 'new':
                    new_count += 1
                else:
                    avg_count += 1
                    
            except (ValueError, IndexError):
                skip_count += 1
    
    update_source(cursor, indicator_code)
    
    print(f"   ✓ {new_count + avg_count:,} values imported ({new_count:,} new + {avg_count:,} averaged)")
    print(f"   Skipped: {skip_count:,} missing values, {unmapped_count:,} unmapped countries")

def import_fossil_fuel_consumption(cursor, filepath):
    """Import nrg_bal_c: Extract fossil fuel consumption % → EG.USE.COMM.FO.ZS"""
    print("\n📊 Processing Fossil Fuel Consumption (nrg_bal_c)...")
    
    indicator_code = 'EG.USE.COMM.FO.ZS'
    indicator_id = get_indicator_id(cursor, indicator_code)
    
    if not indicator_id:
        print(f"   ✗ Indicator {indicator_code} not found")
        return
    
    year_columns, data_rows = parse_eurostat_tsv(filepath)
    print(f"   Found {len(year_columns)} years")
    print(f"   Total rows: {len(data_rows):,}")
    
    # This is a huge file - we need to extract specific energy products
    # SIEC codes: C0000X0350-0370 = Solid fossil fuels, O4000XBIO = Oil products, G3000 = Natural gas
    
    new_count = 0
    avg_count = 0
    skip_count = 0
    unmapped_count = 0
    processed_lines = 0
    
    for row in data_rows:
        # Dimensions: freq,unit,nrg_bal,siec,geo
        dimensions = row[0].split(',')
        if len(dimensions) < 5:
            continue
        
        unit = dimensions[1].strip()
        nrg_bal = dimensions[2].strip()  # Balance item
        siec = dimensions[3].strip()  # Energy product
        geo_code = dimensions[-1].strip()
        
        # Filter: only final consumption (FC) and TJ units
        if nrg_bal != 'FC':
            continue
        
        if unit != 'TJ':
            continue
        
        # Only fossil fuels: coal, oil, gas
        if siec not in ['C0000X0350-0370', 'O4000XBIO', 'G3000']:
            continue
        
        processed_lines += 1
        
        iso3 = EUROSTAT_TO_ISO3.get(geo_code)
        if not iso3:
            unmapped_count += 1
            continue
        
        country_id = get_country_id(cursor, iso3)
        if not country_id:
            continue
        
        # Note: This gives us absolute TJ values, not percentages
        # We'd need to calculate % from total energy - for now skip detailed calculation
        # Just count as processed for monitoring
        skip_count += len(year_columns)
    
    print(f"   ℹ️ Processed {processed_lines:,} fossil fuel lines")
    print(f"   ⚠️ Skipping detailed import (requires % calculation from total energy)")
    print(f"   Unmapped: {unmapped_count:,} countries")

def main():
    print("="*80)
    print("EUROSTAT ENERGY DATA IMPORT - CATEGORY 7")
    print("="*80)
    
    base_dir = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/Eurostat'
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Import energy dependency (EG.IMP.CONS.ZS)
        dep_file = os.path.join(base_dir, 'eurostat_energy_dependence.tsv')
        if os.path.exists(dep_file):
            import_energy_dependence(cursor, dep_file)
        
        # Import energy consumption per capita (EG.USE.PCAP.KG.OE)
        cons_file = os.path.join(base_dir, 'eurostat_final_energy.tsv')
        if os.path.exists(cons_file):
            import_energy_consumption(cursor, cons_file)
        
        # Import fossil fuel data (EG.USE.COMM.FO.ZS) - complex calculation
        fossil_file = os.path.join(base_dir, 'eurostat_energy_balance.tsv')
        if os.path.exists(fossil_file):
            import_fossil_fuel_consumption(cursor, fossil_file)
        
        conn.commit()
        print("\n" + "="*80)
        print("✅ Import completed successfully")
        print("="*80)
        
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
