#!/usr/bin/env python3
import psycopg2
import csv

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
            print(f"  ❌ Indicator {indicator_code} not found")
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
        print(f"  ✅ {inserted} nouvelles + {updated} moyennées ({skipped} ignorées)")
        
        return inserted, updated
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Erreur: {e}")
        return 0, 0
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("="*70)
    print("Import WB - Catégories 1 (Économie) et 6 (Innovation)")
    print("="*70)
    
    files_map = {
        '/tmp/wb_DT_DOD_DECT_GN_ZS.csv': 'DT.DOD.DECT.GN.ZS',
        '/tmp/wb_DT_TDS_DECT_EX_ZS.csv': 'DT.TDS.DECT.EX.ZS',
        '/tmp/wb_MS_MIL_XPND_GD_ZS.csv': 'MS.MIL.XPND.GD.ZS',
        '/tmp/wb_FI_RES_TOTL_MO.csv': 'FI.RES.TOTL.MO',
        '/tmp/wb_SP_POP_SCIE_RD_P6.csv': 'SP.POP.SCIE.RD.P6',
        '/tmp/wb_GB_XPD_RSDV_GD_ZS.csv': 'GB.XPD.RSDV.GD.ZS',
    }
    
    total_inserted = 0
    total_updated = 0
    
    for i, (filepath, code) in enumerate(files_map.items(), 1):
        print(f"\n{i}/6. {code}:")
        ins, upd = import_wb_indicator(filepath, code)
        total_inserted += ins
        total_updated += upd
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {total_inserted} nouvelles + {total_updated} moyennées")
    print(f"       = {total_inserted + total_updated} valeurs traitées")
    print(f"{'='*70}")
