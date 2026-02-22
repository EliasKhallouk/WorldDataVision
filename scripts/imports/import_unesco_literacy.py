#!/usr/bin/env python3
"""
Import des données UNESCO sur les taux d'alphabétisation des adultes.
Complète l'indicateur SE.ADT.LITR.ZS avec des données de Our World in Data / UNESCO.

Source: UNESCO Institute for Statistics (2025)
Fichier: literacy-rates-among-adults.csv
Indicateur: SE.ADT.LITR.ZS (Literacy rate, adult total)

Stratégie de fusion:
- Si la valeur existe déjà dans la BDD: calculer la moyenne (World Bank + UNESCO) / 2
- Si la valeur n'existe pas: insérer la nouvelle valeur UNESCO
"""

import csv
import psycopg2
import os
from typing import Dict, List, Tuple

# Configuration de la base de données
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'elias'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'worlddatavision'),
    'password': os.getenv('DB_PASSWORD', 'MaBaseDeDonnee'),
    'port': os.getenv('DB_PORT', 5432)
}

# Constantes
CSV_FILE = '/home/elias/PROJECT/WorldDataVision/Data/IRC/literacy-rates-among-adults.csv'
INDICATOR_CODE = 'SE.ADT.LITR.ZS'
NEW_SOURCE = 'World Bank + UNESCO (Literacy Rate)'


def get_country_mapping(conn) -> Dict[str, int]:
    """Récupère le mapping iso3 → country_id depuis la base de données."""
    cur = conn.cursor()
    cur.execute("SELECT iso3, id FROM country WHERE iso3 IS NOT NULL")
    mapping = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    return mapping


def get_indicator_id(conn, code: str) -> int:
    """Récupère l'ID de l'indicateur par son code."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM indicator WHERE code = %s", (code,))
    result = cur.fetchone()
    cur.close()
    
    if not result:
        raise ValueError(f"Indicateur {code} non trouvé dans la base de données")
    
    return result[0]


def read_unesco_csv(file_path: str) -> List[Tuple[str, int, float]]:
    """
    Lit le CSV UNESCO et retourne les données (iso3, year, value).
    
    Returns:
        List de tuples (iso3, year, value)
    """
    data = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            iso3 = row['Code'].strip()
            year = int(row['Year'])
            value_str = row['Literacy rate among adults'].strip()
            
            # Convertir la valeur en float
            try:
                value = float(value_str)
                data.append((iso3, year, value))
            except ValueError:
                # Ignorer les valeurs non numériques
                continue
    
    return data


def find_country_id(iso3: str, country_mapping: Dict[str, int]) -> int:
    """Trouve l'ID du pays par son code ISO3."""
    return country_mapping.get(iso3)


def upsert_values(conn, indicator_id: int, country_mapping: Dict[str, int], 
                  data: List[Tuple[str, int, float]]) -> Tuple[int, int, int]:
    """
    Insère ou met à jour les valeurs dans indicator_value.
    
    - Si valeur existe: calcule moyenne (existing + new) / 2
    - Sinon: insère nouvelle valeur
    
    Returns:
        Tuple (nb_inserted, nb_updated, nb_ignored)
    """
    cur = conn.cursor()
    
    inserted = 0
    updated = 0
    ignored = 0
    
    for iso3, year, unesco_value in data:
        country_id = find_country_id(iso3, country_mapping)
        
        if not country_id:
            ignored += 1
            continue
        
        # Vérifier si la valeur existe déjà
        cur.execute("""
            SELECT value FROM indicator_value
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (country_id, indicator_id, year))
        
        existing = cur.fetchone()
        
        if existing:
            # Calculer la moyenne
            existing_value = float(existing[0])
            new_value = (existing_value + unesco_value) / 2
            
            cur.execute("""
                UPDATE indicator_value
                SET value = %s
                WHERE country_id = %s AND indicator_id = %s AND year = %s
            """, (new_value, country_id, indicator_id, year))
            
            updated += 1
        else:
            # Insérer nouvelle valeur
            cur.execute("""
                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                VALUES (%s, %s, %s, %s)
            """, (country_id, indicator_id, year, unesco_value))
            
            inserted += 1
    
    cur.close()
    return (inserted, updated, ignored)


def update_indicator_source(conn, indicator_id: int, new_source: str):
    """Met à jour la source de l'indicateur."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE indicator
        SET source = %s
        WHERE id = %s
    """, (new_source, indicator_id))
    cur.close()


def main():
    """Fonction principale d'import."""
    print("="*80)
    print("📚 IMPORT DONNÉES UNESCO - TAUX D'ALPHABÉTISATION DES ADULTES")
    print("="*80)
    
    # Connexion à la base de données
    print("\n🔌 Connexion à la base de données...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        # Récupérer le mapping des pays
        print("🌍 Chargement du mapping des pays...")
        country_mapping = get_country_mapping(conn)
        print(f"   ✓ {len(country_mapping)} pays chargés")
        
        # Récupérer l'ID de l'indicateur
        print(f"\n📊 Recherche de l'indicateur {INDICATOR_CODE}...")
        indicator_id = get_indicator_id(conn, INDICATOR_CODE)
        print(f"   ✓ Indicateur trouvé (ID: {indicator_id})")
        
        # Lire le CSV UNESCO
        print(f"\n📄 Lecture du fichier CSV...")
        print(f"   Fichier: {CSV_FILE}")
        data = read_unesco_csv(CSV_FILE)
        print(f"   ✓ {len(data)} valeurs parsées")
        
        # Afficher quelques statistiques
        years = sorted(set(year for _, year, _ in data))
        countries = set(iso3 for iso3, _, _ in data)
        print(f"\n📈 Statistiques des données UNESCO:")
        print(f"   • Pays: {len(countries)}")
        print(f"   • Années: {years[0]}-{years[-1]}")
        print(f"   • Valeurs totales: {len(data)}")
        
        # Insertion/Mise à jour
        print(f"\n💾 Import des données dans la base...")
        inserted, updated, ignored = upsert_values(conn, indicator_id, country_mapping, data)
        
        # Mise à jour de la source
        print(f"\n🏷️  Mise à jour de la source de l'indicateur...")
        update_indicator_source(conn, indicator_id, NEW_SOURCE)
        
        # Commit
        conn.commit()
        print("   ✓ Commit effectué")
        
        # Résumé
        print("\n" + "="*80)
        print("✅ Import terminé avec succès!")
        print(f"   📥 Nouvelles valeurs insérées: {inserted}")
        print(f"   🔄 Valeurs mises à jour (moyenne): {updated}")
        print(f"   ⏭️  Valeurs ignorées (pays non trouvé): {ignored}")
        print("="*80)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de l'import: {e}")
        raise
    
    finally:
        conn.close()
        print("\n🔌 Connexion fermée")


if __name__ == "__main__":
    main()
