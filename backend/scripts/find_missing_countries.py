#!/usr/bin/env python3
"""Identifie les pays IMF qui ne sont toujours pas trouvés"""

import csv
import psycopg2
from collections import Counter

# Lire le CSV IMF
csv_path = '../../Data/IRC/imf-dm-export-20260221.csv'
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Récupérer les pays de la DB via leurs codes ISO3
conn = psycopg2.connect(
    user='elias', host='localhost', database='worlddatavision', password='', port=5432
)
cursor = conn.cursor()
cursor.execute("SELECT iso3, name FROM country")
db_countries_by_iso3 = {row[0]: row[1] for row in cursor.fetchall()}
cursor.close()
conn.close()

# Mapping du script actuel (copié depuis import_imf_debt_data.py)
COUNTRY_NAME_MAPPING = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO",
    "Antigua and Barbuda": "ATG", "Argentina": "ARG", "Armenia": "ARM",
    "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
    "Bahamas, The": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD", "Barbados": "BRB",
    "Belarus": "BLR", "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN",
    "Bhutan": "BTN", "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
    "Botswana": "BWA", "Brazil": "BRA", "Brunei Darussalam": "BRN",
    "Bulgaria": "BGR", "Burkina Faso": "BFA", "Burundi": "BDI",
    "Cabo Verde": "CPV", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Central African Republic": "CAF", "Chad": "TCD", "Chile": "CHL",
    "China": "CHN", "Colombia": "COL", "Comoros": "COM",
    "Congo, Democratic Republic of the": "COD", "Congo, Dem. Rep.": "COD",
    "Congo, Republic of ": "COG", "Congo, Rep.": "COG",
    "Costa Rica": "CRI", "Croatia": "HRV", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Côte d'Ivoire": "CIV", "Cote d'Ivoire": "CIV",
    "Denmark": "DNK", "Djibouti": "DJI", "Dominica": "DMA",
    "Dominican Republic": "DOM", "Ecuador": "ECU", "Egypt": "EGY",
    "Egypt, Arab Rep.": "EGY", "El Salvador": "SLV", "Equatorial Guinea": "GNQ",
    "Estonia": "EST", "Eswatini": "SWZ", "Ethiopia": "ETH",
    "Fiji": "FJI", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Gambia, The": "GMB", "Georgia": "GEO",
    "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC",
    "Grenada": "GRD", "Guatemala": "GTM", "Guinea": "GIN",
    "Guinea-Bissau": "GNB", "Guyana": "GUY", "Haiti": "HTI",
    "Honduras": "HND", "Hungary": "HUN", "Iceland": "ISL",
    "India": "IND", "Indonesia": "IDN", "Iran, Islamic Rep.": "IRN",
    "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR",
    "Italy": "ITA", "Jamaica": "JAM", "Japan": "JPN",
    "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN",
    "Korea, Rep.": "KOR", "Kosovo": "XKX", "Kuwait": "KWT",
    "Kyrgyz Republic": "KGZ", "Lao PDR": "LAO", "Latvia": "LVA",
    "Lebanon": "LBN", "Lesotho": "LSO", "Liberia": "LBR",
    "Libya": "LBY", "Lithuania": "LTU", "Luxembourg": "LUX",
    "Madagascar": "MDG", "Malawi": "MWI", "Malaysia": "MYS",
    "Maldives": "MDV", "Mali": "MLI", "Malta": "MLT",
    "Mauritania": "MRT", "Mauritius": "MUS", "Mexico": "MEX",
    "Micronesia, Fed. Sts.": "FSM", "Moldova": "MDA", "Mongolia": "MNG",
    "Montenegro": "MNE", "Morocco": "MAR", "Mozambique": "MOZ",
    "Myanmar": "MMR", "Namibia": "NAM", "Nepal": "NPL",
    "Netherlands": "NLD", "New Zealand": "NZL", "Nicaragua": "NIC",
    "Niger": "NER", "Nigeria": "NGA", "North Macedonia": "MKD",
    "Norway": "NOR", "Oman": "OMN", "Pakistan": "PAK",
    "Panama": "PAN", "Papua New Guinea": "PNG", "Paraguay": "PRY",
    "Peru": "PER", "Philippines": "PHL", "Poland": "POL",
    "Portugal": "PRT", "Qatar": "QAT", "Romania": "ROU",
    "Russian Federation": "RUS", "Rwanda": "RWA", "Samoa": "WSM",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Seychelles": "SYC", "Sierra Leone": "SLE", "Singapore": "SGP",
    "Slovak Republic": "SVK", "Slovenia": "SVN", "Solomon Islands": "SLB",
    "South Africa": "ZAF", "South Sudan": "SSD", "Spain": "ESP",
    "Sri Lanka": "LKA", "St. Kitts and Nevis": "KNA", "St. Lucia": "LCA",
    "St. Vincent and the Grenadines": "VCT", "Sudan": "SDN", "Suriname": "SUR",
    "Sweden": "SWE", "Switzerland": "CHE", "Syrian Arab Republic": "SYR",
    "São Tomé and Príncipe": "STP", "Tajikistan": "TJK", "Tanzania": "TZA",
    "Thailand": "THA", "Timor-Leste": "TLS", "Togo": "TGO",
    "Tonga": "TON", "Trinidad and Tobago": "TTO", "Tunisia": "TUN",
    "Türkiye": "TUR", "Turkmenistan": "TKM", "Uganda": "UGA",
    "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA", "Uruguay": "URY", "Uzbekistan": "UZB",
    "Vanuatu": "VUT", "Venezuela, RB": "VEN", "Vietnam": "VNM",
    "West Bank and Gaza": "PSE", "Yemen, Rep.": "YEM", "Zambia": "ZMB",
    "Zimbabwe": "ZWE",
}

# Analyser tous les pays IMF
not_found = []
for row in rows[2:]:
    if not row or not row[0].strip():
        continue
    
    imf_name = row[0].strip()
    
    # Vérifier si mappé
    if imf_name in COUNTRY_NAME_MAPPING:
        iso3 = COUNTRY_NAME_MAPPING[imf_name]
        if iso3 not in db_countries_by_iso3:
            not_found.append(imf_name)
    else:
        not_found.append(imf_name)

print(f"Total pays IMF: {len(rows) - 2}")
print(f"Pays NON trouvés: {len(not_found)}\n")

if not_found:
    print("=" * 80)
    print("PAYS À AJOUTER AU MAPPING:")
    print("=" * 80)
    for country in sorted(set(not_found)):
        print(f'    "{country}": "???",')
