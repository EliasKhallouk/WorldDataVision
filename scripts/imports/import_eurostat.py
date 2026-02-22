#!/usr/bin/env python3
"""
Import données Eurostat pour catégorie 6 (Innovation)
Format: TSV avec années en colonnes
"""
import psycopg2
import os
import csv

# Fichiers Eurostat
EUROSTAT_DIR = "/home/elias/PROJECT/WorldDataVision/Data/Manuel/Eurostat"

DATASETS = {
    'eurostat_researchers.tsv': {
        'indicator': 'SP.POP.SCIE.RD.P6',
        'filter_unit': 'FTE',  # Full-time equivalent only
        'conversion': None
    },
    'eurostat_gerd.tsv': {
        'indicator': 'GB.XPD.RSDV.GD.ZS',
        'filter_unit': None,  # Accept all (will aggregate)
        'conversion': None
    },
    'eurostat_patents.tsv': {
        'indicator': 'IP.PAT.RESD',
        'filter_unit': None,  # Accept all
        'conversion': None
    }
}

# Mapping codes pays Eurostat → ISO3
EUROSTAT_TO_ISO3 = {
    'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP', 'CZ': 'CZE',
    'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA', 'DE': 'DEU', 'EL': 'GRC',
    'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA', 'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX',
    'MT': 'MLT', 'NL': 'NLD', 'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK',
    'SI': 'SVN', 'ES': 'ESP', 'SE': 'SWE',
    # AELE
    'IS': 'ISL', 'NO': 'NOR', 'CH': 'CHE', 'LI': 'LIE',
    # Candidats
    'TR': 'TUR', 'RS': 'SRB', 'ME': 'MNE', 'MK': 'MKD', 'AL': 'ALB',
    'BA': 'BIH', 'XK': 'XKX',  # Kosovo
    # UK post-Brexit
    'UK': 'GBR'
}

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user=os.getenv('USER', 'elias')
    )

def get_country_id(cursor, iso3):
    cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_id(cursor, code):
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (code,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_or_average(cursor, country_id, indicator_id, year, value):
    existing = value_exists(cursor, country_id, indicator_id, year)
    
    if existing is not None:
        averaged = (existing + value) / 2
        cursor.execute("""
            UPDATE indicator_value SET value = %s 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (averaged, country_id, indicator_id, year))
        return 'averaged'
    else:
        cursor.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (country_id, indicator_id, year, value))
        return 'new'

def update_source(cursor, indicator_code):
    # Vérifier la source actuelle
    cursor.execute("SELECT source FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    if result and 'Eurostat' not in result[0]:
        new_source = result[0] + ' + Eurostat'
        cursor.execute("""
            UPDATE indicator 
            SET source = %s
            WHERE code = %s
        """, (new_source, indicator_code))

def parse_eurostat_tsv(filepath, indicator_info):
    """Parse Eurostat TSV format"""
    print(f"\n📊 Parsing {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Première ligne = en-tête
        header = f.readline().strip().split('\t')
        
        # Première colonne = dimensions, puis colonnes d'années
        # Format: "freq,sectperf,prof_pos,sex,unit,geo\TIME_PERIOD" [TAB] "1980" [TAB] "1981" ...
        year_columns = header[1:]  # Skip first column (dimensions)
        years = []
        for col in year_columns:
            try:
                year = int(col.strip())
                years.append(year)
            except ValueError:
                pass
        
        if not years:
            print(f"   ❌ Aucune année trouvée dans l'en-tête")
            return [], []
        
        print(f"   📅 Années: {min(years)}-{max(years)} ({len(years)} colonnes)")
        
        # Lire les données
        data_rows = []
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            
            # Première colonne contient les dimensions séparées par virgules
            # Format varie selon dataset, mais le code pays est toujours le DERNIER élément
            dimensions = parts[0].split(',')
            if len(dimensions) < 2:
                continue
            
            geo_code = dimensions[-1].strip()  # Dernier élément = code pays
            
            # Filtrer dimensions spécifiques pour chercheurs (unit=FTE)
            if indicator_info.get('filter_unit') == 'FTE':
                # Pour researchers: freq,sectperf,prof_pos,sex,unit,geo
                if len(dimensions) >= 5:
                    unit = dimensions[4]
                    if unit != 'FTE':
                        continue
            
            # Valeurs annuelles (colonnes 2+)
            values = parts[1:]
            
            data_rows.append((geo_code, values))
        
        print(f"   📋 {len(data_rows)} lignes à traiter")
        return years, data_rows

def import_eurostat_file(cursor, filepath, indicator_info):
    """Import one Eurostat file"""
    indicator_code = indicator_info['indicator']
    
    indicator_id = get_indicator_id(cursor, indicator_code)
    if not indicator_id:
        print(f"   ❌ Indicateur {indicator_code} non trouvé")
        return
    
    years, data_rows = parse_eurostat_tsv(filepath, indicator_info)
    
    stats = {'new': 0, 'averaged': 0, 'skipped': 0, 'no_country': 0}
    
    for geo_code, values in data_rows:
        # Map to ISO3
        iso3 = EUROSTAT_TO_ISO3.get(geo_code)
        if not iso3:
            stats['no_country'] += 1
            continue
        
        country_id = get_country_id(cursor, iso3)
        if not country_id:
            stats['no_country'] += 1
            continue
        
        # Process each year
        for year, value_str in zip(years, values):
            # Eurostat uses ":" for missing values
            if not value_str or value_str.strip() in [':', '', 'n/a']:
                stats['skipped'] += 1
                continue
            
            try:
                # Clean value (peut avoir des espaces)
                value = float(value_str.strip().replace(' ', ''))
            except ValueError:
                stats['skipped'] += 1
                continue
            
            result = insert_or_average(cursor, country_id, indicator_id, year, value)
            stats[result] += 1
    
    # Update source
    update_source(cursor, indicator_code)
    
    total = stats['new'] + stats['averaged']
    print(f"   ✅ Total: {total} valeurs ({stats['new']} new + {stats['averaged']} averaged)")
    print(f"   ⚠️  Skipped: {stats['skipped']}, No country: {stats['no_country']}")

def main():
    print("=" * 70)
    print("IMPORT EUROSTAT - CATÉGORIE 6 (INNOVATION)")
    print("=" * 70)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    for filename, info in DATASETS.items():
        filepath = os.path.join(EUROSTAT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"\n❌ Fichier non trouvé: {filepath}")
            continue
        
        try:
            import_eurostat_file(cursor, filepath, info)
            conn.commit()
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("IMPORT TERMINÉ")
    print("=" * 70)

if __name__ == "__main__":
    main()
