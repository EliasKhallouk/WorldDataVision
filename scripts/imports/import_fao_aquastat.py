#!/usr/bin/env python3
"""
Import FAO AQUASTAT Water Data into WorldDataVision database
Handles ER.H2O.FWST.ZS indicator (Level of water stress)

File format: Long CSV
- m49,VariableGroup,Subgroup,Variable,Area,Year,Value,Unit,Symbol,IsAggregate
- Variable: "Agricultural water withdrawal as % of total renewable water resources"
"""

import psycopg2
import csv
import sys
from pathlib import Path

# Database connection parameters (peer authentication via Unix socket)
DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'postgres'
    # No password/host for peer authentication
}

# FAO Indicator mapping
INDICATOR_CODE = 'ER.H2O.FWST.ZS'
INDICATOR_NAME = 'Level of water stress: freshwater withdrawal as a proportion of available freshwater resources'

# FAO Country name → ISO3 mapping (extended version)
COUNTRY_NAME_MAPPING = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Andorra': 'AND',
    'Angola': 'AGO', 'Antigua and Barbuda': 'ATG', 'Argentina': 'ARG', 'Armenia': 'ARM',
    'Australia': 'AUS', 'Austria': 'AUT', 'Azerbaijan': 'AZE', 'Bahamas': 'BHS',
    'Bahrain': 'BHR', 'Bangladesh': 'BGD', 'Barbados': 'BRB', 'Belarus': 'BLR',
    'Belgium': 'BEL', 'Belize': 'BLZ', 'Benin': 'BEN', 'Bhutan': 'BTN',
    'Bolivia': 'BOL', 'Bolivia (Plurinational State of)': 'BOL',
    'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA', 'Brazil': 'BRA',
    'Brunei Darussalam': 'BRN', 'Bulgaria': 'BGR', 'Burkina Faso': 'BFA',
    'Burundi': 'BDI', 'Cabo Verde': 'CPV', 'Cambodia': 'KHM', 'Cameroon': 'CMR',
    'Canada': 'CAN', 'Central African Republic': 'CAF', 'Chad': 'TCD',
    'Chile': 'CHL', 'China': 'CHN', "China, Hong Kong SAR": 'HKG',
    "China, Macao SAR": 'MAC', 'China, mainland': 'CHN',
    'Colombia': 'COL', 'Comoros': 'COM', 'Congo': 'COG',
    'Democratic Republic of the Congo': 'COD', 'Costa Rica': 'CRI',
    "Côte d'Ivoire": 'CIV', 'Croatia': 'HRV', 'Cuba': 'CUB', 'Cyprus': 'CYP',
    'Czechia': 'CZE', 'Czech Republic': 'CZE', 'Denmark': 'DNK', 'Djibouti': 'DJI',
    'Dominica': 'DMA', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU', 'Egypt': 'EGY',
    'El Salvador': 'SLV', 'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI',
    'Estonia': 'EST', 'Eswatini': 'SWZ', 'Ethiopia': 'ETH', 'Fiji': 'FJI',
    'Finland': 'FIN', 'France': 'FRA', 'Gabon': 'GAB', 'Gambia': 'GMB',
    'Georgia': 'GEO', 'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC',
    'Grenada': 'GRD', 'Guatemala': 'GTM', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB',
    'Guyana': 'GUY', 'Haiti': 'HTI', 'Honduras': 'HND', 'Hungary': 'HUN',
    'Iceland': 'ISL', 'India': 'IND', 'Indonesia': 'IDN',
    'Iran': 'IRN', 'Iran (Islamic Republic of)': 'IRN',
    'Iraq': 'IRQ', 'Ireland': 'IRL', 'Israel': 'ISR', 'Italy': 'ITA',
    'Jamaica': 'JAM', 'Japan': 'JPN', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
    'Kenya': 'KEN', 'Kiribati': 'KIR',
    "Democratic People's Republic of Korea": 'PRK', 'North Korea': 'PRK',
    'Republic of Korea': 'KOR', 'South Korea': 'KOR', 'Korea': 'KOR',
    'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ',
    "Lao People's Democratic Republic": 'LAO', 'Laos': 'LAO',
    'Latvia': 'LVA', 'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR',
    'Libya': 'LBY', 'Liechtenstein': 'LIE', 'Lithuania': 'LTU', 'Luxembourg': 'LUX',
    'Madagascar': 'MDG', 'Malawi': 'MWI', 'Malaysia': 'MYS', 'Maldives': 'MDV',
    'Mali': 'MLI', 'Malta': 'MLT', 'Marshall Islands': 'MHL', 'Mauritania': 'MRT',
    'Mauritius': 'MUS', 'Mexico': 'MEX',
    'Micronesia (Federated States of)': 'FSM', 'Micronesia': 'FSM',
    'Republic of Moldova': 'MDA', 'Moldova': 'MDA',
    'Monaco': 'MCO', 'Mongolia': 'MNG', 'Montenegro': 'MNE', 'Morocco': 'MAR',
    'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Namibia': 'NAM', 'Nauru': 'NRU',
    'Nepal': 'NPL', 'Netherlands': 'NLD', 'New Zealand': 'NZL', 'Nicaragua': 'NIC',
    'Niger': 'NER', 'Nigeria': 'NGA', 'North Macedonia': 'MKD', 'Norway': 'NOR',
    'Oman': 'OMN', 'Pakistan': 'PAK', 'Palau': 'PLW', 'Panama': 'PAN',
    'Papua New Guinea': 'PNG', 'Paraguay': 'PRY', 'Peru': 'PER',
    'Philippines': 'PHL', 'Poland': 'POL', 'Portugal': 'PRT', 'Qatar': 'QAT',
    'Romania': 'ROU', 'Russian Federation': 'RUS', 'Russia': 'RUS',
    'Rwanda': 'RWA', 'Saint Kitts and Nevis': 'KNA', 'Saint Lucia': 'LCA',
    'Saint Vincent and the Grenadines': 'VCT', 'Samoa': 'WSM', 'San Marino': 'SMR',
    'Sao Tome and Principe': 'STP', 'Saudi Arabia': 'SAU', 'Senegal': 'SEN',
    'Serbia': 'SRB', 'Seychelles': 'SYC', 'Sierra Leone': 'SLE', 'Singapore': 'SGP',
    'Slovakia': 'SVK', 'Slovenia': 'SVN', 'Solomon Islands': 'SLB', 'Somalia': 'SOM',
    'South Africa': 'ZAF', 'South Sudan': 'SSD', 'Spain': 'ESP', 'Sri Lanka': 'LKA',
    'Sudan': 'SDN', 'Suriname': 'SUR', 'Sweden': 'SWE', 'Switzerland': 'CHE',
    'Syrian Arab Republic': 'SYR', 'Syria': 'SYR',
    'Tajikistan': 'TJK',
    'United Republic of Tanzania': 'TZA', 'Tanzania': 'TZA',
    'Thailand': 'THA', 'Timor-Leste': 'TLS', 'Togo': 'TGO', 'Tonga': 'TON',
    'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN', 'Turkey': 'TUR', 'Türkiye': 'TUR',
    'Turkmenistan': 'TKM', 'Tuvalu': 'TUV', 'Uganda': 'UGA', 'Ukraine': 'UKR',
    'United Arab Emirates': 'ARE', 'United Kingdom': 'GBR',
    'United States of America': 'USA', 'United States': 'USA', 'USA': 'USA',
    'Uruguay': 'URY', 'Uzbekistan': 'UZB', 'Vanuatu': 'VUT',
    'Venezuela': 'VEN', 'Venezuela (Bolivarian Republic of)': 'VEN',
    'Viet Nam': 'VNM', 'Vietnam': 'VNM', 'Yemen': 'YEM', 'Zambia': 'ZMB',
    'Zimbabwe': 'ZWE'
}


def read_fao_csv(filepath):
    """
    Read FAO AQUASTAT CSV file and extract water stress data
    Returns: list of (country_name, year, value) tuples
    """
    data = []
    skipped_aggregates = 0
    skipped_other = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Skip aggregates (IsAggregate = true)
            if row.get('IsAggregate', 'false').lower() == 'true':
                skipped_aggregates += 1
                continue
            
            # Get country name
            country_name = row.get('Area', '').strip()
            if not country_name:
                continue
            
            # Get variable - we want water withdrawal/stress related variables
            variable = row.get('Variable', '').strip()
            
            # Filter for relevant water stress variables
            # We want "Agricultural water withdrawal as % of total renewable water resources"
            # or similar water stress indicators
            if 'water' not in variable.lower() or 'withdrawal' not in variable.lower():
                skipped_other += 1
                continue
            
            # Get year and value
            year_str = row.get('Year', '').strip()
            value_str = row.get('Value', '').strip()
            
            if not year_str or not value_str:
                continue
            
            try:
                year = int(year_str)
                value = float(value_str)
                
                # Filter years 1950-2035 (DB constraint)
                if 1950 <= year <= 2035:
                    data.append((country_name, year, value))
            except (ValueError, AttributeError):
                continue
    
    print(f"✓ Lecture FAO AQUASTAT: {len(data)} valeurs extraites")
    if skipped_aggregates > 0:
        print(f"  ⚠ {skipped_aggregates} agrégats régionaux ignorés (normal)")
    if skipped_other > 0:
        print(f"  ⚠ {skipped_other} autres variables ignorées")
    
    return data


def get_country_mapping(conn):
    """Get mapping from country names to country IDs"""
    cursor = conn.cursor()
    cursor.execute("SELECT country_name, id, iso3 FROM country")
    
    # Create name → ID mapping
    mapping = {}
    for name, id, iso3 in cursor.fetchall():
        mapping[name] = id
        # Also map ISO3 if available
        if iso3:
            mapping[iso3] = id
    
    cursor.close()
    return mapping


def upsert_values(conn, country_mapping, data):
    """
    Insert or update FAO water values in database
    If value exists: average with existing value
    """
    cursor = conn.cursor()
    
    # Get indicator ID
    cursor.execute("""
        SELECT id FROM indicator WHERE code = %s
    """, (INDICATOR_CODE,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Indicateur {INDICATOR_CODE} introuvable dans la base")
        cursor.close()
        return
    
    id = result[0]
    
    inserted = 0
    updated = 0
    ignored = 0
    unmapped_countries = set()
    
    for country_name, year, value in data:
        # Try to map country name → ISO3 → id
        iso3 = COUNTRY_NAME_MAPPING.get(country_name)
        if not iso3:
            unmapped_countries.add(country_name)
            ignored += 1
            continue
        
        id = country_mapping.get(iso3)
        if not id:
            unmapped_countries.add(country_name)
            ignored += 1
            continue
        
        # Check if value exists
        cursor.execute("""
            SELECT value FROM indicator_value
            WHERE id = %s AND id = %s AND year = %s
        """, (id, id, year))
        
        existing = cursor.fetchone()
        
        if existing:
            # Average: (WB + FAO) / 2
            old_value = float(existing[0])
            new_value = (old_value + value) / 2
            
            cursor.execute("""
                UPDATE indicator_value
                SET value = %s
                WHERE id = %s AND id = %s AND year = %s
            """, (new_value, id, id, year))
            updated += 1
        else:
            # Insert new value
            try:
                cursor.execute("""
                    INSERT INTO indicator_value (id, id, year, value)
                    VALUES (%s, %s, %s, %s)
                """, (id, id, year, value))
                inserted += 1
            except Exception as e:
                print(f"  ⚠ Erreur insertion {country_name} {year}: {e}")
                ignored += 1
    
    # Update source in indicator table
    cursor.execute("""
        UPDATE indicator
        SET source = 'World Bank + FAO AQUASTAT (Water Stress)'
        WHERE id = %s
    """, (id,))
    
    conn.commit()
    cursor.close()
    
    print(f"\n📊 RÉSULTATS IMPORT FAO AQUASTAT:")
    print(f"  ✓ {inserted} nouvelles valeurs insérées")
    print(f"  ✓ {updated} valeurs moyennées avec World Bank")
    print(f"  ⚠ {ignored} valeurs ignorées")
    
    if unmapped_countries:
        print(f"\n⚠ Pays non mappés ({len(unmapped_countries)}):")
        for country in sorted(unmapped_countries)[:10]:
            print(f"    - {country}")
        if len(unmapped_countries) > 10:
            print(f"    ... et {len(unmapped_countries) - 10} autres")
    
    total_processed = inserted + updated
    total_input = len(data)
    success_rate = (total_processed / total_input * 100) if total_input > 0 else 0
    print(f"  📈 Taux de succès: {success_rate:.1f}%")


def main():
    filepath = '/tmp/fao_aquastat.csv'
    
    if not Path(filepath).exists():
        print(f"❌ Fichier introuvable: {filepath}")
        sys.exit(1)
    
    print("🚀 IMPORT FAO AQUASTAT WATER DATA")
    print(f"📁 Fichier: {Path(filepath).name}")
    
    # Read FAO data
    data = read_fao_csv(filepath)
    
    if not data:
        print("❌ Aucune donnée extraite du fichier FAO")
        sys.exit(1)
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connexion PostgreSQL établie")
        
        # Get country mapping
        country_mapping = get_country_mapping(conn)
        print(f"✓ {len(country_mapping)} pays trouvés dans la base")
        
        # Upsert values
        upsert_values(conn, country_mapping, data)
        
        conn.close()
        print("\n✅ Import FAO AQUASTAT terminé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
