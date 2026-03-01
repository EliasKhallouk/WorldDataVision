#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import IfDB (African Development Bank) literacy data
Source: SE.ADT.LITR.ZS - Adult literacy rate (% of people ages 15+)
"""

import csv
import psycopg2
from psycopg2.extras import execute_values

# Connexion PostgreSQL
conn = psycopg2.connect(
    dbname="worlddatavision",
    user="elias",
    password="MaBaseDeDonnee",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

print("=" * 90)
print("IMPORT IfDB - SE.ADT.LITR.ZS (Adult literacy rate)")
print("=" * 90)

# Mapping pays IfDB → iso3 (basé sur Country.csv de IfDB)
# On garde seulement les pays réels, pas les agrégats régionaux
COUNTRY_MAPPING = {
    'AGO': 'AGO',  # Angola
    'BDI': 'BDI',  # Burundi
    'BEN': 'BEN',  # Benin
    'BFA': 'BFA',  # Burkina Faso
    'BWA': 'BWA',  # Botswana
    'CAF': 'CAF',  # Central African Republic
    'CIV': 'CIV',  # Côte d'Ivoire
    'CMR': 'CMR',  # Cameroon
    'COD': 'COD',  # Congo, Dem. Rep.
    'COG': 'COG',  # Congo, Rep.
    'COM': 'COM',  # Comoros
    'CPV': 'CPV',  # Cabo Verde
    'DJI': 'DJI',  # Djibouti
    'DZA': 'DZA',  # Algeria
    'EGY': 'EGY',  # Egypt
    'ERI': 'ERI',  # Eritrea
    'ETH': 'ETH',  # Ethiopia
    'GAB': 'GAB',  # Gabon
    'GHA': 'GHA',  # Ghana
    'GIN': 'GIN',  # Guinea
    'GMB': 'GMB',  # Gambia
    'GNB': 'GNB',  # Guinea-Bissau
    'GNQ': 'GNQ',  # Equatorial Guinea
    'KEN': 'KEN',  # Kenya
    'LBR': 'LBR',  # Liberia
    'LBY': 'LBY',  # Libya
    'LSO': 'LSO',  # Lesotho
    'MAR': 'MAR',  # Morocco
    'MDG': 'MDG',  # Madagascar
    'MLI': 'MLI',  # Mali
    'MOZ': 'MOZ',  # Mozambique
    'MRT': 'MRT',  # Mauritania
    'MUS': 'MUS',  # Mauritius
    'MWI': 'MWI',  # Malawi
    'NAM': 'NAM',  # Namibia
    'NER': 'NER',  # Niger
    'NGA': 'NGA',  # Nigeria
    'RWA': 'RWA',  # Rwanda
    'SDN': 'SDN',  # Sudan
    'SEN': 'SEN',  # Senegal
    'SLE': 'SLE',  # Sierra Leone
    'SOM': 'SOM',  # Somalia
    'SSD': 'SSD',  # South Sudan
    'STP': 'STP',  # São Tomé and Príncipe
    'SWZ': 'SWZ',  # Eswatini
    'SYC': 'SYC',  # Seychelles
    'TCD': 'TCD',  # Chad
    'TGO': 'TGO',  # Togo
    'TUN': 'TUN',  # Tunisia
    'TZA': 'TZA',  # Tanzania
    'UGA': 'UGA',  # Uganda
    'ZAF': 'ZAF',  # South Africa
    'ZMB': 'ZMB',  # Zambia
    'ZWE': 'ZWE',  # Zimbabwe
}

# 1. Lire les données IfDB
print("\n[1] LECTURE DES DONNÉES IfDB...")
print("-" * 90)

data_file = 'Data/Manuel/IfDB/Data.csv'
literacy_data = []

with open(data_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Indicator'] == 'SE.ADT.LITR.ZS':
            country_code = row['Country']
            
            # Ignorer les agrégats régionaux
            if country_code not in COUNTRY_MAPPING:
                continue
            
            try:
                year = int(row['Date'][:4])
                value = float(row['Value'])
                
                # Validation: pourcentages (0-100%)
                if value < 0 or value > 100:
                    print(f"  ⚠️  Valeur aberrante ignorée: {country_code} {year} = {value}%")
                    continue
                
                literacy_data.append({
                    'country_code': COUNTRY_MAPPING[country_code],
                    'year': year,
                    'value': value
                })
            except (ValueError, KeyError):
                continue

print(f"  ✅ {len(literacy_data)} valeurs lues depuis IfDB")

# 2. Vérifier l'indicateur SE.ADT.LITR.ZS existe
print("\n[2] VÉRIFICATION INDICATEUR...")
print("-" * 90)

cur.execute("""
    SELECT id FROM indicator WHERE code = 'SE.ADT.LITR.ZS'
""")
result = cur.fetchone()

if not result:
    print("  ❌ Indicateur SE.ADT.LITR.ZS introuvable dans la DB")
    cur.close()
    conn.close()
    exit(1)

indicator_id = result[0]
print(f"  ✅ Indicateur trouvé: id={indicator_id}")

# 3. Mapper country_code → country_id
print("\n[3] MAPPING PAYS...")
print("-" * 90)

cur.execute("""
    SELECT iso3, id FROM country
""")
country_map = {row[0]: row[1] for row in cur.fetchall()}

mapped_data = []
countries_not_found = set()

for item in literacy_data:
    iso3 = item['country_code']
    if iso3 in country_map:
        mapped_data.append({
            'country_id': country_map[iso3],
            'year': item['year'],
            'value': item['value']
        })
    else:
        countries_not_found.add(iso3)

print(f"  ✅ {len(mapped_data)} valeurs mappées")
if countries_not_found:
    print(f"  ⚠️  {len(countries_not_found)} pays non trouvés: {', '.join(sorted(countries_not_found))}")

# 4. Import avec averaging
print("\n[4] IMPORT AVEC AVERAGING...")
print("-" * 90)

new_count = 0
updated_count = 0

for item in mapped_data:
    # Vérifier si la donnée existe déjà
    cur.execute("""
        SELECT id, value FROM indicator_value
        WHERE country_id = %s
          AND indicator_id = %s
          AND year = %s
    """, (item['country_id'], indicator_id, item['year']))
    
    existing = cur.fetchone()
    
    if existing:
        # Faire la moyenne
        old_value = existing[1]
        avg_value = (old_value + item['value']) / 2
        
        cur.execute("""
            UPDATE indicator_value
            SET value = %s
            WHERE id = %s
        """, (avg_value, existing[0]))
        
        updated_count += 1
    else:
        # Nouvelle insertion
        cur.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (item['country_id'], indicator_id, item['year'], item['value']))
        
        new_count += 1

conn.commit()

print(f"  ✅ {new_count} nouvelles valeurs insérées")
print(f"  ✅ {updated_count} valeurs moyennées avec existantes")

# 5. Validation finale
print("\n[5] VALIDATION FINALE...")
print("-" * 90)

cur.execute("""
    SELECT 
        COUNT(*) as total,
        MIN(value) as min_val,
        MAX(value) as max_val,
        AVG(value) as avg_val,
        STDDEV(value) as stddev_val,
        MIN(year) as first_year,
        MAX(year) as last_year,
        COUNT(DISTINCT country_id) as countries
    FROM indicator_value
    WHERE indicator_id = %s
""", (indicator_id,))

stats = cur.fetchone()

print(f"  Total valeurs: {stats[0]}")
print(f"  Période: {stats[5]:.0f} - {stats[6]:.0f}")
print(f"  Pays: {stats[7]}")
print(f"  Min: {stats[1]:.2f}%")
print(f"  Max: {stats[2]:.2f}%")
print(f"  Moyenne: {stats[3]:.2f}%")
print(f"  Écart-type: {stats[4]:.2f}%")

# Vérifier les valeurs aberrantes
cur.execute("""
    SELECT COUNT(*) FROM indicator_value
    WHERE indicator_id = %s
      AND (value < 0 OR value > 100)
""", (indicator_id,))

aberrant_count = cur.fetchone()[0]

if aberrant_count > 0:
    print(f"  ❌ {aberrant_count} valeurs aberrantes détectées (hors 0-100%)")
else:
    print(f"  ✅ Toutes les valeurs sont dans l'intervalle 0-100%")

print("\n" + "=" * 90)
print("✅ IMPORT IFDB TERMINÉ AVEC SUCCÈS")
print("=" * 90 + "\n")

cur.close()
conn.close()
