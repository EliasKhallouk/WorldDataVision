#!/usr/bin/env python3
"""Diagnostic : Quels pays UNESCO ne sont pas dans la base de données."""

import csv
import psycopg2

DB_CONFIG = {
    'user': 'elias',
    'host': 'localhost',
    'database': 'worlddatavision',
    'password': 'MaBaseDeDonnee',
    'port': 5432
}

CSV_FILE = '/home/elias/PROJECT/WorldDataVision/Data/IRC/literacy-rates-among-adults.csv'

# Charger les pays de la DB
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT iso3, name FROM country ORDER BY iso3")
db_countries = {row[0]: row[1] for row in cur.fetchall()}
cur.close()
conn.close()

print(f"🌍 Pays dans la base de données: {len(db_countries)}")

# Lire le CSV
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    csv_data = list(reader)

# Analyser les correspondances
csv_countries = {}
for row in csv_data:
    code = row['Code'].strip()
    entity = row['Entity'].strip()
    if code not in csv_countries:
        csv_countries[code] = entity

print(f"📄 Pays dans le CSV UNESCO: {len(csv_countries)}")

# Identifier les manquants
missing_in_db = []
found_in_db = []

for iso3, entity in sorted(csv_countries.items()):
    if iso3 not in db_countries:
        # Compter combien de valeurs sont perdues
        count = sum(1 for row in csv_data if row['Code'].strip() == iso3)
        missing_in_db.append((iso3, entity, count))
    else:
        found_in_db.append((iso3, entity))

print(f"\n✅ Pays trouvés dans la DB: {len(found_in_db)}")
print(f"❌ Pays ABSENTS de la DB: {len(missing_in_db)}\n")

if missing_in_db:
    print("="*80)
    print("PAYS UNESCO ABSENTS DE LA BASE DE DONNÉES:")
    print("="*80)
    
    total_lost = 0
    for iso3, entity, count in missing_in_db:
        print(f"  {iso3:3s} | {entity:40s} | {count:3d} valeurs perdues")
        total_lost += count
    
    print("="*80)
    print(f"TOTAL VALEURS PERDUES: {total_lost}")
    print("="*80)

print("\n💡 Solution: Ajouter ces pays dans la table 'country' ou mapper vers pays existants")
