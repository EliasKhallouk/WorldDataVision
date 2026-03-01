#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import du taux d'alphabétisation des adultes depuis KIDB-alphabetisation_adulte.csv
Indicateur: Adult (15 Years and Older) Literacy Rate, Both Sexes (%)
"""

import psycopg2
import csv
import os
import sys

# Configuration base de données
DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'elias',
    'password': 'MaBaseDeDonnee',
    'host': 'localhost',
    'port': '5432'
}

# Mapping des noms de pays vers codes ISO3
# Note: On ne garde que les pays principaux, pas les régions (ARM-xxx, AZE-xxx, etc.)
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

def get_country_id(cursor, country_name):
    """Récupère l'ID du pays depuis la base de données"""
    # D'abord essayer avec le mapping
    iso3 = COUNTRY_MAPPING.get(country_name)
    
    if iso3:
        cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3,))
    else:
        # Sinon essayer par nom
        cursor.execute("SELECT id FROM country WHERE name = %s", (country_name,))
    
    result = cursor.fetchone()
    return result[0] if result else None

def get_or_create_indicator(cursor, conn):
    """Récupère ou crée l'indicateur d'alphabétisation"""
    indicator_code = 'SE.ADT.LITR.ZS'
    indicator_name = 'Adult literacy rate, population 15+ years, both sexes (%)'
    
    # Vérifier si l'indicateur existe
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    
    if result:
        print(f"✓ Indicateur existant trouvé: {indicator_code}")
        return result[0]
    
    # Créer l'indicateur
    # Category 2 = Éducation (à vérifier dans votre base)
    cursor.execute("""
        INSERT INTO indicator (code, name, category_id, description, unit)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        indicator_code,
        indicator_name,
        2,  # Category Éducation
        "The percentage of the population aged 15 years and older who can both read and write (with understanding) a short simple statement on his or her everyday life. Generally, literacy also encompasses numeracy, i.e., the ability to make simple arithmetic calculations.",
        "percent"
    ))
    
    indicator_id = cursor.fetchone()[0]
    conn.commit()
    print(f"✓ Nouvel indicateur créé: {indicator_code} (ID: {indicator_id})")
    return indicator_id

def import_literacy_data(csv_file_path):
    """Import les données du CSV dans la base"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print(f"\n📂 Lecture du fichier: {csv_file_path}")
    
    try:
        # Récupérer ou créer l'indicateur
        indicator_id = get_or_create_indicator(cursor, conn)
        
        # Lire le CSV
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Les années sont dans les colonnes 2000-2025
            year_columns = [str(year) for year in range(2000, 2026)]
            
            inserted_count = 0
            skipped_count = 0
            error_count = 0
            
            for row in reader:
                country_name = row['Economy'].strip()
                unit = row['Unit of Measure'].strip()
                
                # Ignorer les lignes sans unité (régions/groupes)
                if not unit or unit == '':
                    skipped_count += 1
                    continue
                
                # Ignorer les sous-régions (ARM-xxx, AZE-xxx, etc.)
                if '-' in country_name and len(country_name.split('-')[0]) == 3:
                    skipped_count += 1
                    continue
                
                # Récupérer l'ID du pays
                country_id = get_country_id(cursor, country_name)
                
                if not country_id:
                    print(f"⚠️  Pays non trouvé: {country_name}")
                    error_count += 1
                    continue
                
                # Insérer les valeurs pour chaque année
                for year in year_columns:
                    value_str = row.get(year, '').strip()
                    
                    # Ignorer les valeurs manquantes
                    if not value_str or value_str == '...' or value_str == '':
                        continue
                    
                    try:
                        value = float(value_str)
                        
                        # Vérifier si la valeur existe déjà
                        cursor.execute("""
                            SELECT id, value FROM indicator_value
                            WHERE country_id = %s AND indicator_id = %s AND year = %s
                        """, (country_id, indicator_id, int(year)))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Calculer la moyenne entre l'ancienne et la nouvelle valeur
                            old_value = existing[1]
                            avg_value = (old_value + value) / 2.0
                            
                            cursor.execute("""
                                UPDATE indicator_value
                                SET value = %s
                                WHERE country_id = %s AND indicator_id = %s AND year = %s
                            """, (avg_value, country_id, indicator_id, int(year)))
                            
                            print(f"   ⚠️  Moyenne calculée pour {country_name} ({year}): {old_value:.2f} + {value:.2f} = {avg_value:.2f}")
                        else:
                            # Insertion
                            cursor.execute("""
                                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                                VALUES (%s, %s, %s, %s)
                            """, (country_id, indicator_id, int(year), value))
                        
                        inserted_count += 1
                        
                    except ValueError:
                        print(f"⚠️  Valeur invalide pour {country_name} ({year}): {value_str}")
                        error_count += 1
            
            # Commit final
            conn.commit()
            
            print(f"\n✅ Import terminé!")
            print(f"   • Valeurs insérées/mises à jour: {inserted_count}")
            print(f"   • Lignes ignorées (régions): {skipped_count}")
            print(f"   • Erreurs: {error_count}")
    
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de l'import: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    csv_path = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/KIDB-alphabetisation_adulte.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier introuvable: {csv_path}")
        sys.exit(1)
    
    import_literacy_data(csv_path)
