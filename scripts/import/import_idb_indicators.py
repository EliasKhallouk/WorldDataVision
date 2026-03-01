#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import IDB (Inter-American Development Bank) indicators
Avec validation stricte des unités et conversions appropriées
"""

import os
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

print("=" * 100)
print("IMPORT IDB - 16 INDICATEURS VALIDÉS")
print("=" * 100)

# Configuration des 16 indicateurs validés
INDICATORS_CONFIG = [
    # CATÉGORIE 1 - ÉCONOMIE
    {
        'folder': 'Percentage of unemployed population',
        'irc_code': 'SL.UEM.TOTL.ZS',
        'conversion': lambda x: x * 100,  # Decimal → Pourcentage
        'validation_range': (0, 100),
    },
    
    # CATÉGORIE 2 - ÉDUCATION (Années de scolarisation)
    {
        'folder': 'Average years of education of people aged 25 or older',
        'irc_code': None,  # Nouvel indicateur
        'new_indicator': {
            'code': 'SE.AVG.EDU.25UP',
            'name': 'Années moyennes d\'éducation (25+ ans)',
            'category_id': 2
        },
        'conversion': None,  # Pas de conversion
        'validation_range': (0, 25),
    },
    {
        'folder': 'Average years of education of people aged 25+ (Census)',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.AVG.EDU.25UP.CENSUS',
            'name': 'Années moyennes d\'éducation (25+ ans, Census)',
            'category_id': 2
        },
        'conversion': None,
        'validation_range': (0, 25),
    },
    {
        'folder': 'Average years of schooling',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.AVG.SCHOOL',
            'name': 'Années moyennes de scolarisation',
            'category_id': 2
        },
        'conversion': None,
        'validation_range': (0, 25),
    },
    
    # CATÉGORIE 2 - SANTÉ
    {
        'folder': 'Medical doctors per 10 000 population',
        'irc_code': 'SH.MED.PHYS.ZS',
        'conversion': lambda x: x / 10,  # Per 10,000 → Per 1,000
        'validation_range': (0, 20),
    },
    
    # CATÉGORIE 2 - ÉDUCATION (Taux de fréquentation)
    {
        'folder': 'Attenadance rate 4-5 years old',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.ATTEND.04-05',
            'name': 'Taux de fréquentation scolaire 4-5 ans (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Attenadance rate 6-11 years old',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.ATTEND.06-11',
            'name': 'Taux de fréquentation scolaire 6-11 ans (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Attenadance rate 12-14 years old',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.ATTEND.12-14',
            'name': 'Taux de fréquentation scolaire 12-14 ans (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Attenadance rate 15-17 years old',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.ATTEND.15-17',
            'name': 'Taux de fréquentation scolaire 15-17 ans (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Attenadance rate 18-23 years old',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.ATTEND.18-23',
            'name': 'Taux de fréquentation scolaire 18-23 ans (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    
    # CATÉGORIE 2 - ÉDUCATION (Taux de complétion)
    {
        'folder': 'Completion rate in primary education',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.COMPL.PRIM',
            'name': 'Taux de complétion primaire (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Completion rate in secondary education',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.COMPL.SEC',
            'name': 'Taux de complétion secondaire (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Completion rate in tertiary education',
        'irc_code': None,
        'new_indicator': {
            'code': 'SE.COMPL.TERT',
            'name': 'Taux de complétion tertiaire (%)',
            'category_id': 2
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    
    # CATÉGORIE 3 - DÉMOGRAPHIE
    {
        'folder': 'Percentage of population residing in urban areas (Census)',
        'irc_code': 'SP.URB.TOTL.IN.ZS',
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Percentage of population residing in rural areas',
        'irc_code': None,
        'new_indicator': {
            'code': 'SP.RUR.TOTL.IN.ZS',
            'name': 'Population rurale (% du total)',
            'category_id': 3
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
    {
        'folder': 'Percentage of migrants in population (Census)',
        'irc_code': None,
        'new_indicator': {
            'code': 'SM.POP.MIGR.ZS',
            'name': 'Migrants (% de la population, Census)',
            'category_id': 3
        },
        'conversion': lambda x: x * 100,
        'validation_range': (0, 100),
    },
]

# Charger la table country pour le mapping
cur.execute("SELECT iso3, id FROM country")
country_map = {row[0]: row[1] for row in cur.fetchall()}

print(f"\n[1] CRÉATION DES NOUVEAUX INDICATEURS")
print("=" * 100)

indicator_ids = {}

for config in INDICATORS_CONFIG:
    if config['irc_code']:
        # Indicateur existant
        cur.execute("SELECT id FROM indicator WHERE code = %s", (config['irc_code'],))
        result = cur.fetchone()
        if result:
            indicator_ids[config['folder']] = result[0]
            print(f"  ✓ {config['irc_code']}: ID={result[0]} (existant)")
    elif config.get('new_indicator'):
        # Créer nouvel indicateur
        new_ind = config['new_indicator']
        
        # Vérifier s'il existe déjà
        cur.execute("SELECT id FROM indicator WHERE code = %s", (new_ind['code'],))
        result = cur.fetchone()
        
        if result:
            indicator_ids[config['folder']] = result[0]
            print(f"  ↻ {new_ind['code']}: ID={result[0]} (déjà existant)")
        else:
            cur.execute("""
                INSERT INTO indicator (code, name, category_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (new_ind['code'], new_ind['name'], new_ind['category_id']))
            
            indicator_id = cur.fetchone()[0]
            indicator_ids[config['folder']] = indicator_id
            print(f"  + {new_ind['code']}: ID={indicator_id} (créé)")

conn.commit()

print(f"\n[2] IMPORT DES DONNÉES")
print("=" * 100)

idb_path = 'Data/IDB'
total_imported = 0
total_updated = 0

for config in INDICATORS_CONFIG:
    folder_name = config['folder']
    folder_path = os.path.join(idb_path, folder_name)
    
    print(f"\n📊 {folder_name}")
    
    if folder_name not in indicator_ids:
        print(f"  ❌ SKIP: Indicateur non configuré")
        continue
    
    indicator_id = indicator_ids[folder_name]
    
    # Lire le CSV
    csv_files = [f for f in os.listdir(folder_path) 
                 if f.endswith('.csv') and not f.endswith('_metadata.csv')]
    
    if not csv_files:
        print(f"  ❌ SKIP: Pas de CSV")
        continue
    
    csv_file = os.path.join(folder_path, csv_files[0])
    
    # Charger les données
    data_to_import = []
    skipped_count = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:  # UTF-8-SIG pour gérer BOM
        reader = csv.DictReader(f)
        
        # Agréger les données par pays/année (moyenne des désagrégations)
        aggregated_data = {}
        
        for row in reader:
            try:
                # Les colonnes peuvent avoir le BOM, nettoyer
                country_code = row.get('isoalpha3', '').strip()
                year_str = row.get('year', '') or row.get('\ufeffyear', '')
                value_str = row.get('value', '')
                
                # Filtrer pour données nationales uniquement
                idgeo = row.get('idgeo', '')
                if idgeo != 'country':
                    continue
                
                # Filtrer pour Total (pas par quintile, sexe, etc.)
                quintile = row.get('quintile', '')
                sex = row.get('sex', '')
                age = row.get('age', '')
                education_level = row.get('education_level', '')
                ethnicity = row.get('ethnicity', '')
                
                # Ne garder que les totaux
                if quintile != 'Total' or sex != 'Total' or age != 'Total' or \
                   education_level != 'Total' or ethnicity != 'Total':
                    continue
                
                if not country_code or not year_str or not value_str or not value_str.strip():
                    skipped_count += 1
                    continue
                
                # Convertir
                year = int(year_str)
                value = float(value_str)
                
                # Créer clé unique pour agréger
                key = (country_code, year)
                
                # Agréger (moyenne si plusieurs valeurs pour même pays/année)
                if key not in aggregated_data:
                    aggregated_data[key] = {'values': [], 'country_code': country_code, 'year': year}
                
                aggregated_data[key]['values'].append(value)
            
            except (ValueError, KeyError):
                skipped_count += 1
                continue
        
        # Calculer moyennes et préparer import
        for key, data in aggregated_data.items():
            country_code = data['country_code']
            year = data['year']
            values = data['values']
            
            # Moyenne des valeurs
            avg_value = sum(values) / len(values)
            
            # Appliquer conversion si nécessaire
            if config['conversion']:
                avg_value = config['conversion'](avg_value)
            
            # Valider range
            min_val, max_val = config['validation_range']
            if avg_value < min_val or avg_value > max_val:
                skipped_count += 1
                continue
            
            # Mapper pays
            if country_code not in country_map:
                skipped_count += 1
                continue
            
            country_id = country_map[country_code]
            
            data_to_import.append({
                'country_id': country_id,
                'year': year,
                'value': avg_value
            })
    
    print(f"  📥 Données préparées: {len(data_to_import)} valeurs")
    if skipped_count > 0:
        print(f"  ⚠️  Ignorées: {skipped_count} (hors range ou invalides)")
    
    # Import avec averaging
    new_count = 0
    updated_count = 0
    
    for item in data_to_import:
        # Vérifier si existe
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
    
    total_imported += new_count
    total_updated += updated_count
    
    print(f"  ✅ Nouvelles: {new_count}")
    print(f"  ✅ Moyennées: {updated_count}")

print(f"\n{'='*100}")
print(f"RÉSUMÉ FINAL")
print(f"{'='*100}")
print(f"  Total nouvelles valeurs: {total_imported}")
print(f"  Total valeurs moyennées: {total_updated}")
print(f"  Total insertions/mises à jour: {total_imported + total_updated}")

print(f"\n✅ IMPORT TERMINÉ AVEC SUCCÈS")
print("=" * 100 + "\n")

cur.close()
conn.close()
