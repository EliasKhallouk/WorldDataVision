#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import du taux d'alphabétisation depuis la Banque Mondiale
Source: Data/IRC/literacy_rate_adult.csv
Indicateur: SE.ADT.LITR.ZS
"""

import psycopg2
import csv
import os

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'elias',
    'password': 'MaBaseDeDonnee',
    'host': 'localhost',
    'port': '5432'
}

def import_world_bank_literacy():
    """Import des données de la Banque Mondiale"""
    csv_path = '/home/elias/PROJECT/WorldDataVision/Data/IRC/literacy_rate_adult.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier introuvable: {csv_path}")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print(f"\n📂 Import depuis Banque Mondiale: {csv_path}")
    
    try:
        # Récupérer l'ID de l'indicateur
        cursor.execute("SELECT id FROM indicator WHERE code = 'SE.ADT.LITR.ZS'")
        indicator_result = cursor.fetchone()
        
        if not indicator_result:
            print("❌ Indicateur SE.ADT.LITR.ZS non trouvé")
            return
        
        indicator_id = indicator_result[0]
        print(f"✓ Indicateur ID: {indicator_id}")
        
        inserted_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                country_code = row['country_code'].strip()
                year = int(row['year'])
                value_str = row['value'].strip()
                
                if not value_str or value_str == '':
                    continue
                
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                
                # Récupérer l'ID du pays
                cursor.execute("SELECT id FROM country WHERE iso3 = %s", (country_code,))
                country_result = cursor.fetchone()
                
                if not country_result:
                    skipped_count += 1
                    continue
                
                country_id = country_result[0]
                
                # Vérifier si existe déjà
                cursor.execute("""
                    SELECT id, value FROM indicator_value
                    WHERE country_id = %s AND indicator_id = %s AND year = %s
                """, (country_id, indicator_id, year))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Calculer moyenne
                    old_value = existing[1]
                    avg_value = (old_value + value) / 2.0
                    
                    cursor.execute("""
                        UPDATE indicator_value
                        SET value = %s
                        WHERE country_id = %s AND indicator_id = %s AND year = %s
                    """, (avg_value, country_id, indicator_id, year))
                    
                    print(f"   ⚠️  Moyenne: {country_code} {year}: {old_value:.2f} + {value:.2f} = {avg_value:.2f}")
                else:
                    # Insertion
                    cursor.execute("""
                        INSERT INTO indicator_value (country_id, indicator_id, year, value)
                        VALUES (%s, %s, %s, %s)
                    """, (country_id, indicator_id, year, value))
                
                inserted_count += 1
        
        conn.commit()
        
        print(f"\n✅ Import Banque Mondiale terminé!")
        print(f"   • Valeurs insérées/mises à jour: {inserted_count}")
        print(f"   • Lignes ignorées (pays non trouvés): {skipped_count}")
    
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    import_world_bank_literacy()
