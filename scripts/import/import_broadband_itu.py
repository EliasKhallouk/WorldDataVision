#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import IT.NET.BBND.P2 (Fixed broadband subscriptions)
1) Import World Bank (IRC) 
2) Enrichissement ITU avec MOYENNE si conflit
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# ========================================
# CONFIGURATION
# ========================================
DB_CONFIG = {
    "dbname": "worlddatavision",
    "user": "elias",
    "password": "MaBaseDeDonnee",
    "host": "localhost",
    "port": "5432"
}

IRC_FILE = "/home/elias/PROJECT/WorldDataVision/Data/IRC/fixed_broadband.csv"
ITU_FILE = "/home/elias/PROJECT/WorldDataVision/Data/ITU/Fixed-broadband subscriptions.csv"
INDICATOR_CODE = "IT.NET.BBND.P2"

# Table de correspondance EN→FR
COUNTRY_MAPPING = {
    "afghanistan": "afghanistan", "albania": "albanie", "algeria": "algérie",
    "andorra": "andorre", "angola": "angola", "argentina": "argentine",
    "armenia": "arménie", "australia": "australie", "austria": "autriche",
    "azerbaijan": "azerbaïdjan", "bahamas": "bahamas", "bahrain": "bahreïn",
    "bangladesh": "bangladesh", "barbados": "barbade", "belarus": "bélarus",
    "belgium": "belgique", "belize": "belize", "benin": "bénin",
    "bhutan": "bhoutan", "bolivia (plurinational state of)": "bolivie",
    "bosnia and herzegovina": "bosnie-herzégovine", "botswana": "botswana",
    "brazil": "brésil", "brunei darussalam": "brunéi darussalam",
    "bulgaria": "bulgarie", "burkina faso": "burkina faso", "burundi": "burundi",
    "cabo verde": "cabo verde", "cambodia": "cambodge", "cameroon": "cameroun",
    "canada": "canada", "central african republic": "république centrafricaine",
    "chad": "tchad", "chile": "chili", "china": "chine", "colombia": "colombie",
    "comoros": "comores", "congo": "congo", "costa rica": "costa rica",
    "croatia": "croatie", "cuba": "cuba", "cyprus": "chypre", "czechia": "tchéquie",
    "denmark": "danemark", "djibouti": "djibouti", "dominica": "dominique",
    "dominican republic": "république dominicaine", "ecuador": "équateur",
    "egypt": "égypte", "el salvador": "el salvador", "estonia": "estonie",
    "ethiopia": "éthiopie", "fiji": "fidji", "finland": "finlande",
    "france": "france", "gabon": "gabon", "gambia": "gambie",
    "georgia": "géorgie", "germany": "allemagne", "ghana": "ghana",
    "greece": "grèce", "guatemala": "guatemala", "guinea": "guinée",
    "haiti": "haïti", "honduras": "honduras", "hungary": "hongrie",
    "iceland": "islande", "india": "inde", "indonesia": "indonésie",
    "iran (islamic republic of)": "iran", "iraq": "iraq", "ireland": "irlande",
    "israel": "israël", "italy": "italie", "jamaica": "jamaïque",
    "japan": "japon", "jordan": "jordanie", "kazakhstan": "kazakhstan",
    "kenya": "kenya", "korea (republic of)": "corée (république de)",
    "kuwait": "koweït", "kyrgyzstan": "kirghizistan", "latvia": "lettonie",
    "lebanon": "liban", "lesotho": "lesotho", "libya": "libye",
    "lithuania": "lituanie", "luxembourg": "luxembourg", "madagascar": "madagascar",
    "malawi": "malawi", "malaysia": "malaisie", "maldives": "maldives",
    "mali": "mali", "malta": "malte", "mauritania": "mauritanie",
    "mauritius": "maurice", "mexico": "mexique", "moldova": "moldavie",
    "monaco": "monaco", "mongolia": "mongolie", "montenegro": "monténégro",
    "morocco": "maroc", "mozambique": "mozambique", "myanmar": "myanmar",
    "namibia": "namibie", "nepal": "népal", "netherlands": "pays-bas",
    "new zealand": "nouvelle-zélande", "nicaragua": "nicaragua",
    "niger": "niger", "nigeria": "nigéria", "north macedonia": "macédoine du nord",
    "norway": "norvège", "oman": "oman", "pakistan": "pakistan",
    "palestine": "palestine", "panama": "panama", "paraguay": "paraguay",
    "peru": "pérou", "philippines": "philippines", "poland": "pologne",
    "portugal": "portugal", "qatar": "qatar", "romania": "roumanie",
    "russian federation": "russie", "rwanda": "rwanda", "saudi arabia": "arabie saoudite",
    "senegal": "sénégal", "serbia": "serbie", "singapore": "singapour",
    "slovakia": "slovaquie", "slovenia": "slovénie", "south africa": "afrique du sud",
    "south sudan": "soudan du sud", "spain": "espagne", "sri lanka": "sri lanka",
    "sudan": "soudan", "suriname": "suriname", "sweden": "suède",
    "switzerland": "suisse", "taiwan, china": "taiwan (chine)",
    "tajikistan": "tadjikistan", "tanzania": "tanzanie", "thailand": "thaïlande",
    "timor-leste": "timor-leste", "togo": "togo", "trinidad and tobago": "trinité-et-tobago",
    "tunisia": "tunisie", "turkey": "turquie", "turkmenistan": "turkménistan",
    "uganda": "ouganda", "ukraine": "ukraine", "united arab emirates": "émirats arabes unis",
    "united kingdom": "royaume-uni", "united states": "états-unis",
    "uruguay": "uruguay", "uzbekistan": "ouzbékistan",
    "venezuela (bolivarian republic of)": "venezuela", "viet nam": "viet nam",
    "yemen": "yémen", "zambia": "zambie", "zimbabwe": "zimbabwe"
}

def get_country_mapping(conn):
    """Crée mapping pays"""
    cur = conn.cursor()
    cur.execute("SELECT id, name, iso3 FROM country")
    
    mapping = {}
    for country_id, db_name, iso3 in cur.fetchall():
        db_name_norm = db_name.lower().strip()
        mapping[db_name_norm] = country_id
        
        if iso3:
            mapping[iso3.lower()] = country_id
        
        for en_name, fr_name in COUNTRY_MAPPING.items():
            if fr_name == db_name_norm:
                mapping[en_name] = country_id
    
    cur.close()
    return mapping

def main():
    print("\n" + "="*80)
    print("IMPORT IT.NET.BBND.P2 - Fixed broadband subscriptions")
    print("="*80)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Récupérer indicateur
    cur.execute("SELECT id FROM indicator WHERE code = %s", (INDICATOR_CODE,))
    indicator_id = cur.fetchone()[0]
    print(f"✓ Indicateur ID: {indicator_id}")
    
    country_mapping = get_country_mapping(conn)
    print(f"✓ Mapping: {len(country_mapping)} variantes")
    
    # ÉTAPE 1: Import IRC (World Bank)
    print("\n" + "="*80)
    print("ÉTAPE 1: IMPORT WORLD BANK (IRC)")
    print("="*80)
    
    irc_df = pd.read_csv(IRC_FILE)
    print(f"✓ {len(irc_df)} lignes chargées")
    
    irc_values = []
    for _, row in irc_df.iterrows():
        if pd.isna(row['value']):
            continue
        
        country_code = str(row['country_code']).lower().strip()
        country_id = country_mapping.get(country_code)
        
        if country_id:
            irc_values.append((indicator_id, country_id, int(row['year']), float(row['value'])))
    
    execute_values(cur, """
        INSERT INTO indicator_value (indicator_id, country_id, year, value)
        VALUES %s
        ON CONFLICT (indicator_id, country_id, year) DO UPDATE SET value = EXCLUDED.value
    """, irc_values, page_size=1000)
    
    conn.commit()
    print(f"✅ {len(irc_values):,} valeurs World Bank importées")
    
    # ÉTAPE 2: Enrichissement ITU avec MOYENNE
    print("\n" + "="*80)
    print("ÉTAPE 2: ENRICHISSEMENT ITU (moyenne si conflit)")
    print("="*80)
    
    itu_df = pd.read_csv(ITU_FILE)
    print(f"✓ {len(itu_df)} pays ITU chargés")
    
    year_cols = [col for col in itu_df.columns if col != 'Economy']
    
    itu_values = []
    matched = 0
    
    for _, row in itu_df.iterrows():
        country_norm = row['Economy'].lower().strip()
        country_id = country_mapping.get(country_norm)
        
        if not country_id:
            continue
        
        matched += 1
        
        for year_str in year_cols:
            value_str = str(row[year_str]).strip()
            if value_str in ['', '-', 'nan']:
                continue
            
            try:
                itu_values.append((indicator_id, country_id, int(year_str), float(value_str)))
            except:
                continue
    
    # Import avec MOYENNE si conflit
    execute_values(cur, """
        INSERT INTO indicator_value (indicator_id, country_id, year, value)
        VALUES %s
        ON CONFLICT (indicator_id, country_id, year) 
        DO UPDATE SET value = (EXCLUDED.value + indicator_value.value) / 2
    """, itu_values, page_size=1000)
    
    conn.commit()
    print(f"✅ {len(itu_values):,} valeurs ITU importées ({matched} pays matchés)")
    
    # Mise à jour source
    cur.execute("""
        UPDATE indicator 
        SET source = 'World Bank, ITU (International Telecommunication Union)'
        WHERE id = %s
    """, (indicator_id,))
    conn.commit()
    
    # Stats finales
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = %s", (indicator_id,))
    total_values, total_countries = cur.fetchone()
    
    print("\n" + "="*80)
    print("✅ TERMINÉ")
    print("="*80)
    print(f"Total: {total_values:,} valeurs, {total_countries} pays")
    print(f"Source: 'World Bank, ITU'")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
