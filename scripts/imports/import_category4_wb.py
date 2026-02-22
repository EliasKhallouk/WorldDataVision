#!/usr/bin/env python3
import psycopg2
import csv
import glob

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'postgres'
}

def import_wb_indicator(filepath, indicator_code):
    """Import WB data and average with existing values"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Get indicator ID
        cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
        result = cursor.fetchone()
        if not result:
            print(f"  ❌ Indicator {indicator_code} not found in DB")
            return 0, 0
        indicator_id = result[0]
        
        # Get all countries mapping
        cursor.execute("SELECT iso3, id FROM country")
        country_map = {row[0]: row[1] for row in cursor.fetchall()}
        
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
        print(f"  ✅ {inserted} inserted, {updated} updated, {skipped} skipped")
        
        return inserted, updated
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("=== Import World Bank - Catégorie 4 (Gouvernance) ===\n")
    
    # Map des fichiers aux codes d'indicateurs
    files_map = {
        '/tmp/wb_GC_TAX_TOTL_GD_ZS.csv': 'GC.TAX.TOTL.GD.ZS',
        '/tmp/wb_CC_EST.csv': 'CC.EST',
        '/tmp/wb_GE_EST.csv': 'GE.EST',
        '/tmp/wb_PV_EST.csv': 'PV.EST',
        '/tmp/wb_RL_EST.csv': 'RL.EST',
        '/tmp/wb_RQ_EST.csv': 'RQ.EST',
        '/tmp/wb_VA_EST.csv': 'VA.EST'
    }
    
    total_inserted = 0
    total_updated = 0
    
    for i, (filepath, code) in enumerate(files_map.items(), 1):
        print(f"{i}/7. {code}:")
        ins, upd = import_wb_indicator(filepath, code)
        total_inserted += ins
        total_updated += upd
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_inserted} nouvelles valeurs, {total_updated} valeurs moyennées")
    print(f"{'='*60}")
