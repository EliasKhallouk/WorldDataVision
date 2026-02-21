#!/usr/bin/env python3
"""Affiche TOUS les pays non trouvés avec leurs suggestions"""

import csv
import psycopg2
import os

csv_path = '../../Data/IRC/imf-dm-export-20260221.csv'

# Lire tous les pays IMF
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

imf_countries = [row[0].strip() for row in rows[2:] if row and row[0].strip()]

# Récupérer tous les pays de la DB
conn = psycopg2.connect(
    user='elias',
    host='localhost',
    database='worlddatavision',
    password='',
    port=5432
)
cursor = conn.cursor()
cursor.execute("SELECT iso3, name FROM country ORDER BY name")
db_countries = {row[1]: row[0] for row in cursor.fetchall()}
cursor.close()
conn.close()

print(f"Total pays IMF: {len(imf_countries)}")
print(f"Total pays DB: {len(db_countries)}\n")
print("=" * 80)
print("PAYS IMF (liste complète):")
print("=" * 80)

for i, country in enumerate(imf_countries, 1):
    print(f"{i:3d}. {country}")
