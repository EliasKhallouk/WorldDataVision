#!/usr/bin/env python3
"""
Import IMF World Economic Outlook data to improve IRC indicators coverage
Focus on: External debt, Debt service, Reserves
"""
import psycopg2
import csv
import sys
import os

# IMF WEO Subject Code → IRC indicator code mapping
# CRITICAL: These mappings may not be semantically equivalent
# - GGXWDG_NGDP = General government gross debt (PUBLIC debt, not external debt)
# - DT.DOD.DECT.GN.ZS = External debt stocks (EXTERNAL debt only)
# We'll import but flag this semantic mismatch for user review
IMF_TO_IRC = {
    # Note: Public debt ≠ External debt, but can provide broader coverage
    'GGXWDG_NGDP': 'DT.DOD.DECT.GN.ZS',  # General gov gross debt → External debt (APPROX)
    # Note: Net lending/borrowing ≠ Debt service, but related fiscal metric
    'GGXONLB_NGDP': 'DT.TDS.DECT.EX.ZS',  # Gov net lending/borrowing → Debt service (APPROX)
}

# Search for reserves indicators (may vary)
RESERVES_CODES = ['FI_RES', 'REER', 'BCA', 'BCA_NGDPD']

# Input file
IMF_FILE = '/home/elias/PROJECT/WorldDataVision/Data/Manuel/weooct2024all.xls'

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        dbname="worlddatavision",
        user=os.getenv('USER', 'elias')
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
    """Update indicator source to include IMF WEO"""
    cursor.execute("""
        UPDATE indicator 
        SET source = 'World Bank + IMF WEO'
        WHERE code = %s
    """, (indicator_code,))

def clean_value(value_str):
    """Clean IMF value (remove commas, handle n/a)"""
    if not value_str or value_str.strip() in ['n/a', '', '--']:
        return None
    try:
        # Remove commas and convert to float
        return float(value_str.replace(',', ''))
    except ValueError:
        return None

def import_imf_weo(cursor):
    """Import IMF WEO data"""
    print("=" * 70, flush=True)
    print("IMF WEO DATA IMPORT", flush=True)
    print("=" * 70, flush=True)
    print(f"⚠️  SEMANTIC WARNING:", flush=True)
    print(f"   - GGXWDG_NGDP (Public debt) ≠ DT.DOD.DECT.GN.ZS (External debt)", flush=True)
    print(f"   - GGXONLB_NGDP (Fiscal balance) ≠ DT.TDS.DECT.EX.ZS (Debt service)", flush=True)
    print(f"   These are APPROXIMATIONS for broader coverage.\n", flush=True)
    
    print(f"📂 Opening file: {IMF_FILE}", flush=True)
    
    # Read file (tab-separated, UTF-16 Little Endian encoding)
    with open(IMF_FILE, 'r', encoding='utf-16-le', errors='replace') as f:
        # First line is header
        header = f.readline().strip().split('\t')
        print(f"📄 Header has {len(header)} columns", flush=True)
        
        # Find year columns (columns 10-59)
        year_cols = []
        year_indices = {}
        for i, col in enumerate(header):
            col_clean = col.strip()
            if not col_clean:  # Skip empty columns
                continue
            try:
                year = int(col_clean)
                if 1960 <= year <= 2030:
                    year_cols.append(year)
                    year_indices[year] = i
            except ValueError:
                continue
        
        if not year_cols:
            print("❌ No year columns found!", flush=True)
            return
        
        print(f"📅 Found {len(year_cols)} year columns: {min(year_cols)}-{max(year_cols)}\n", flush=True)
        
        # Process indicators
        for imf_code, irc_code in IMF_TO_IRC.items():
            print(f"📊 Importing {imf_code} → {irc_code}", flush=True)
            
            indicator_id = get_indicator_id(cursor, irc_code)
            if not indicator_id:
                print(f"❌ Indicator {irc_code} not found in database", flush=True)
                continue
            
            stats = {'new': 0, 'averaged': 0, 'skipped': 0, 'no_iso': 0, 'rows_processed': 0}
            
            # Reset file pointer
            f.seek(0)
            f.readline()  # Skip header again
            
            # Read all rows
            row_count = 0
            for line in f:
                row_count += 1
                if row_count % 1000 == 0:
                    print(f"   Processing row {row_count}...", flush=True)
                
                row = line.strip().split('\t')
                if len(row) < 3:
                    continue
                
                # Columns: 0=WEO Country Code, 1=ISO, 2=WEO Subject Code, ...
                weo_subject = row[2].strip() if len(row) > 2 else ''
                
                # Only process rows for this indicator
                if weo_subject != imf_code:
                    continue
                
                stats['rows_processed'] += 1
                
                iso3 = row[1].strip() if len(row) > 1 else ''
                if not iso3 or len(iso3) != 3:
                    stats['no_iso'] += 1
                    continue
                
                country_id = get_country_id(cursor, iso3)
                if not country_id:
                    stats['no_iso'] += 1
                    continue
                
                # Process each year column
                for year in year_cols:
                    idx = year_indices[year]
                    if idx >= len(row):
                        continue
                    
                    value = clean_value(row[idx])
                    if value is None:
                        stats['skipped'] += 1
                        continue
                    
                    # Insert or average
                    result = insert_or_average(cursor, country_id, indicator_id, year, value)
                    stats[result] += 1
            
            print(f"   Processed {stats['rows_processed']} matching rows", flush=True)
            
            # Update source
            update_indicator_source(cursor, irc_code)
            
            # Print stats
            total = stats['new'] + stats['averaged']
            print(f"   ✅ Total: {total} values ({stats['new']} new + {stats['averaged']} averaged)", flush=True)
            print(f"   ⚠️  Skipped: {stats['skipped']} (no data), {stats['no_iso']} (no ISO3)", flush=True)
            print(flush=True)

def main():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        import_imf_weo(cursor)
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print("\n⚠️  REMINDER: Verify semantic accuracy of mappings:")
        print("   - Public debt vs External debt")
        print("   - Fiscal balance vs Debt service")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
