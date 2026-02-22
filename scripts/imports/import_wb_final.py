#!/usr/bin/env python3
import psycopg2
import csv

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'postgres'
}

def import_wb_data(filepath, indicator_code):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Get indicator ID
        cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
        result = cursor.fetchone()
        if not result:
            print(f"❌ Indicator {indicator_code} not found")
            return 0, 0
        indicator_id = result[0]
        print(f"Indicator ID: {indicator_id}")
        
        # Get all countries mapping
        cursor.execute("SELECT iso3, id FROM country")
        country_map = {row[0]: row[1] for row in cursor.fetchall()}
        print(f"Countries loaded: {len(country_map)}")
        
        inserted = 0
        updated = 0
        skipped = 0
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                iso3 = row['country_iso3']
                year = int(row['year'])
                value = float(row['value'])
                
                if iso3 not in country_map:
                    skipped += 1
                    continue
                
                country_id = country_map[iso3]
                
                # Check if value already exists
                cursor.execute("""
                    SELECT value FROM indicator_value 
                    WHERE indicator_id = %s AND country_id = %s AND year = %s
                """, (indicator_id, country_id, year))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Average with existing value
                    old_value = existing[0]
                    new_value = (old_value + value) / 2
                    cursor.execute("""
                        UPDATE indicator_value 
                        SET value = %s 
                        WHERE indicator_id = %s AND country_id = %s AND year = %s
                    """, (new_value, indicator_id, country_id, year))
                    updated += 1
                else:
                    # Insert new value
                    cursor.execute("""
                        INSERT INTO indicator_value (indicator_id, country_id, year, value)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (country_id, indicator_id, year) DO UPDATE
                        SET value = EXCLUDED.value
                    """, (indicator_id, country_id, year, value))
                    inserted += 1
        
        conn.commit()
        print(f"✓ {indicator_code}: {inserted} inserted, {updated} updated, {skipped} skipped")
        
        # Update source
        cursor.execute("SELECT source FROM indicator WHERE id = %s", (indicator_id,))
        current_source = cursor.fetchone()[0] or ""
        if "World Bank" not in current_source:
            new_source = current_source + " + World Bank" if current_source else "World Bank"
            cursor.execute("UPDATE indicator SET source = %s WHERE id = %s", (new_source, indicator_id))
            conn.commit()
            print(f"Source updated: {new_source}")
        
        return inserted, updated
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=== Importing World Bank data ===\n")
    
    print("1. IP.PAT.RESD (Patent applications):")
    i1, u1 = import_wb_data('/tmp/wb_IP_PAT_RESD_clean.csv', 'IP.PAT.RESD')
    
    print("\n2. ER.H2O.FWST.ZS (Water stress):")
    i2, u2 = import_wb_data('/tmp/wb_ER_H2O_FWST_ZS_clean.csv', 'ER.H2O.FWST.ZS')
    
    print(f"\n=== Total: {i1+i2} inserted, {u1+u2} updated ===")
