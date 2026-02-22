#!/usr/bin/env python3
"""
Import World Bank data for IP.PAT.RESD and ER.H2O.FWST.ZS
Averages with existing WIPO/FAO data
"""
import psycopg2
import csv
import sys

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'postgres'
}

def import_wb_data(filepath, indicator_code):
    """Import World Bank CSV data"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get indicator ID
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    if not result:
        print(f"❌ Indicateur {indicator_code} introuvable")
        cursor.close()
        conn.close()
        return
    
    indicator_id = result[0]
    
    # Get country mapping
    cursor.execute("SELECT iso3, id FROM country WHERE iso3 IS NOT NULL")
    country_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    inserted = 0
    updated = 0
    ignored = 0
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            iso3 = row['country_iso3'].strip('"')
            year = int(row['year'])
            value = float(row['value'])
            
            # Filter years and get country_id
            if year < 1950 or year > 2035:
                ignored += 1
                continue
            
            country_id = country_map.get(iso3)
            if not country_id:
                ignored += 1
                continue
            
            # Check if value exists
            cursor.execute("""
                SELECT value FROM indicator_value
                WHERE indicator_id = %s AND country_id = %s AND year = %s
            """, (indicator_id, country_id, year))
            
            existing = cursor.fetchone()
            
            if existing:
                # Average with existing (WIPO/FAO + WB) / 2
                old_value = float(existing[0])
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
    
    # Update source
    cursor.execute("""
        UPDATE indicator
        SET source = CASE 
            WHEN source LIKE '%World Bank%' THEN source
            WHEN source IS NULL THEN 'World Bank'
            ELSE source || ' + World Bank'
        END
        WHERE id = %s
    """, (indicator_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n📊 {indicator_code}:")
    print(f"  ✓ {inserted} nouvelles valeurs")
    print(f"  ✓ {updated} valeurs moyennées (WB + WIPO/FAO)")
    print(f"  ⚠ {ignored} ignorées")
    total = inserted + updated
    success = (total / (total + ignored) * 100) if (total + ignored) > 0 else 0
    print(f"  📈 Taux: {success:.1f}%")


def main():
    print("🚀 IMPORT WORLD BANK DATA")
    print("=" * 50)
    
    files = [
        ('/tmp/wb_IP_PAT_RESD_clean.csv', 'IP.PAT.RESD'),
        ('/tmp/wb_ER_H2O_FWST_ZS_clean.csv', 'ER.H2O.FWST.ZS')
    ]
    
    for filepath, code in files:
        try:
            import_wb_data(filepath, code)
        except Exception as e:
            print(f"❌ Erreur {code}: {e}")
    
    print("\n✅ Import World Bank terminé")


if __name__ == '__main__':
    main()
