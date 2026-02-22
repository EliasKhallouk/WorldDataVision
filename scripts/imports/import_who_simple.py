#!/usr/bin/env python3
"""Import OMS - Version simplifiée et robuste"""
import psycopg2
import requests
import time

conn = psycopg2.connect(dbname="worlddatavision", user="elias", password="MaBaseDeDonnee", host="localhost")
cursor = conn.cursor()

WHO_BASE = "https://ghoapi.azureedge.net/api"

mappings = {
    'SP.DYN.IMRT.IN': 'MDG_0000000001',
    'SP.DYN.LE00.IN': 'WHOSIS_000001',
}

# Pays
cursor.execute("SELECT id, iso3 FROM country WHERE iso3 IS NOT NULL AND iso3 != ''")
countries = {iso3: cid for cid, iso3 in cursor.fetchall()}

print(f"Pays: {len(countries)}\n")

for irc, who_code in mappings.items():
    print(f"\n{'='*60}\n{irc} ← {who_code}\n{'='*60}")
    
    cursor.execute("SELECT COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)", (irc,))
    before = cursor.fetchone()[0]
    print(f"Avant: {before} pays")
    
    # Télécharger
    print(f"Téléchargement OMS...")
    resp = requests.get(f"{WHO_BASE}/{who_code}", timeout=90)
    
    if resp.status_code != 200:
        print(f"✗ HTTP {resp.status_code}")
        continue
    
    values = resp.json().get('value', [])
    print(f"✓ {len(values)} observations")
    
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (irc,))
    ind_id = cursor.fetchone()[0]
    
    # Traiter
    data = {}
    for v in values:
        iso3, year, val = v.get('SpatialDim'), v.get('TimeDim'), v.get('NumericValue')
        if iso3 in countries and year and val is not None:
            try:
                key = (countries[iso3], int(year))
                if key not in data:
                    data[key] = []
                data[key].append(float(val))
            except:
                pass
    
    print(f"✓ {len(data)} paires pays-année")
    
    new, avg = 0, 0
    
    for (country_id, year), vals in data.items():
        value = sum(vals) / len(vals)
        
        cursor.execute("SELECT id, value FROM indicator_value WHERE indicator_id = %s AND country_id = %s AND year = %s", 
                      (ind_id, country_id, year))
        ex = cursor.fetchone()
        
        if ex:
            cursor.execute("UPDATE indicator_value SET value = %s WHERE id = %s", 
                          ((ex[1] + value) / 2, ex[0]))
            avg += 1
        else:
            cursor.execute("INSERT INTO indicator_value (indicator_id, country_id, year, value) VALUES (%s, %s, %s, %s)",
                          (ind_id, country_id, year, value))
            new += 1
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = %s", (ind_id,))
    after = cursor.fetchone()[0]
    
    # Mise à jour source
    cursor.execute("SELECT source FROM indicator WHERE code = %s", (irc,))
    src = cursor.fetchone()[0] or ""
    if 'OMS' not in src and 'WHO' not in src:
        new_src = (src + " + OMS (WHO GHO)") if src else "OMS (WHO GHO)"
        cursor.execute("UPDATE indicator SET source = %s WHERE code = %s", (new_src, irc))
        conn.commit()
    
    print(f"\n✅ Nouvelles: {new} | Moyennées: {avg}")
    print(f"📈 {before} → {after} (+{after-before})")
    
    time.sleep(1)

cursor.close()
conn.close()
print("\n✅ TERMINÉ")
