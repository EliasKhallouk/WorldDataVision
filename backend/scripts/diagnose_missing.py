#!/usr/bin/env python3
"""Diagnostic détaillé : quels pays sont ignorés et pourquoi."""

import csv
import psycopg2
from collections import defaultdict

# Fichier CSV
csv_file = '/home/elias/PROJECT/WorldDataVision/Data/IRC/imf-dm-export-20260221.csv'

# DB Config
DB_CONFIG = {
    'user': 'elias',
    'host': 'localhost',
    'database': 'worlddatavision',
    'password': 'MaBaseDeDonnee',
    'port': 5432
}

# Mapping (copie du script principal)
COUNTRY_NAME_MAPPING = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO",
    "Antigua and Barbuda": "ATG", "Argentina": "ARG", "Armenia": "ARM",
    "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
    "Bahamas, The": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD",
    "Barbados": "BRB", "Belarus": "BLR", "Belgium": "BEL", "Belize": "BLZ",
    "Benin": "BEN", "Bhutan": "BTN", "Bolivia": "BOL",
    "Bosnia and Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Brunei Darussalam": "BRN", "Bulgaria": "BGR", "Burkina Faso": "BFA",
    "Burundi": "BDI", "Cabo Verde": "CPV", "Cambodia": "KHM",
    "Cameroon": "CMR", "Canada": "CAN", "Central African Republic": "CAF",
    "Chad": "TCD", "Chile": "CHL", "China": "CHN", "Colombia": "COL",
    "Comoros": "COM", "Congo, Democratic Republic of the": "COD",
    "Congo, Dem. Rep.": "COD", "Congo, Republic of ": "COG",
    "Congo, Rep.": "COG", "Costa Rica": "CRI", "Croatia": "HRV",
    "Cyprus": "CYP", "Czech Republic": "CZE", "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV", "Denmark": "DNK", "Djibouti": "DJI",
    "Dominica": "DMA", "Dominican Republic": "DOM", "Ecuador": "ECU",
    "Egypt": "EGY", "Egypt, Arab Rep.": "EGY", "El Salvador": "SLV",
    "Equatorial Guinea": "GNQ", "Estonia": "EST", "Eswatini": "SWZ",
    "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Gambia, The": "GMB", "Georgia": "GEO",
    "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC", "Grenada": "GRD",
    "Guatemala": "GTM", "Guinea": "GIN", "Guinea-Bissau": "GNB",
    "Guyana": "GUY", "Haiti": "HTI", "Honduras": "HND",
    "Hong Kong SAR": "HKG", "Hungary": "HUN", "Iceland": "ISL",
    "India": "IND", "Indonesia": "IDN", "Iran": "IRN",
    "Iran, Islamic Rep.": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Jamaica": "JAM", "Japan": "JPN",
    "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN", "Kiribati": "KIR",
    "Korea": "KOR", "Korea, Republic of": "KOR", "Korea, Rep.": "KOR",
    "Kosovo": "XKX", "Kuwait": "KWT", "Kyrgyz Republic": "KGZ",
    "Lao P.D.R.": "LAO", "Lao PDR": "LAO", "Latvia": "LVA",
    "Lebanon": "LBN", "Lesotho": "LSO", "Liberia": "LBR", "Libya": "LBY",
    "Lithuania": "LTU", "Luxembourg": "LUX", "Macao SAR": "MAC",
    "Madagascar": "MDG", "Malawi": "MWI", "Malaysia": "MYS",
    "Maldives": "MDV", "Mali": "MLI", "Malta": "MLT",
    "Marshall Islands": "MHL", "Mauritania": "MRT", "Mauritius": "MUS",
    "Mexico": "MEX", "Micronesia": "FSM", "Micronesia, Fed. Sts.": "FSM",
    "Moldova": "MDA", "Mongolia": "MNG", "Montenegro": "MNE",
    "Morocco": "MAR", "Mozambique": "MOZ", "Myanmar": "MMR",
    "Namibia": "NAM", "Nauru": "NRU", "Nepal": "NPL",
    "Netherlands": "NLD", "New Zealand": "NZL", "Nicaragua": "NIC",
    "Niger": "NER", "Nigeria": "NGA", "North Macedonia": "MKD",
    "North Macedonia ": "MKD", "Norway": "NOR", "Oman": "OMN",
    "Pakistan": "PAK", "Palau": "PLW", "Panama": "PAN",
    "Papua New Guinea": "PNG", "Paraguay": "PRY", "Peru": "PER",
    "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
    "Qatar": "QAT", "Romania": "ROU", "Russia": "RUS",
    "Russian Federation": "RUS", "Rwanda": "RWA", "Samoa": "WSM",
    "San Marino": "SMR", "Saudi Arabia": "SAU", "Senegal": "SEN",
    "Serbia": "SRB", "Seychelles": "SYC", "Sierra Leone": "SLE",
    "Singapore": "SGP", "Slovak Republic": "SVK", "Slovenia": "SVN",
    "Solomon Islands": "SLB", "Somalia": "SOM", "South Africa": "ZAF",
    "South Sudan": "SSD", "Spain": "ESP", "Sri Lanka": "LKA",
    "St. Kitts and Nevis": "KNA", "St. Lucia": "LCA",
    "St. Vincent and the Grenadines": "VCT", "Sudan": "SDN",
    "Suriname": "SUR", "Sweden": "SWE", "Switzerland": "CHE",
    "Syria": "SYR", "São Tomé and Príncipe": "STP",
    "Taiwan Province of China": "TWN", "Tajikistan": "TJK",
    "Tanzania": "TZA", "Thailand": "THA", "Timor-Leste": "TLS",
    "Togo": "TGO", "Tonga": "TON", "Trinidad and Tobago": "TTO",
    "Tunisia": "TUN", "Turkmenistan": "TKM", "Tuvalu": "TUV",
    "Türkiye, Republic of": "TUR", "Uganda": "UGA", "Ukraine": "UKR",
    "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA", "Uruguay": "URY", "Uzbekistan": "UZB",
    "Vanuatu": "VUT", "Venezuela": "VEN", "Venezuela, RB": "VEN",
    "Vietnam": "VNM", "West Bank and Gaza": "PSE", "Yemen": "YEM",
    "Yemen, Rep.": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE"
}

# Charger tous les pays de la DB
print("🔍 Connexion à la base de données...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT iso3, name FROM country ORDER BY iso3")
db_countries = {row[0]: row[1] for row in cur.fetchall()}
print(f"   Base de données: {len(db_countries)} pays")

# Lire le CSV
print("\n📄 Lecture du CSV IMF...")
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Analyser les problèmes
print("\n🔍 ANALYSE DES PAYS IGNORÉS:\n")

missing_in_mapping = []
missing_in_db = []
found_ok = []

for row in rows[2:]:  # Skip header
    if not row or not row[0] or row[0].startswith('©'):
        continue
    
    country_name = row[0]
    
    # Compter les valeurs non-vides
    data_values = [v for v in row[1:] if v and v != 'no data']
    if not data_values:
        continue
    
    # Vérifier mapping
    if country_name not in COUNTRY_NAME_MAPPING:
        missing_in_mapping.append((country_name, len(data_values)))
    else:
        iso3 = COUNTRY_NAME_MAPPING[country_name]
        if iso3 not in db_countries:
            missing_in_db.append((country_name, iso3, len(data_values)))
        else:
            found_ok.append((country_name, iso3))

if missing_in_mapping:
    print(f"❌ Pays NON MAPPÉS ({len(missing_in_mapping)}):")
    for name, count in sorted(missing_in_mapping):
        print(f"   '{name}' → {count} valeurs")

if missing_in_db:
    print(f"\n❌ Codes ISO3 ABSENTS de la DB ({len(missing_in_db)}):")
    for name, iso3, count in sorted(missing_in_db):
        print(f"   '{name}' → {iso3} ({count} valeurs)")

print(f"\n✅ Pays correctement mappés: {len(found_ok)}")

# Suggestions de codes ISO3 similaires
if missing_in_db:
    print("\n💡 CODES ISO3 DISPONIBLES DANS LA DB (pour référence):")
    all_iso3 = sorted(db_countries.keys())
    print(f"   Total: {len(all_iso3)} codes")
    print(f"   Exemples: {', '.join(all_iso3[:20])}")

cur.close()
conn.close()

print("\n" + "="*60)
print(f"RÉSUMÉ: {len(missing_in_mapping)} non mappés + {len(missing_in_db)} absents DB")
print("="*60)
