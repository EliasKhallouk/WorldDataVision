#!/usr/bin/env python3
"""
Import WIPO Patent Data into WorldDataVision database
Handles IP.PAT.RESD indicator (Patent applications by residents)

File format: Wide CSV with years as columns
- Origin, Origin (Code), Office, Type, 1980, 1981, ..., 2024
- Type = "Resident" only
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

# WIPO Indicator mapping
INDICATOR_CODE = 'IP.PAT.RESD'
INDICATOR_NAME = 'Patent applications, residents'

# WIPO ISO2 → ISO3 mapping (based on file content)
COUNTRY_MAPPING = {
    'AL': 'ALB', 'DZ': 'DZA', 'AD': 'AND', 'AO': 'AGO', 'AG': 'ATG',
    'AR': 'ARG', 'AM': 'ARM', 'AU': 'AUS', 'AT': 'AUT', 'AZ': 'AZE',
    'BS': 'BHS', 'BH': 'BHR', 'BD': 'BGD', 'BB': 'BRB', 'BY': 'BLR',
    'BE': 'BEL', 'BZ': 'BLZ', 'BJ': 'BEN', 'BT': 'BTN', 'BO': 'BOL',
    'BA': 'BIH', 'BW': 'BWA', 'BR': 'BRA', 'BN': 'BRN', 'BG': 'BGR',
    'BF': 'BFA', 'BI': 'BDI', 'KH': 'KHM', 'CM': 'CMR', 'CA': 'CAN',
    'CV': 'CPV', 'CF': 'CAF', 'TD': 'TCD', 'CL': 'CHL', 'CN': 'CHN',
    'CO': 'COL', 'KM': 'COM', 'CG': 'COG', 'CD': 'COD', 'CR': 'CRI',
    'CI': 'CIV', 'HR': 'HRV', 'CU': 'CUB', 'CY': 'CYP', 'CZ': 'CZE',
    'DK': 'DNK', 'DJ': 'DJI', 'DM': 'DMA', 'DO': 'DOM', 'EC': 'ECU',
    'EG': 'EGY', 'SV': 'SLV', 'GQ': 'GNQ', 'ER': 'ERI', 'EE': 'EST',
    'SZ': 'SWZ', 'ET': 'ETH', 'FJ': 'FJI', 'FI': 'FIN', 'FR': 'FRA',
    'GA': 'GAB', 'GM': 'GMB', 'GE': 'GEO', 'DE': 'DEU', 'GH': 'GHA',
    'GR': 'GRC', 'GD': 'GRD', 'GT': 'GTM', 'GN': 'GIN', 'GW': 'GNB',
    'GY': 'GUY', 'HT': 'HTI', 'HN': 'HND', 'HU': 'HUN', 'IS': 'ISL',
    'IN': 'IND', 'ID': 'IDN', 'IR': 'IRN', 'IQ': 'IRQ', 'IE': 'IRL',
    'IL': 'ISR', 'IT': 'ITA', 'JM': 'JAM', 'JP': 'JPN', 'JO': 'JOR',
    'KZ': 'KAZ', 'KE': 'KEN', 'KI': 'KIR', 'KP': 'PRK', 'KR': 'KOR',
    'KW': 'KWT', 'KG': 'KGZ', 'LA': 'LAO', 'LV': 'LVA', 'LB': 'LBN',
    'LS': 'LSO', 'LR': 'LBR', 'LY': 'LBY', 'LI': 'LIE', 'LT': 'LTU',
    'LU': 'LUX', 'MG': 'MDG', 'MW': 'MWI', 'MY': 'MYS', 'MV': 'MDV',
    'ML': 'MLI', 'MT': 'MLT', 'MH': 'MHL', 'MR': 'MRT', 'MU': 'MUS',
    'MX': 'MEX', 'FM': 'FSM', 'MD': 'MDA', 'MC': 'MCO', 'MN': 'MNG',
    'ME': 'MNE', 'MA': 'MAR', 'MZ': 'MOZ', 'MM': 'MMR', 'NA': 'NAM',
    'NR': 'NRU', 'NP': 'NPL', 'NL': 'NLD', 'NZ': 'NZL', 'NI': 'NIC',
    'NE': 'NER', 'NG': 'NGA', 'MK': 'MKD', 'NO': 'NOR', 'OM': 'OMN',
    'PK': 'PAK', 'PW': 'PLW', 'PA': 'PAN', 'PG': 'PNG', 'PY': 'PRY',
    'PE': 'PER', 'PH': 'PHL', 'PL': 'POL', 'PT': 'PRT', 'QA': 'QAT',
    'RO': 'ROU', 'RU': 'RUS', 'RW': 'RWA', 'KN': 'KNA', 'LC': 'LCA',
    'VC': 'VCT', 'WS': 'WSM', 'SM': 'SMR', 'ST': 'STP', 'SA': 'SAU',
    'SN': 'SEN', 'RS': 'SRB', 'SC': 'SYC', 'SL': 'SLE', 'SG': 'SGP',
    'SK': 'SVK', 'SI': 'SVN', 'SB': 'SLB', 'SO': 'SOM', 'ZA': 'ZAF',
    'SS': 'SSD', 'ES': 'ESP', 'LK': 'LKA', 'SD': 'SDN', 'SR': 'SUR',
    'SE': 'SWE', 'CH': 'CHE', 'SY': 'SYR', 'TJ': 'TJK', 'TZ': 'TZA',
    'TH': 'THA', 'TL': 'TLS', 'TG': 'TGO', 'TO': 'TON', 'TT': 'TTO',
    'TN': 'TUN', 'TR': 'TUR', 'TM': 'TKM', 'TV': 'TUV', 'UG': 'UGA',
    'UA': 'UKR', 'AE': 'ARE', 'GB': 'GBR', 'US': 'USA', 'UY': 'URY',
    'UZ': 'UZB', 'VU': 'VUT', 'VE': 'VEN', 'VN': 'VNM', 'YE': 'YEM',
    'ZM': 'ZMB', 'ZW': 'ZWE'
}


def read_wipo_csv(filepath):
    """
    Read WIPO CSV file and extract patent data by resident applicants
    Returns: list of (iso3, year, value) tuples
    """
    data = []
    skipped = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Skip first 6 header lines
        for _ in range(6):
            f.readline()
        
        reader = csv.DictReader(f)
        
        for row in reader:
            # Only process "Resident" type
            if row.get('Type') != 'Resident':
                continue
            
            # Get ISO2 code
            iso2 = row.get('Origin (Code)', '').strip()
            if not iso2 or iso2 not in COUNTRY_MAPPING:
                skipped += 1
                continue
            
            iso3 = COUNTRY_MAPPING[iso2]
            
            # Extract year columns (1980-2024)
            for year_str in range(1980, 2025):
                year_str = str(year_str)
                if year_str not in row:
                    continue
                
                value_str = row[year_str].strip()
                if not value_str or value_str == '':
                    continue
                
                try:
                    # WIPO uses integer counts
                    value = int(value_str.replace(',', ''))
                    year = int(year_str)
                    
                    # Filter years 1950-2035 (DB constraint)
                    if 1950 <= year <= 2035:
                        data.append((iso3, year, value))
                except (ValueError, AttributeError):
                    continue
    
    print(f"✓ Lecture WIPO: {len(data)} valeurs extraites")
    if skipped > 0:
        print(f"  ⚠ {skipped} pays ignorés (codes ISO2 non mappés)")
    
    return data


def get_country_mapping(conn):
    """Get mapping from ISO3 codes to country IDs"""
    cursor = conn.cursor()
    cursor.execute("SELECT iso3, id FROM country WHERE iso3 IS NOT NULL")
    mapping = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    return mapping


def upsert_values(conn, country_mapping, data):
    """
    Insert or update patent values in database
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
    
    for iso3, year, value in data:
        # Get id
        id = country_mapping.get(iso3)
        if not id:
            ignored += 1
            continue
        
        # Check if value exists
        cursor.execute("""
            SELECT value FROM indicator_value
            WHERE id = %s AND id = %s AND year = %s
        """, (id, id, year))
        
        existing = cursor.fetchone()
        
        if existing:
            # Average: (WB + WIPO) / 2
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
                print(f"  ⚠ Erreur insertion {iso3} {year}: {e}")
                ignored += 1
    
    # Update source in indicator table
    cursor.execute("""
        UPDATE indicator
        SET source = 'World Bank + WIPO (Patent Applications)'
        WHERE id = %s
    """, (id,))
    
    conn.commit()
    cursor.close()
    
    print(f"\n📊 RÉSULTATS IMPORT WIPO:")
    print(f"  ✓ {inserted} nouvelles valeurs insérées")
    print(f"  ✓ {updated} valeurs moyennées avec World Bank")
    print(f"  ⚠ {ignored} valeurs ignorées")
    total_processed = inserted + updated
    total_input = len(data)
    success_rate = (total_processed / total_input * 100) if total_input > 0 else 0
    print(f"  📈 Taux de succès: {success_rate:.1f}%")


def main():
    filepath = '/tmp/wipo_patents.csv'
    
    if not Path(filepath).exists():
        print(f"❌ Fichier introuvable: {filepath}")
        sys.exit(1)
    
    print("🚀 IMPORT WIPO PATENT DATA")
    print(f"📁 Fichier: {Path(filepath).name}")
    
    # Read WIPO data
    data = read_wipo_csv(filepath)
    
    if not data:
        print("❌ Aucune donnée extraite du fichier WIPO")
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
        print("\n✅ Import WIPO terminé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
