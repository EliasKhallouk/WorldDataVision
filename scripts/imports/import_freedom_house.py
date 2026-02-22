#!/usr/bin/env python3
"""
Import Freedom House data into WorldDataVision database.

Freedom House provides:
- PR (Political Rights): 1-7 scale (1=most free, 7=least free)
- CL (Civil Liberties): 1-7 scale (1=most free, 7=least free)
- Status: F (Free), PF (Partly Free), NF (Not Free)

Mapping to IRC indicators:
- PR → VA.EST (Voice and Accountability)
- CL → RL.EST (Rule of Law)
"""

import openpyxl
import psycopg2
import re

DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'postgres'
}

# Mapping des noms de pays Freedom House → ISO3
COUNTRY_MAPPING = {
    'United States': 'USA',
    'United Kingdom': 'GBR',
    'South Korea': 'KOR',
    'North Korea': 'PRK',
    'Congo (Brazzaville)': 'COG',
    'Congo (Kinshasa)': 'COD',
    'Cote d\'Ivoire': 'CIV',
    'Ivory Coast': 'CIV',
    'Czech Republic': 'CZE',
    'Czechia': 'CZE',
    'East Timor': 'TLS',
    'Timor-Leste': 'TLS',
    'Gambia': 'GMB',
    'The Gambia': 'GMB',
    'Kyrgyzstan': 'KGZ',
    'Laos': 'LAO',
    'Macedonia': 'MKD',
    'North Macedonia': 'MKD',
    'Micronesia': 'FSM',
    'Russia': 'RUS',
    'Syria': 'SYR',
    'Tanzania': 'TZA',
    'Turkey': 'TUR',
    'Turkiye': 'TUR',
    'Venezuela': 'VEN',
    'Vietnam': 'VNM',
    'Yemen': 'YEM',
}

def normalize_score(fh_score):
    """
    Convert Freedom House score (1-7, lower is better) to
    WGI-style score (higher is better, roughly -2.5 to +2.5).
    
    FH: 1 (best) → 7 (worst)
    WGI: +2.5 (best) → -2.5 (worst)
    """
    try:
        score = float(fh_score)
        # Linear transformation: 1→2.5, 7→-2.5
        # Formula: y = 3.33 - 0.833*x
        normalized = 3.33 - (0.833 * score)
        return round(normalized, 3)
    except (ValueError, TypeError):
        return None


def read_freedom_house_excel(filepath):
    """Parse Freedom House Excel file."""
    wb = openpyxl.load_workbook(filepath)
    sheet = wb['Country Ratings, Statuses ']
    
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)
    
    # Row 0: Survey editions
    # Row 1: Years under review
    # Row 2: PR, CL, Status headers
    # Row 3+: Country data
    
    years_row = data[1]
    years = []
    
    # Extract years from row 1 (every 4th column starting at index 1)
    for i in range(1, len(years_row), 4):
        year = years_row[i]
        if year and isinstance(year, int):
            years.append(year)
    
    print(f"📅 Années détectées: {len(years)} ({min(years)} - {max(years)})")
    
    # Parse country data (starting row 3)
    parsed_data = []
    
    for row_idx in range(3, len(data)):
        row = data[row_idx]
        country_name = row[0]
        
        if not country_name or country_name in [None, '']:
            continue
        
        # Extract PR and CL for each year
        for year_idx, year in enumerate(years):
            # Column structure: [Country, PR, CL, Status, PR, CL, Status, ...]
            # First year starts at column 1
            col_base = 1 + (year_idx * 4)
            
            if col_base + 1 < len(row):
                pr = row[col_base]  # Political Rights
                cl = row[col_base + 1]  # Civil Liberties
                
                if pr and pr != '-' and cl and cl != '-':
                    parsed_data.append({
                        'country': country_name,
                        'year': year,
                        'pr': pr,
                        'cl': cl
                    })
    
    print(f"📊 {len(parsed_data)} valeurs extraites")
    return parsed_data


def import_freedom_house(filepath):
    """Import Freedom House data into database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Get indicator IDs
        cursor.execute("SELECT id FROM indicator WHERE code = 'VA.EST'")
        va_id = cursor.fetchone()
        if not va_id:
            print("❌ VA.EST not found in database")
            return
        va_id = va_id[0]
        
        cursor.execute("SELECT id FROM indicator WHERE code = 'RL.EST'")
        rl_id = cursor.fetchone()
        if not rl_id:
            print("❌ RL.EST not found in database")
            return
        rl_id = rl_id[0]
        
        print(f"✅ Indicators: VA.EST={va_id}, RL.EST={rl_id}")
        
        # Get country mapping
        cursor.execute("SELECT name, iso3, id FROM country")
        country_db = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        # Also map by ISO3
        cursor.execute("SELECT iso3, id FROM country")
        iso3_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Parse Freedom House data
        fh_data = read_freedom_house_excel(filepath)
        
        va_inserted = 0
        va_updated = 0
        rl_inserted = 0
        rl_updated = 0
        skipped = 0
        
        for record in fh_data:
            country_name = record['country']
            year = record['year']
            pr_score = normalize_score(record['pr'])
            cl_score = normalize_score(record['cl'])
            
            if pr_score is None or cl_score is None:
                skipped += 1
                continue
            
            # Find country ID
            country_id = None
            
            # Try exact match
            if country_name in country_db:
                country_id = country_db[country_name][1]
            # Try mapping
            elif country_name in COUNTRY_MAPPING:
                iso3 = COUNTRY_MAPPING[country_name]
                if iso3 in iso3_map:
                    country_id = iso3_map[iso3]
            # Try partial match
            else:
                for db_name, (iso3, cid) in country_db.items():
                    if country_name.lower() in db_name.lower() or db_name.lower() in country_name.lower():
                        country_id = cid
                        break
            
            if not country_id:
                skipped += 1
                continue
            
            # Import VA.EST (Political Rights)
            cursor.execute("""
                SELECT value FROM indicator_value 
                WHERE indicator_id = %s AND country_id = %s AND year = %s
            """, (va_id, country_id, year))
            
            existing = cursor.fetchone()
            
            if existing:
                # Average with existing
                new_value = (existing[0] + pr_score) / 2
                cursor.execute("""
                    UPDATE indicator_value 
                    SET value = %s 
                    WHERE indicator_id = %s AND country_id = %s AND year = %s
                """, (new_value, va_id, country_id, year))
                va_updated += 1
            else:
                cursor.execute("""
                    INSERT INTO indicator_value (indicator_id, country_id, year, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (country_id, indicator_id, year) DO UPDATE
                    SET value = EXCLUDED.value
                """, (va_id, country_id, year, pr_score))
                va_inserted += 1
            
            # Import RL.EST (Civil Liberties)
            cursor.execute("""
                SELECT value FROM indicator_value 
                WHERE indicator_id = %s AND country_id = %s AND year = %s
            """, (rl_id, country_id, year))
            
            existing = cursor.fetchone()
            
            if existing:
                new_value = (existing[0] + cl_score) / 2
                cursor.execute("""
                    UPDATE indicator_value 
                    SET value = %s 
                    WHERE indicator_id = %s AND country_id = %s AND year = %s
                """, (new_value, rl_id, country_id, year))
                rl_updated += 1
            else:
                cursor.execute("""
                    INSERT INTO indicator_value (indicator_id, country_id, year, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (country_id, indicator_id, year) DO UPDATE
                    SET value = EXCLUDED.value
                """, (rl_id, country_id, year, cl_score))
                rl_inserted += 1
        
        conn.commit()
        
        print(f"\n{'='*70}")
        print(f"VA.EST (Political Rights):  {va_inserted} nouvelles + {va_updated} moyennées")
        print(f"RL.EST (Civil Liberties):   {rl_inserted} nouvelles + {rl_updated} moyennées")
        print(f"Ignorées: {skipped}")
        print(f"TOTAL: {va_inserted + rl_inserted} nouvelles + {va_updated + rl_updated} moyennées")
        print(f"{'='*70}")
        
        # Update sources
        for code, indicator_id in [('VA.EST', va_id), ('RL.EST', rl_id)]:
            cursor.execute("SELECT source FROM indicator WHERE id = %s", (indicator_id,))
            current_source = cursor.fetchone()[0] or ""
            
            if "Freedom House" not in current_source:
                new_source = current_source + " + Freedom House" if current_source else "Freedom House"
                cursor.execute("UPDATE indicator SET source = %s WHERE id = %s", (new_source, indicator_id))
                print(f"✅ {code} source: {new_source}")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("="*70)
    print("IMPORT FREEDOM HOUSE - Political Rights & Civil Liberties")
    print("="*70)
    print("\nSource: Freedom in the World 2024")
    print("Indicateurs: PR (Political Rights) → VA.EST")
    print("             CL (Civil Liberties) → RL.EST")
    print("Période: 1973-2024")
    print("Normalisation: FH 1-7 → WGI -2.5 à +2.5\n")
    
    import_freedom_house('/tmp/freedom_house_2024.xlsx')
    
    print("\n✅ Import terminé!")
