#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction : recalculer les moyennes pour les données d'alphabétisation
qui ont été écrasées au lieu d'être moyennées
"""

import psycopg2
import csv

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'elias',
    'password': 'MaBaseDeDonnee',
    'host': 'localhost',
    'port': '5432'
}

COUNTRY_MAPPING = {
    'Afghanistan': 'AFG',
    'Armenia': 'ARM',
    'Azerbaijan': 'AZE',
    'Bangladesh': 'BGD',
    'Bhutan': 'BTN',
    'Brunei Darussalam': 'BRN',
    'Cambodia': 'KHM',
    'China, People\'s Republic of': 'CHN',
    'Georgia': 'GEO',
    'India': 'IND',
    'Indonesia': 'IDN',
    'Kazakhstan': 'KAZ',
    'Kiribati': 'KIR',
    'Korea, Republic of': 'KOR',
    'Kyrgyz Republic': 'KGZ',
    'Lao People\'s Democratic Republic': 'LAO',
    'Malaysia': 'MYS',
    'Maldives': 'MDV',
    'Marshall Islands': 'MHL',
    'Mongolia': 'MNG',
    'Myanmar': 'MMR',
    'Nauru': 'NRU',
    'Nepal': 'NPL',
    'Pakistan': 'PAK',
    'Palau': 'PLW',
    'Papua New Guinea': 'PNG',
    'Philippines': 'PHL',
    'Samoa': 'WSM',
    'Singapore': 'SGP',
    'Sri Lanka': 'LKA',
    'Tajikistan': 'TJK',
    'Thailand': 'THA',
    'Timor-Leste': 'TLS',
    'Tonga': 'TON',
    'Türkiye': 'TUR',
    'Uzbekistan': 'UZB',
    'Vanuatu': 'VUT',
    'Viet Nam': 'VNM',
}

print("🔧 Correction des moyennes - Taux d'alphabétisation")
print("=" * 70)
print("\n⚠️  ATTENTION : Ce script va RESTAURER les données écrasées en utilisant")
print("    les valeurs du CSV d'origine et faire la moyenne avec les valeurs actuelles.\n")

response = input("Voulez-vous continuer ? (oui/non) : ")
if response.lower() not in ['oui', 'o', 'yes', 'y']:
    print("❌ Annulé")
    exit(0)

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Récupérer l'ID de l'indicateur
cursor.execute("SELECT id FROM indicator WHERE code = 'SE.ADT.LITR.ZS'")
indicator_id = cursor.fetchone()[0]

print(f"\n📊 Traitement de l'indicateur SE.ADT.LITR.ZS (ID: {indicator_id})")

# D'abord, sauvegarder les valeurs actuelles dans une table temporaire
print("\n1️⃣  Sauvegarde des valeurs actuelles...")
cursor.execute("""
    CREATE TEMP TABLE old_literacy_values AS
    SELECT country_id, year, value, source
    FROM indicator_value
    WHERE indicator_id = %s
""", (indicator_id,))
conn.commit()

saved_count = cursor.rowcount
print(f"   ✓ {saved_count} valeurs sauvegardées")

# Lire le CSV pour récupérer les valeurs originales
print("\n2️⃣  Lecture du CSV original...")
csv_file = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/KIDB-alphabetisation_adulte.csv'
year_columns = [str(year) for year in range(2000, 2026)]

corrected_count = 0
skipped_count = 0

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        country_name = row['Economy'].strip()
        unit = row['Unit of Measure'].strip()
        
        if not unit or '-' in country_name[:4]:
            continue
        
        iso3 = COUNTRY_MAPPING.get(country_name)
        if not iso3:
            continue
        
        # Récupérer l'ID du pays
        cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3,))
        result = cursor.fetchone()
        if not result:
            continue
        
        country_id = result[0]
        
        # Pour chaque année avec une valeur dans le CSV
        for year in year_columns:
            value_str = row.get(year, '').strip()
            if not value_str or value_str == '...':
                continue
            
            try:
                csv_value = float(value_str)
                source = row.get('Source', 'United Nations Educational, Scientific and Cultural Organization').strip()
                
                # Récupérer la valeur actuelle en base
                cursor.execute("""
                    SELECT value FROM old_literacy_values
                    WHERE country_id = %s AND year = %s
                """, (country_id, int(year)))
                
                old_result = cursor.fetchone()
                
                if old_result:
                    db_value = old_result[0]
                    
                    # Si les valeurs sont différentes, c'est qu'il y avait un doublon
                    if abs(db_value - csv_value) > 0.01:
                        # Calculer la moyenne
                        avg_value = (db_value + csv_value) / 2.0
                        
                        cursor.execute("""
                            UPDATE indicator_value
                            SET value = %s, source = %s
                            WHERE country_id = %s AND indicator_id = %s AND year = %s
                        """, (avg_value, source, country_id, indicator_id, int(year)))
                        
                        print(f"   📊 {country_name:25} {year}: {db_value:.2f} → moyenne({db_value:.2f}, {csv_value:.2f}) = {avg_value:.2f}")
                        corrected_count += 1
                    else:
                        skipped_count += 1
                        
            except ValueError:
                continue

conn.commit()

print(f"\n✅ Correction terminée!")
print(f"   • Valeurs corrigées (moyennes recalculées): {corrected_count}")
print(f"   • Valeurs inchangées: {skipped_count}")

cursor.close()
conn.close()
