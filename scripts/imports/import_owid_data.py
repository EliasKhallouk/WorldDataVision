#!/usr/bin/env python3
"""
Import des données Our World in Data pour compléter les indicateurs IRC manquants.
Stratégie: Si la donnée existe déjà, faire la moyenne (World Bank + OWID) / 2
"""

import psycopg2
import csv
import os
import sys
from collections import defaultdict

# Configuration BDD
DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'elias',
    'password': 'MaBaseDeDonnee',
    'host': 'localhost',
    'port': '5432'
}

# Mapping World Bank Indicator Code → Our World in Data CSV file
# Format: 'WB_CODE': ('owid_filename.csv', 'column_name', 'description_for_verification')
OWID_INDICATOR_MAPPING = {
    # Alphabétisation adultes (déjà fait avec UNESCO mais on peut croiser)
    'SE.ADT.LITR.ZS': ('literacy-rates-among-adults.csv', 'Literacy rate', 'Adult literacy rate (15+)'),
    
    # Dépenses R&D (% PIB) ✅ DISPONIBLE
    'GB.XPD.RSDV.GD.ZS': ('research-and-development-expenditure-of-gdp.csv', 'Research and development expenditure (% of GDP)', 'R&D expenditure as % of GDP'),
    
    # Consommation d'électricité par habitant (kWh) ✅ DISPONIBLE
    'EG.USE.ELEC.KH.PC': ('per-capita-electricity-use.csv', 'Electricity consumption per capita (kWh)', 'Electricity use per capita'),
    
    # Consommation énergétique par habitant ✅ DISPONIBLE
    'EG.USE.PCAP.KG.OE': ('per-capita-energy-use.csv', 'Primary energy consumption per capita (kWh/person)', 'Energy use per capita'),
    
    # Rendement des céréales (kg/hectare) ✅ DISPONIBLE
    'AG.YLD.CREL.KG': ('cereal-yield.csv', 'Cereal yield (tonnes per hectare)', 'Cereal yield'),
    
    # Dépenses militaires (% PIB) ✅ DISPONIBLE
    'MS.MIL.XPND.GD.ZS': ('military-expenditure-as-a-share-of-gdp.csv', 'Military expenditure (% of GDP)', 'Military spending % GDP'),
    
    # Consommation combustibles fossiles (% total) ✅ DISPONIBLE
    'EG.USE.COMM.FO.ZS': ('fossil-fuels-share-energy.csv', 'Fossil fuels (% of total energy)', 'Fossil fuel consumption %'),
    
    # Revenus fiscaux ✅ DISPONIBLE
    'GC.TAX.TOTL.GD.ZS': ('total-tax-revenue-gdp.csv', 'Tax revenue (% of GDP)', 'Tax revenues % GDP'),
    
    # Chercheurs en R&D ✅ COMPATIBLE (téléchargé manuellement)
    'SP.POP.SCIE.RD.P6': ('researchers-in-rd-per-million-people.csv', 'Researchers in R&D (per million people)', 'Researchers per million'),
    
    # Stress hydrique ✅ COMPATIBLE (téléchargé manuellement)
    'ER.H2O.FWST.ZS': ('freshwater-withdrawals-as-a-share-of-internal-resources.csv', 'Level of water stress', 'Freshwater withdrawal %'),
    
    # Importations nettes d'énergie ✅ COMPATIBLE (téléchargé manuellement)
    'EG.IMP.CONS.ZS': ('energy-imports-and-exports-energy-use.csv', 'Energy imports, net (% of energy use)', 'Net energy imports %'),
    
    # ⚠️ Brevets - INCOMPATIBLE (WB = nombre absolu, OWID = par million) - EXCLU
    # 'IP.PAT.RESD': ('patent-applications-per-million.csv', ...),
}


def get_country_mapping(conn):
    """Récupère le mapping iso3 → country_id depuis la DB"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, iso3, name FROM country ORDER BY id")
    
    mapping = {}
    for country_id, iso3, name in cursor.fetchall():
        if iso3:
            mapping[iso3.upper()] = (country_id, name)
    
    cursor.close()
    return mapping


def get_indicator_id(conn, wb_code):
    """Récupère l'ID de l'indicateur depuis son code World Bank"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM indicator WHERE code = %s", (wb_code,))
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return result[0], result[1]
    return None, None


def convert_unit(value, indicator_code, value_column):
    """
    Convertit les unités OWID vers les unités World Bank si nécessaire.
    
    Conversions connues:
    - AG.YLD.CREL.KG: tonnes/ha → kg/ha (×1000)
    """
    # Rendement céréales: OWID en tonnes/ha, WB en kg/ha
    if indicator_code == 'AG.YLD.CREL.KG':
        if 'tonne' in value_column.lower():
            return value * 1000  # tonnes → kg
    
    # Pas de conversion nécessaire
    return value


def read_owid_csv(file_path, indicator_code=''):
    """
    Lit un fichier CSV Our World in Data.
    Format typique: Entity, Code, Year, [IndicatorName]
    Retourne: liste de tuples (iso3, year, value)
    """
    if not os.path.exists(file_path):
        print(f"⚠️ Fichier non trouvé: {file_path}")
        return []
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Détecter le nom de la colonne de valeur (dernière colonne généralement)
        columns = reader.fieldnames
        value_column = None
        
        for col in columns:
            if col not in ['Entity', 'Code', 'Year']:
                value_column = col
                break
        
        if not value_column:
            print(f"⚠️ Impossible de trouver la colonne de valeur dans {file_path}")
            return []
        
        print(f"📊 Colonne de valeur détectée: '{value_column}'")
        
        for row in reader:
            iso3 = row.get('Code', '').strip()
            year = row.get('Year', '').strip()
            value_str = row.get(value_column, '').strip()
            
            # Filtrer les agrégats (OWID_*, vide, etc.)
            if not iso3 or iso3.startswith('OWID_') or len(iso3) != 3:
                continue
            
            if not year or not value_str:
                continue
            
            try:
                year = int(year)
                
                # ⚠️ Filtrer les années hors de la plage DB (1950-2035)
                if year < 1950 or year > 2035:
                    continue
                
                value = float(value_str)
                
                # Appliquer les conversions d'unités si nécessaire
                value = convert_unit(value, indicator_code, value_column)
                
                data.append((iso3.upper(), year, value))
            except (ValueError, TypeError):
                continue
    
    return data


def upsert_values(conn, indicator_id, indicator_code, country_mapping, owid_data):
    """
    Insère ou met à jour les valeurs dans indicator_value.
    Si la valeur existe déjà, calcule la moyenne (existant + OWID) / 2
    """
    cursor = conn.cursor()
    
    inserted = 0
    updated = 0
    ignored = 0
    
    for iso3, year, value in owid_data:
        # Trouver le country_id
        if iso3 not in country_mapping:
            ignored += 1
            continue
        
        country_id, country_name = country_mapping[iso3]
        
        # Vérifier si la valeur existe déjà
        cursor.execute("""
            SELECT value FROM indicator_value 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (country_id, indicator_id, year))
        
        existing = cursor.fetchone()
        
        if existing:
            # Moyenne des deux valeurs
            existing_value = existing[0]
            new_value = (existing_value + value) / 2
            
            cursor.execute("""
                UPDATE indicator_value 
                SET value = %s
                WHERE country_id = %s AND indicator_id = %s AND year = %s
            """, (new_value, country_id, indicator_id, year))
            
            updated += 1
        else:
            # Insertion nouvelle valeur
            cursor.execute("""
                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                VALUES (%s, %s, %s, %s)
            """, (country_id, indicator_id, year, value))
            
            inserted += 1
    
    conn.commit()
    cursor.close()
    
    return inserted, updated, ignored


def update_indicator_source(conn, indicator_code, new_source):
    """Met à jour la source de l'indicateur dans la table indicator"""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE indicator 
        SET source = %s 
        WHERE code = %s
    """, (new_source, indicator_code))
    conn.commit()
    cursor.close()


def main():
    print("="*80)
    print("📥 IMPORT DONNÉES OUR WORLD IN DATA - INDICATEURS IRC")
    print("="*80)
    
    # Vérifier le dossier des données OWID
    owid_data_dir = '/home/elias/PROJECT/WorldDataVision/Data/OWID'
    
    if not os.path.exists(owid_data_dir):
        print(f"\n⚠️ Dossier OWID non trouvé: {owid_data_dir}")
        print("Veuillez télécharger les datasets Our World in Data et les placer dans ce dossier.")
        print("\nIndicateurs à télécharger:")
        for wb_code, (filename, _, description) in OWID_INDICATOR_MAPPING.items():
            print(f"  • {filename} - {description}")
        sys.exit(1)
    
    # Connexion DB
    conn = psycopg2.connect(**DB_CONFIG)
    print("✓ Connecté à PostgreSQL")
    
    # Charger le mapping des pays
    country_mapping = get_country_mapping(conn)
    print(f"✓ {len(country_mapping)} pays chargés")
    
    # Statistiques globales
    total_inserted = 0
    total_updated = 0
    total_ignored = 0
    
    # Traiter chaque indicateur
    for wb_code, (owid_filename, expected_column, description) in OWID_INDICATOR_MAPPING.items():
        print(f"\n{'='*80}")
        print(f"📊 Traitement: {wb_code}")
        print(f"   Description: {description}")
        print(f"   Fichier OWID: {owid_filename}")
        print(f"{'='*80}")
        
        # Vérifier que l'indicateur existe dans la DB
        indicator_id, indicator_name = get_indicator_id(conn, wb_code)
        
        if not indicator_id:
            print(f"⚠️ Indicateur {wb_code} non trouvé dans la DB - SKIP")
            continue
        
        print(f"✓ Indicateur trouvé (ID: {indicator_id}): {indicator_name}")
        
        # Lire les données OWID
        file_path = os.path.join(owid_data_dir, owid_filename)
        owid_data = read_owid_csv(file_path, wb_code)
        
        if not owid_data:
            print(f"⚠️ Aucune donnée trouvée dans {owid_filename} - SKIP")
            continue
        
        print(f"✓ {len(owid_data)} valeurs parsées")
        
        # Statistiques OWID
        countries = set(iso3 for iso3, _, _ in owid_data)
        years = set(year for _, year, _ in owid_data)
        print(f"📈 Statistiques: {len(countries)} pays, {min(years)}-{max(years)}, {len(owid_data)} valeurs")
        
        # Import dans la DB
        inserted, updated, ignored = upsert_values(conn, indicator_id, wb_code, country_mapping, owid_data)
        
        total_inserted += inserted
        total_updated += updated
        total_ignored += ignored
        
        print(f"\n✅ Import terminé:")
        print(f"   📥 Nouvelles valeurs insérées: {inserted}")
        print(f"   🔄 Valeurs mises à jour (moyenne): {updated}")
        print(f"   ⏭️ Valeurs ignorées (pays non trouvé): {ignored}")
        
        # Mettre à jour la source
        new_source = f"World Bank + Our World in Data ({description})"
        update_indicator_source(conn, wb_code, new_source)
        print(f"   ✓ Source mise à jour: '{new_source}'")
    
    # Résumé global
    print(f"\n{'='*80}")
    print("📊 RÉSUMÉ GLOBAL DE L'IMPORT")
    print(f"{'='*80}")
    print(f"Total nouvelles valeurs insérées: {total_inserted}")
    print(f"Total valeurs moyennées: {total_updated}")
    print(f"Total valeurs ignorées: {total_ignored}")
    print(f"Total valeurs traitées: {total_inserted + total_updated + total_ignored}")
    
    if total_inserted + total_updated > 0:
        success_rate = 100 * (total_inserted + total_updated) / (total_inserted + total_updated + total_ignored)
        print(f"\n✅ Taux de succès: {success_rate:.1f}%")
    
    conn.close()
    print("\n✓ Connexion fermée")


if __name__ == '__main__':
    main()
