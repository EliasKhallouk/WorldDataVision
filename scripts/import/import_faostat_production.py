#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import FAOSTAT Production Indices
AG.PRD.FOOD.XD, AG.PRD.CROP.XD, AG.PRD.LVSK.XD
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
sys.path.append('/home/elias/PROJECT/WorldDataVision')
from import_faostat import get_country_mapping, DB_CONFIG

PROD_FILE = "/home/elias/PROJECT/WorldDataVision/Data/FAOSTAT/Production_Indices_E_All_Data_(Normalized).csv"

# Mapping: IRC_CODE: (Item Code, Element Code, description)
PROD_MAPPING = {
    'AG.PRD.FOOD.XD': (2054, 432, "Food production index"),
    'AG.PRD.CROP.XD': (2041, 432, "Crop production index"),
    'AG.PRD.LVSK.XD': (2044, 432, "Livestock production index"),
}

def import_production_index(conn, df, country_mapping, irc_code, item_code, element_code):
    """Import indice de production"""
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM indicator WHERE code = %s", (irc_code,))
    indicator = cur.fetchone()
    
    if not indicator:
        print(f"  ❌ {irc_code} non trouvé")
        return 0
    
    indicator_id, name = indicator
    print(f"\n✓ {irc_code}: {name}")
    
    # Filtrer données
    subset = df[(df['Item Code'] == item_code) & (df['Element Code'] == element_code)].copy()
    print(f"  Observations FAOSTAT: {len(subset):,}")
    
    if len(subset) == 0:
        return 0
    
    # Préparer import (avec déduplication)
    values_dict = {}
    matched = 0
    
    for _, row in subset.iterrows():
        area = str(row['Area']).lower().strip()
        country_id = country_mapping.get(area)
        
        if not country_id:
            continue
        
        matched += 1
        year = int(row['Year'])
        value = row['Value']
        
        if pd.isna(value):
            continue
        
        try:
            key = (country_id, year)
            if key in values_dict:
                values_dict[key] = (values_dict[key] + float(value)) / 2
            else:
                values_dict[key] = float(value)
        except:
            continue
    
    values_to_insert = [(indicator_id, cid, yr, val) for (cid, yr), val in values_dict.items()]
    
    print(f"  Pays matchés: {matched}")
    print(f"  Valeurs: {len(values_to_insert):,}")
    
    if len(values_to_insert) == 0:
        return 0
    
    # Import avec moyenne
    execute_values(cur, """
        INSERT INTO indicator_value (indicator_id, country_id, year, value)
        VALUES %s
        ON CONFLICT (indicator_id, country_id, year)
        DO UPDATE SET value = (EXCLUDED.value + indicator_value.value) / 2
    """, values_to_insert, page_size=1000)
    
    conn.commit()
    
    # Update source
    cur.execute("SELECT source FROM indicator WHERE id = %s", (indicator_id,))
    source = cur.fetchone()[0]
    if 'FAOSTAT' not in source:
        cur.execute("UPDATE indicator SET source = %s WHERE id = %s", (source + ', FAOSTAT', indicator_id))
        conn.commit()
        print(f"  📝 Source: {source}, FAOSTAT")
    
    print(f"  ✅ {len(values_to_insert):,} importées")
    cur.close()
    return len(values_to_insert)

def main():
    print("="*80)
    print("IMPORT FAOSTAT - PRODUCTION INDICES")
    print("="*80)
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    print(f"\n📥 Chargement {PROD_FILE}...")
    df = pd.read_csv(PROD_FILE, encoding='latin-1', low_memory=False)
    print(f"✓ {len(df):,} lignes")
    
    country_mapping = get_country_mapping(conn)
    print(f"✓ {len(country_mapping)} variantes pays")
    
    total = 0
    for irc_code, (item, element, desc) in PROD_MAPPING.items():
        print(f"\n📊 {desc}")
        total += import_production_index(conn, df, country_mapping, irc_code, item, element)
    
    print("\n" + "="*80)
    print(f"✅ TERMINÉ: {total:,} valeurs importées")
    print("="*80)
    
    conn.close()

if __name__ == "__main__":
    main()
