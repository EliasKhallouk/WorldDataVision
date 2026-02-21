#!/usr/bin/env python3
"""
Script d'import des données de dette publique du FMI
Source: IMF - Central Government Debt (Percent of GDP)
Fichier: Data/IRC/imf-dm-export-20260221.csv

Fonctionnalités:
- Conversion format large → format long
- Mapping noms de pays (anglais) → codes ISO3
- Fusion avec données existantes (moyenne si dupliqué)
- Mise à jour des métadonnées de l'indicateur
"""

import csv
import psycopg2
from psycopg2 import sql
import os
import sys
from typing import Dict, List, Tuple, Optional
import unicodedata

# Configuration de la base de données
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'elias'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'worlddatavision'),
    'password': os.getenv('DB_PASSWORD', 'MaBaseDeDonnee'),
    'port': os.getenv('DB_PORT', 5432)
}

# Mapping exhaustif COMPLET des noms de pays IMF (anglais) → codes ISO3
# Les pays de la DB sont en FRANÇAIS, donc on doit mapper TOUS les pays IMF manuellement
COUNTRY_NAME_MAPPING = {
    # A
    "Afghanistan": "AFG",
    "Albania": "ALB",
    "Algeria": "DZA",
    "Angola": "AGO",
    "Antigua and Barbuda": "ATG",
    "Argentina": "ARG",
    "Armenia": "ARM",
    "Australia": "AUS",
    "Austria": "AUT",
    "Azerbaijan": "AZE",
    
    # B
    "Bahamas, The": "BHS",
    "Bahrain": "BHR",
    "Bangladesh": "BGD",
    "Barbados": "BRB",
    "Belarus": "BLR",
    "Belgium": "BEL",
    "Belize": "BLZ",
    "Benin": "BEN",
    "Bhutan": "BTN",
    "Bolivia": "BOL",
    "Bosnia and Herzegovina": "BIH",
    "Botswana": "BWA",
    "Brazil": "BRA",
    "Brunei Darussalam": "BRN",
    "Bulgaria": "BGR",
    "Burkina Faso": "BFA",
    "Burundi": "BDI",
    
    # C
    "Cabo Verde": "CPV",
    "Cambodia": "KHM",
    "Cameroon": "CMR",
    "Canada": "CAN",
    "Central African Republic": "CAF",
    "Chad": "TCD",
    "Chile": "CHL",
    "China": "CHN",
    "Colombia": "COL",
    "Comoros": "COM",
    "Congo, Democratic Republic of the": "COD",
    "Congo, Dem. Rep.": "COD",
    "Congo, Republic of ": "COG",  # Note: espace final dans CSV
    "Congo, Rep.": "COG",
    "Costa Rica": "CRI",
    "Croatia": "HRV",
    "Cyprus": "CYP",
    "Czech Republic": "CZE",
    "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    
    # D
    "Denmark": "DNK",
    "Djibouti": "DJI",
    "Dominica": "DMA",
    "Dominican Republic": "DOM",
    
    # E
    "Ecuador": "ECU",
    "Egypt": "EGY",
    "Egypt, Arab Rep.": "EGY",
    "El Salvador": "SLV",
    "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI",
    "Estonia": "EST",
    "Eswatini": "SWZ",
    "Ethiopia": "ETH",
    
    # F
    "Fiji": "FJI",
    "Finland": "FIN",
    "France": "FRA",
    
    # G
    "Gabon": "GAB",
    "Gambia, The": "GMB",
    "Georgia": "GEO",
    "Germany": "DEU",
    "Ghana": "GHA",
    "Greece": "GRC",
    "Grenada": "GRD",
    "Guatemala": "GTM",
    "Guinea": "GIN",
    "Guinea-Bissau": "GNB",
    "Guyana": "GUY",
    
    # H
    "Haiti": "HTI",
    "Honduras": "HND",
    "Hong Kong SAR": "HKG",
    "Hungary": "HUN",
    
    # I
    "Iceland": "ISL",
    "India": "IND",
    "Indonesia": "IDN",
    "Iran": "IRN",
    "Iran, Islamic Rep.": "IRN",
    "Iraq": "IRQ",
    "Ireland": "IRL",
    "Israel": "ISR",
    "Italy": "ITA",
    
    # J
    "Jamaica": "JAM",
    "Japan": "JPN",
    "Jordan": "JOR",
    
    # K
    "Kazakhstan": "KAZ",
    "Kenya": "KEN",
    "Kiribati": "KIR",
    "Korea": "KOR",
    "Korea, Republic of": "KOR",
    "Korea, Rep.": "KOR",
    "Kosovo": "XKX",
    "Kuwait": "KWT",
    "Kyrgyz Republic": "KGZ",
    
    # L
    "Lao P.D.R.": "LAO",
    "Lao PDR": "LAO",
    "Latvia": "LVA",
    "Lebanon": "LBN",
    "Lesotho": "LSO",
    "Liberia": "LBR",
    "Libya": "LBY",
    "Lithuania": "LTU",
    "Luxembourg": "LUX",
    
    # M
    "Macao SAR": "MAC",
    "Madagascar": "MDG",
    "Malawi": "MWI",
    "Malaysia": "MYS",
    "Maldives": "MDV",
    "Mali": "MLI",
    "Malta": "MLT",
    "Marshall Islands": "MHL",
    "Mauritania": "MRT",
    "Mauritius": "MUS",
    "Mexico": "MEX",
    "Micronesia": "FSM",
    "Micronesia, Fed. Sts.": "FSM",
    "Moldova": "MDA",
    "Mongolia": "MNG",
    "Montenegro": "MNE",
    "Morocco": "MAR",
    "Mozambique": "MOZ",
    "Myanmar": "MMR",
    
    # N
    "Namibia": "NAM",
    "Nauru": "NRU",
    "Nepal": "NPL",
    "Netherlands": "NLD",
    "New Zealand": "NZL",
    "Nicaragua": "NIC",
    "Niger": "NER",
    "Nigeria": "NGA",
    "North Macedonia": "MKD",
    "North Macedonia ": "MKD",  # Note: espace final possible
    "Norway": "NOR",
    
    # O
    "Oman": "OMN",
    
    # P
    "Pakistan": "PAK",
    "Palau": "PLW",
    "Panama": "PAN",
    "Papua New Guinea": "PNG",
    "Paraguay": "PRY",
    "Peru": "PER",
    "Philippines": "PHL",
    "Poland": "POL",
    "Portugal": "PRT",
    
    # Q
    "Qatar": "QAT",
    
    # R
    "Romania": "ROU",
    "Russia": "RUS",
    "Russian Federation": "RUS",
    "Rwanda": "RWA",
    
    # S
    "Samoa": "WSM",
    "San Marino": "SMR",
    "Saudi Arabia": "SAU",
    "Senegal": "SEN",
    "Serbia": "SRB",
    "Seychelles": "SYC",
    "Sierra Leone": "SLE",
    "Singapore": "SGP",
    "Slovak Republic": "SVK",
    "Slovenia": "SVN",
    "Solomon Islands": "SLB",
    "Somalia": "SOM",
    "South Africa": "ZAF",
    "South Sudan": "SSD",
    "South Sudan, Republic of": "SSD",
    "Spain": "ESP",
    "Sri Lanka": "LKA",
    "St. Kitts and Nevis": "KNA",
    "Saint Kitts and Nevis": "KNA",
    "St. Lucia": "LCA",
    "Saint Lucia": "LCA",
    "St. Vincent and the Grenadines": "VCT",
    "Saint Vincent and the Grenadines": "VCT",
    "Sudan": "SDN",
    "Suriname": "SUR",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Syria": "SYR",
    "São Tomé and Príncipe": "STP",
    
    # T
    "Taiwan Province of China": "TWN",
    "Tajikistan": "TJK",
    "Tanzania": "TZA",
    "Thailand": "THA",
    "Timor-Leste": "TLS",
    "Togo": "TGO",
    "Tonga": "TON",
    "Trinidad and Tobago": "TTO",
    "Tunisia": "TUN",
    "Turkmenistan": "TKM",
    "Tuvalu": "TUV",
    "Türkiye, Republic of": "TUR",
    
    # U
    "Uganda": "UGA",
    "Ukraine": "UKR",
    "United Arab Emirates": "ARE",
    "United Kingdom": "GBR",
    "United States": "USA",
    "Uruguay": "URY",
    "Uzbekistan": "UZB",
    
    # V
    "Vanuatu": "VUT",
    "Venezuela": "VEN",
    "Venezuela, RB": "VEN",
    "Vietnam": "VNM",
    
    # W
    "West Bank and Gaza": "PSE",
    
    # Y
    "Yemen": "YEM",
    "Yemen, Rep.": "YEM",
    
    # Z
    "Zambia": "ZMB",
    "Zimbabwe": "ZWE"
}

def normalize_name(name: str) -> str:
    """Normalise un nom de pays (minuscules, sans accents)."""
    name = name.lower().strip()
    # Supprimer les accents
    name = unicodedata.normalize('NFD', name)
    name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
    return name

def read_imf_csv(file_path: str) -> Tuple[List[int], List[List[str]]]:
    """Lit le fichier CSV IMF et retourne les années et les données parsées."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    if len(all_rows) < 3:
        raise ValueError("Fichier CSV invalide: pas assez de lignes")
    
    # Ligne 1: En-tête avec les années
    header = all_rows[0]
    years = [int(y.strip()) for y in header[1:] if y.strip().isdigit()]
    
    print(f"📅 Plage temporelle: {years[0]} - {years[-1]}")
    print(f"📊 Nombre d'années: {len(years)}")
    
    # Ligne 2 est vide, données commencent à la ligne 3
    data_rows = [row for row in all_rows[2:] if row and row[0].strip()]
    print(f"🌍 Nombre de pays: {len(data_rows)}")
    
    return years, data_rows

def parse_data_line(row: List[str], years: List[int]) -> List[Dict]:
    """Parse une ligne et retourne les enregistrements."""
    if not row or len(row) < 2:
        return []
    
    country_name = row[0].strip()
    values = row[1:]
    
    records = []
    
    for i, year in enumerate(years):
        if i >= len(values):
            continue
            
        value_str = values[i].strip()
        
        if value_str and value_str != 'no data':
            try:
                # Remplacer virgule par point pour conversion numérique
                value = float(value_str.replace(',', '.'))
                records.append({
                    'country': country_name,
                    'year': year,
                    'value': value
                })
            except ValueError:
                continue
    
    return records

def get_country_mapping(cursor) -> Dict[str, Dict]:
    """Récupère le mapping des pays depuis la base de données."""
    cursor.execute("SELECT id, iso3, name FROM country ORDER BY name")
    
    mapping = {}
    iso3_mapping = {}
    
    for row in cursor.fetchall():
        country_id, iso3, name = row
        normalized = normalize_name(name)
        
        mapping[normalized] = {
            'id': country_id,
            'iso3': iso3,
            'original_name': name
        }
        
        iso3_mapping[iso3] = {
            'id': country_id,
            'iso3': iso3,
            'original_name': name
        }
    
    return mapping, iso3_mapping

def find_country_id(imf_name: str, country_mapping: Dict, iso3_mapping: Dict) -> Optional[int]:
    """Trouve le country_id pour un nom de pays IMF."""
    # 1. Vérifier le mapping manuel
    if imf_name in COUNTRY_NAME_MAPPING:
        iso3 = COUNTRY_NAME_MAPPING[imf_name]
        if iso3 in iso3_mapping:
            return iso3_mapping[iso3]['id']
    
    # 2. Recherche par nom normalisé
    normalized_imf = normalize_name(imf_name.replace(',', ''))
    
    # Recherche exacte
    if normalized_imf in country_mapping:
        return country_mapping[normalized_imf]['id']
    
    # 3. Recherche partielle (contient)
    for name, info in country_mapping.items():
        if normalized_imf in name or name in normalized_imf:
            return info['id']
    
    return None

def get_indicator_id(cursor) -> int:
    """Récupère l'ID de l'indicateur GC.DOD.TOTL.GD.ZS."""
    cursor.execute("SELECT id FROM indicator WHERE code = 'GC.DOD.TOTL.GD.ZS'")
    result = cursor.fetchone()
    
    if not result:
        raise ValueError("Indicateur GC.DOD.TOTL.GD.ZS non trouvé dans la base")
    
    return result[0]

def update_indicator_source(cursor, indicator_id: int):
    """Met à jour la source de l'indicateur."""
    cursor.execute("""
        UPDATE indicator 
        SET source = 'World Bank + IMF (Central Government Debt)'
        WHERE id = %s
    """, (indicator_id,))
    
    print('✅ Source de l\'indicateur mise à jour')

def upsert_values(cursor, indicator_id: int, records: List[Dict], 
                  country_mapping: Dict, iso3_mapping: Dict) -> Dict[str, int]:
    """Insère ou met à jour les valeurs avec fusion (moyenne)."""
    inserted = 0
    updated = 0
    skipped = 0
    
    for record in records:
        country_id = find_country_id(record['country'], country_mapping, iso3_mapping)
        
        if not country_id:
            print(f"⚠️  Pays non trouvé: {record['country']}")
            skipped += 1
            continue
        
        # Vérifier si la valeur existe déjà
        cursor.execute("""
            SELECT value FROM indicator_value
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (country_id, indicator_id, record['year']))
        
        existing = cursor.fetchone()
        
        if existing:
            # Calculer la moyenne
            existing_value = existing[0]
            new_value = (existing_value + record['value']) / 2
            
            cursor.execute("""
                UPDATE indicator_value
                SET value = %s
                WHERE country_id = %s AND indicator_id = %s AND year = %s
            """, (new_value, country_id, indicator_id, record['year']))
            
            updated += 1
        else:
            # Insérer la nouvelle valeur
            cursor.execute("""
                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                VALUES (%s, %s, %s, %s)
            """, (country_id, indicator_id, record['year'], record['value']))
            
            inserted += 1
    
    return {'inserted': inserted, 'updated': updated, 'skipped': skipped}

def main():
    """Fonction principale."""
    print('🚀 Début de l\'import des données IMF de dette publique\n')
    
    # 1. Lire le fichier CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '../../Data/IRC/imf-dm-export-20260221.csv')
    print(f'📂 Lecture du fichier: {csv_path}')
    
    years, data_rows = read_imf_csv(csv_path)
    
    # 2. Parser toutes les lignes
    print('\n📊 Parsing des données...')
    all_records = []
    
    for row in data_rows:
        records = parse_data_line(row, years)
        all_records.extend(records)
    
    print(f'✅ {len(all_records)} valeurs parsées')
    
    # 3. Connexion à la base
    print('\n🔌 Connexion à la base de données...')
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 4. Récupérer l'ID de l'indicateur
        indicator_id = get_indicator_id(cursor)
        print(f'\n🎯 Indicateur ID: {indicator_id}')
        
        # 5. Récupérer le mapping des pays
        print('\n🗺️  Chargement du mapping des pays...')
        country_mapping, iso3_mapping = get_country_mapping(cursor)
        print(f'✅ {len(country_mapping)} pays dans la base')
        
        # 6. Import des valeurs
        print('\n💾 Import des valeurs dans la base...')
        stats = upsert_values(cursor, indicator_id, all_records, 
                             country_mapping, iso3_mapping)
        
        # 7. Mettre à jour la source
        update_indicator_source(cursor, indicator_id)
        
        # 8. Commit
        conn.commit()
        
        print('\n✅ Import terminé avec succès!')
        print(f'   📥 Nouvelles valeurs insérées: {stats["inserted"]}')
        print(f'   🔄 Valeurs mises à jour (moyenne): {stats["updated"]}')
        print(f'   ⏭️  Valeurs ignorées (pays non trouvé): {stats["skipped"]}')
        
    except Exception as e:
        conn.rollback()
        print(f'\n❌ Erreur lors de l\'import: {e}')
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Erreur fatale: {e}', file=sys.stderr)
        sys.exit(1)
