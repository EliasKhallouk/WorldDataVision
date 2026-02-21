#!/usr/bin/env python3
"""
Analyse les pays IMF qui ne sont pas trouvés dans la base
"""

import csv
import psycopg2
import os
import unicodedata
from collections import Counter

DB_CONFIG = {
    'user': 'elias',
    'host': 'localhost',
    'database': 'worlddatavision',
    'password': '',
    'port': 5432
}

def normalize_name(name: str) -> str:
    """Normalise un nom de pays."""
    name = name.lower().strip()
    name = unicodedata.normalize('NFD', name)
    name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
    return name

# Lire les pays IMF
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '../../Data/IRC/imf-dm-export-20260221.csv')

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

imf_countries = []
for row in rows[2:]:  # Skip header and empty line
    if row and row[0].strip():
        imf_countries.append(row[0].strip())

print(f"📊 {len(imf_countries)} pays dans le fichier IMF\n")

# Récupérer les pays de la DB
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT id, iso3, name FROM country ORDER BY name")
db_countries = cursor.fetchall()
print(f"📊 {len(db_countries)} pays dans la base de données\n")

# Créer un mapping normalisé
db_mapping = {}
for country_id, iso3, name in db_countries:
    normalized = normalize_name(name)
    db_mapping[normalized] = (iso3, name)

# Analyser les pays non trouvés
not_found = []
found = []

for imf_name in imf_countries:
    normalized_imf = normalize_name(imf_name.replace(',', ''))
    
    # Chercher dans la DB
    matched = False
    
    # Exact match
    if normalized_imf in db_mapping:
        matched = True
        found.append(imf_name)
    else:
        # Partial match
        for db_norm, (iso3, db_name) in db_mapping.items():
            if normalized_imf in db_norm or db_norm in normalized_imf:
                matched = True
                found.append(imf_name)
                break
    
    if not matched:
        not_found.append(imf_name)

print("=" * 80)
print(f"✅ PAYS TROUVÉS: {len(found)}")
print(f"❌ PAYS NON TROUVÉS: {len(not_found)}")
print("=" * 80)

if not_found:
    print("\n🔍 Liste des pays IMF non trouvés:\n")
    for i, country in enumerate(not_found, 1):
        print(f"{i:3d}. {country}")
    
    print("\n" + "=" * 80)
    print("💡 SUGGESTIONS DE MAPPING MANUEL À AJOUTER:")
    print("=" * 80)
    print("\nAjouter dans COUNTRY_NAME_MAPPING du script:\n")
    
    for country in not_found:
        # Chercher les suggestions dans la DB
        normalized = normalize_name(country.replace(',', '').replace('the', '').strip())
        
        suggestions = []
        for db_norm, (iso3, db_name) in db_mapping.items():
            # Similarité partielle
            words_imf = set(normalized.split())
            words_db = set(db_norm.split())
            
            common = words_imf.intersection(words_db)
            if len(common) > 0:
                suggestions.append((iso3, db_name))
        
        if suggestions:
            print(f'    "{country}": "{suggestions[0][0]}",  # {suggestions[0][1]}')
        else:
            print(f'    "{country}": "???",  # À compléter manuellement')

cursor.close()
conn.close()
