#!/usr/bin/env python3
"""
Import UNESCO UIS data to improve IRC indicators coverage
Imports: Literacy, Researchers, R&D Expenditure
"""
import psycopg2
import csv
import sys

# UNESCO indicator code → IRC indicator code mapping
UNESCO_TO_IRC = {
    'ILLPOP.AG15T99': 'SE.ADT.LITR.ZS',      # Literacy rate, adult total (% of people ages 15 and above)
    'RESDEN.INHAB.TFTE': 'SP.POP.SCIE.RD.P6', # Researchers in R&D (per million people)
    'EXPGDP.TOT': 'GB.XPD.RSDV.GD.ZS'         # Research and development expenditure (% of GDP)
}

# UNESCO geoUnit codes → ISO3 mapping (extended)
COUNTRY_MAPPING = {
    'ABW': 'ABW', 'AFG': 'AFG', 'AGO': 'AGO', 'AIA': 'AIA', 'ALB': 'ALB', 'AND': 'AND',
    'ARE': 'ARE', 'ARG': 'ARG', 'ARM': 'ARM', 'ASM': 'ASM', 'ATG': 'ATG', 'AUS': 'AUS',
    'AUT': 'AUT', 'AZE': 'AZE', 'BDI': 'BDI', 'BEL': 'BEL', 'BEN': 'BEN', 'BFA': 'BFA',
    'BGD': 'BGD', 'BGR': 'BGR', 'BHR': 'BHR', 'BHS': 'BHS', 'BIH': 'BIH', 'BLR': 'BLR',
    'BLZ': 'BLZ', 'BMU': 'BMU', 'BOL': 'BOL', 'BRA': 'BRA', 'BRB': 'BRB', 'BRN': 'BRN',
    'BTN': 'BTN', 'BWA': 'BWA', 'CAF': 'CAF', 'CAN': 'CAN', 'CHE': 'CHE', 'CHL': 'CHL',
    'CHN': 'CHN', 'CIV': 'CIV', 'CMR': 'CMR', 'COD': 'COD', 'COG': 'COG', 'COK': 'COK',
    'COL': 'COL', 'COM': 'COM', 'CPV': 'CPV', 'CRI': 'CRI', 'CUB': 'CUB', 'CUW': 'CUW',
    'CYM': 'CYM', 'CYP': 'CYP', 'CZE': 'CZE', 'DEU': 'DEU', 'DJI': 'DJI', 'DMA': 'DMA',
    'DNK': 'DNK', 'DOM': 'DOM', 'DZA': 'DZA', 'ECU': 'ECU', 'EGY': 'EGY', 'ERI': 'ERI',
    'ESP': 'ESP', 'EST': 'EST', 'ETH': 'ETH', 'FIN': 'FIN', 'FJI': 'FJI', 'FRA': 'FRA',
    'FRO': 'FRO', 'FSM': 'FSM', 'GAB': 'GAB', 'GBR': 'GBR', 'GEO': 'GEO', 'GHA': 'GHA',
    'GIB': 'GIB', 'GIN': 'GIN', 'GMB': 'GMB', 'GNB': 'GNB', 'GNQ': 'GNQ', 'GRC': 'GRC',
    'GRD': 'GRD', 'GRL': 'GRL', 'GTM': 'GTM', 'GUM': 'GUM', 'GUY': 'GUY', 'HKG': 'HKG',
    'HND': 'HND', 'HRV': 'HRV', 'HTI': 'HTI', 'HUN': 'HUN', 'IDN': 'IDN', 'IND': 'IND',
    'IRL': 'IRL', 'IRN': 'IRN', 'IRQ': 'IRQ', 'ISL': 'ISL', 'ISR': 'ISR', 'ITA': 'ITA',
    'JAM': 'JAM', 'JOR': 'JOR', 'JPN': 'JPN', 'KAZ': 'KAZ', 'KEN': 'KEN', 'KGZ': 'KGZ',
    'KHM': 'KHM', 'KIR': 'KIR', 'KNA': 'KNA', 'KOR': 'KOR', 'KWT': 'KWT', 'LAO': 'LAO',
    'LBN': 'LBN', 'LBR': 'LBR', 'LBY': 'LBY', 'LCA': 'LCA', 'LIE': 'LIE', 'LKA': 'LKA',
    'LSO': 'LSO', 'LTU': 'LTU', 'LUX': 'LUX', 'LVA': 'LVA', 'MAC': 'MAC', 'MAR': 'MAR',
    'MCO': 'MCO', 'MDA': 'MDA', 'MDG': 'MDG', 'MDV': 'MDV', 'MEX': 'MEX', 'MHL': 'MHL',
    'MKD': 'MKD', 'MLI': 'MLI', 'MLT': 'MLT', 'MMR': 'MMR', 'MNE': 'MNE', 'MNG': 'MNG',
    'MNP': 'MNP', 'MOZ': 'MOZ', 'MRT': 'MRT', 'MSR': 'MSR', 'MUS': 'MUS', 'MWI': 'MWI',
    'MYS': 'MYS', 'NAM': 'NAM', 'NCL': 'NCL', 'NER': 'NER', 'NGA': 'NGA', 'NIC': 'NIC',
    'NIU': 'NIU', 'NLD': 'NLD', 'NOR': 'NOR', 'NPL': 'NPL', 'NRU': 'NRU', 'NZL': 'NZL',
    'OMN': 'OMN', 'PAK': 'PAK', 'PAN': 'PAN', 'PER': 'PER', 'PHL': 'PHL', 'PLW': 'PLW',
    'PNG': 'PNG', 'POL': 'POL', 'PRI': 'PRI', 'PRK': 'PRK', 'PRT': 'PRT', 'PRY': 'PRY',
    'PSE': 'PSE', 'PYF': 'PYF', 'QAT': 'QAT', 'ROU': 'ROU', 'RUS': 'RUS', 'RWA': 'RWA',
    'SAU': 'SAU', 'SDN': 'SDN', 'SEN': 'SEN', 'SGP': 'SGP', 'SLB': 'SLB', 'SLE': 'SLE',
    'SLV': 'SLV', 'SMR': 'SMR', 'SOM': 'SOM', 'SRB': 'SRB', 'SSD': 'SSD', 'STP': 'STP',
    'SUR': 'SUR', 'SVK': 'SVK', 'SVN': 'SVN', 'SWE': 'SWE', 'SWZ': 'SWZ', 'SXM': 'SXM',
    'SYC': 'SYC', 'SYR': 'SYR', 'TCA': 'TCA', 'TCD': 'TCD', 'TGO': 'TGO', 'THA': 'THA',
    'TJK': 'TJK', 'TKL': 'TKL', 'TKM': 'TKM', 'TLS': 'TLS', 'TON': 'TON', 'TTO': 'TTO',
    'TUN': 'TUN', 'TUR': 'TUR', 'TUV': 'TUV', 'TWN': 'TWN', 'TZA': 'TZA', 'UGA': 'UGA',
    'UKR': 'UKR', 'URY': 'URY', 'USA': 'USA', 'UZB': 'UZB', 'VCT': 'VCT', 'VEN': 'VEN',
    'VGB': 'VGB', 'VIR': 'VIR', 'VNM': 'VNM', 'VUT': 'VUT', 'WSM': 'WSM', 'YEM': 'YEM',
    'ZAF': 'ZAF', 'ZMB': 'ZMB', 'ZWE': 'ZWE'
}

# Input files
FILES = [
    ('/home/elias/PROJECT/WorldDataVision/Data/Manuel/indicator-data-export_ILLPOP.AG15T99/data.csv', 'ILLPOP.AG15T99'),
    ('/home/elias/PROJECT/WorldDataVision/Data/Manuel/indicator-data-export_RESDEN.INHAB.TFTE/data.csv', 'RESDEN.INHAB.TFTE'),
    ('/home/elias/PROJECT/WorldDataVision/Data/Manuel/indicator-data-export_EXPGDP.TOT/data.csv', 'EXPGDP.TOT')
]

def connect_db():
    """Connect to PostgreSQL database"""
    import os
    # Use peer authentication (current user)
    return psycopg2.connect(
        dbname="worlddatavision",
        user=os.getenv('USER', 'postgres')
    )

def get_country_id(cursor, iso3_code):
    """Get country_id from ISO3 code"""
    cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_id(cursor, indicator_code):
    """Get indicator_id from indicator code"""
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_year_id(cursor, year):
    """Get year value (which is the year itself in year_table)"""
    cursor.execute("SELECT value FROM year_table WHERE value = %s", (year,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    """Check if value already exists"""
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_or_average(cursor, country_id, indicator_id, year, new_value):
    """Insert new value or average with existing"""
    existing = value_exists(cursor, country_id, indicator_id, year)
    
    if existing is not None:
        # Average with existing value
        averaged_value = (existing + new_value) / 2
        cursor.execute("""
            UPDATE indicator_value 
            SET value = %s 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (averaged_value, country_id, indicator_id, year))
        return 'averaged'
    else:
        # Insert new value
        cursor.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (country_id, indicator_id, year, new_value))
        return 'new'

def update_indicator_source(cursor, indicator_code):
    """Update indicator source to include UNESCO UIS"""
    cursor.execute("""
        UPDATE indicator 
        SET source = 'World Bank + UNESCO UIS'
        WHERE code = %s
    """, (indicator_code,))

def import_unesco_file(cursor, filepath, unesco_code):
    """Import one UNESCO data file"""
    irc_code = UNESCO_TO_IRC.get(unesco_code)
    if not irc_code:
        print(f"❌ No IRC mapping for UNESCO code {unesco_code}")
        return
    
    indicator_id = get_indicator_id(cursor, irc_code)
    if not indicator_id:
        print(f"❌ Indicator {irc_code} not found in database")
        return
    
    print(f"\n📊 Importing {unesco_code} → {irc_code}")
    print(f"   File: {filepath}")
    
    stats = {'new': 0, 'averaged': 0, 'skipped': 0, 'unmapped_countries': set()}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse row
            geo_unit = row['geoUnit']
            year = int(row['year'])
            value_str = row['value']
            
            # Skip empty values
            if not value_str or value_str.strip() == '':
                stats['skipped'] += 1
                continue
            
            try:
                value = float(value_str)
            except ValueError:
                stats['skipped'] += 1
                continue
            
            # Map country
            iso3 = COUNTRY_MAPPING.get(geo_unit)
            if not iso3:
                stats['unmapped_countries'].add(geo_unit)
                stats['skipped'] += 1
                continue
            
            country_id = get_country_id(cursor, iso3)
            if not country_id:
                stats['unmapped_countries'].add(geo_unit)
                stats['skipped'] += 1
                continue
            
            # Verify year exists in year_table
            year_value = get_year_id(cursor, year)
            if not year_value:
                stats['skipped'] += 1
                continue
            
            # Insert or average (use year directly)
            result = insert_or_average(cursor, country_id, indicator_id, year, value)
            stats[result] += 1
    
    # Update source
    update_indicator_source(cursor, irc_code)
    
    # Print stats
    total = stats['new'] + stats['averaged']
    print(f"   ✅ Total: {total} values ({stats['new']} new + {stats['averaged']} averaged)")
    print(f"   ⚠️  Skipped: {stats['skipped']}")
    if stats['unmapped_countries']:
        print(f"   ⚠️  Unmapped countries: {', '.join(sorted(stats['unmapped_countries']))}")

def main():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        print("=" * 70)
        print("UNESCO UIS DATA IMPORT")
        print("=" * 70)
        
        total_stats = {'new': 0, 'averaged': 0, 'skipped': 0}
        
        for filepath, unesco_code in FILES:
            try:
                import_unesco_file(cursor, filepath, unesco_code)
                # Commit after each file
                conn.commit()
            except Exception as e:
                print(f"❌ Error importing {unesco_code}: {e}")
                conn.rollback()
                continue
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
