#!/usr/bin/env python3
import csv
import os

csv_path = '../../Data/IRC/imf-dm-export-20260221.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

print(f"Total lignes: {len(rows)}")
print(f"Argentina ligne 9: {rows[8][0]}")
print(f"Argentina valeurs 1950-1955: {rows[8][1:7]}")

# Compter valeurs
count = 0
for row in rows[2:]:
    if row and row[0].strip():
        for val in row[1:]:
            if val.strip() and val.strip() != 'no data':
                count += 1

print(f"Total valeurs non vides: {count}")
