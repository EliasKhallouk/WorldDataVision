#!/usr/bin/env python3
"""Test rapide du parsing CSV"""

import csv
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '../../Data/IRC/imf-dm-export-20260221.csv')

print(f"📂 Lecture de: {csv_path}\n")

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

print(f"✅ {len(rows)} lignes lues\n")

# Afficher les 3 premières lignes
print("=" * 80)
print("Ligne 1 (header):")
print(f"  Pays: {rows[0][0]}")
print(f"  Premières années: {rows[0][1:6]}")
print(f"  Total colonnes: {len(rows[0])}")

print("\nLigne 2 (vide):")
print(f"  Contenu: {rows[1]}")

print("\nLigne 3 (Afghanistan):")
print(f"  Pays: {rows[2][0]}")
print(f"  Premières valeurs: {rows[2][1:6]}")
print(f"  Total valeurs: {len(rows[2]) - 1}")

print("\nLigne 4 (Albania):")
print(f"  Pays: {rows[3][0]}")
print(f"  Premières valeurs: {rows[3][1:6]}")

print("\nLigne 9 (Argentina - PROBLÉMATIQUE):")
print(f"  Pays: {rows[8][0]}")
print(f"  Premières valeurs: {rows[8][1:10]}")
print("=" * 80)

# Compter les valeurs non vides
total_values = 0
for row in rows[2:]:  # Ignorer header et ligne vide
    if row and row[0].strip():
        for val in row[1:]:
            if val.strip() and val.strip() != 'no data':
                total_values += 1

print(f"\n📊 Statistiques:")
print(f"   Pays: {len(rows) - 2}")
print(f"   Valeurs non vides estimées: {total_values}")
