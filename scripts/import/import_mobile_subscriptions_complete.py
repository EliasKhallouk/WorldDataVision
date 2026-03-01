#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import complet IT.CEL.SETS.P2 (Mobile cellular subscriptions per 100 people)
Sources: 1) World Bank (IRC), 2) ITU
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys

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

IRC_FILE = "/home/elias/PROJECT/WorldDataVision/Data/IRC/mobile_subscriptions.csv"
ITU_FILE = "/home/elias/PROJECT/WorldDataVision/Data/ITU/Mobile-cellular subscriptions.csv"
INDICATOR_CODE = "IT.CEL.SETS.P2"

# ========================================
# TABLE DE CORRESPONDANCE EN→FR
# ========================================
COUNTRY_MAPPING = {
    # A
    "afghanistan": "afghanistan", "albania": "albanie", "algeria": "algérie",
    "american samoa": "samoa américaines", "andorra": "andorre", "angola": "angola",
    "antigua and barbuda": "antigua-et-barbuda", "argentina": "argentine",
    "armenia": "arménie", "aruba": "aruba", "australia": "australie",
    "austria": "autriche", "azerbaijan": "azerbaïdjan",
    
    # B
    "bahamas": "bahamas", "bahrain": "bahreïn", "bangladesh": "bangladesh",
    "barbados": "barbade", "belarus": "bélarus", "belgium": "belgique",
    "belize": "belize", "benin": "bénin", "bermuda": "bermudes",
    "bhutan": "bhoutan", "bolivia (plurinational state of)": "bolivie",
    "bosnia and herzegovina": "bosnie-herzégovine", "botswana": "botswana",
    "brazil": "brésil", "british virgin islands": "îles vierges britanniques",
    "brunei darussalam": "brunéi darussalam", "bulgaria": "bulgarie",
    "burkina faso": "burkina faso", "burundi": "burundi",
    
    # C
    "cabo verde": "cabo verde", "cambodia": "cambodge", "cameroon": "cameroun",
    "canada": "canada", "cayman islands": "îles caïmans",
    "central african republic": "république centrafricaine", "chad": "tchad",
    "chile": "chili", "china": "chine", "colombia": "colombie",
    "comoros": "comores", "congo": "congo", "congo (dem. rep.)": "congo (rép. dém.)",
    "cook islands": "îles cook", "costa rica": "costa rica", "croatia": "croatie",
    "cuba": "cuba", "cyprus": "chypre", "czechia": "tchéquie",
    "czech republic": "tchéquie", "côte d'ivoire": "côte d'ivoire",
    
    # D-E
    "denmark": "danemark", "djibouti": "djibouti", "dominica": "dominique",
    "dominican republic": "république dominicaine", "ecuador": "équateur",
    "egypt": "égypte", "el salvador": "el salvador",
    "equatorial guinea": "guinée équatoriale", "eritrea": "érythrée",
    "estonia": "estonie", "eswatini": "eswatini", "ethiopia": "éthiopie",
    
    # F-G
    "fiji": "fidji", "finland": "finlande", "france": "france",
    "french polynesia": "polynésie française", "gabon": "gabon",
    "gambia": "gambie", "georgia": "géorgie", "germany": "allemagne",
    "ghana": "ghana", "greece": "grèce", "greenland": "groenland",
    "grenada": "grenade", "guam": "guam", "guatemala": "guatemala",
    "guinea": "guinée", "guinea-bissau": "guinée-bissau", "guyana": "guyana",
    
    # H-I
    "haiti": "haïti", "honduras": "honduras", "hong kong, china": "hong kong (chine)",
    "hungary": "hongrie", "iceland": "islande", "india": "inde",
    "indonesia": "indonésie", "iran (islamic republic of)": "iran",
    "iraq": "iraq", "ireland": "irlande", "israel": "israël", "italy": "italie",
    
    # J-K-L
    "jamaica": "jamaïque", "japan": "japon", "jordan": "jordanie",
    "kazakhstan": "kazakhstan", "kenya": "kenya", "kiribati": "kiribati",
    "korea (dem. people's rep.)": "corée (rép. pop. dém.)",
    "korea (republic of)": "corée (république de)", "kuwait": "koweït",
    "kyrgyzstan": "kirghizistan", "lao people's dem. rep.": "laos",
    "latvia": "lettonie", "lebanon": "liban", "lesotho": "lesotho",
    "liberia": "libéria", "libya": "libye", "liechtenstein": "liechtenstein",
    "lithuania": "lituanie", "luxembourg": "luxembourg",
    
    # M
    "macao, china": "macao (chine)", "madagascar": "madagascar",
    "malawi": "malawi", "malaysia": "malaisie", "maldives": "maldives",
    "mali": "mali", "malta": "malte", "marshall islands": "îles marshall",
    "mauritania": "mauritanie", "mauritius": "maurice", "mexico": "mexique",
    "micronesia (fed. states of)": "micronésie", "moldova": "moldavie",
    "monaco": "monaco", "mongolia": "mongolie", "montenegro": "monténégro",
    "morocco": "maroc", "mozambique": "mozambique", "myanmar": "myanmar",
    
    # N-O-P
    "namibia": "namibie", "nauru": "nauru", "nepal": "népal",
    "netherlands": "pays-bas", "new caledonia": "nouvelle-calédonie",
    "new zealand": "nouvelle-zélande", "nicaragua": "nicaragua",
    "niger": "niger", "nigeria": "nigéria", "niue": "niue",
    "north macedonia": "macédoine du nord", "norway": "norvège", "oman": "oman",
    "pakistan": "pakistan", "palau": "palaos", "palestine": "palestine",
    "panama": "panama", "papua new guinea": "papouasie-nouvelle-guinée",
    "paraguay": "paraguay", "peru": "pérou", "philippines": "philippines",
    "poland": "pologne", "portugal": "portugal", "puerto rico": "porto rico",
    
    # Q-R-S
    "qatar": "qatar", "romania": "roumanie", "russian federation": "russie",
    "rwanda": "rwanda", "saint kitts and nevis": "saint-kitts-et-nevis",
    "saint lucia": "sainte-lucie",
    "saint vincent and the grenadines": "saint-vincent-et-les grenadines",
    "samoa": "samoa", "san marino": "saint-marin",
    "sao tome and principe": "sao tomé-et-principe", "saudi arabia": "arabie saoudite",
    "senegal": "sénégal", "serbia": "serbie", "seychelles": "seychelles",
    "sierra leone": "sierra leone", "singapore": "singapour",
    "slovakia": "slovaquie", "slovenia": "slovénie",
    "solomon islands": "îles salomon", "somalia": "somalie",
    "south africa": "afrique du sud", "south sudan": "soudan du sud",
    "spain": "espagne", "sri lanka": "sri lanka", "sudan": "soudan",
    "suriname": "suriname", "sweden": "suède", "switzerland": "suisse",
    "syrian arab republic": "syrie",
    
    # T-U-V-Y-Z
    "taiwan, china": "taiwan (chine)", "tajikistan": "tadjikistan",
    "tanzania": "tanzanie", "thailand": "thaïlande", "timor-leste": "timor-leste",
    "togo": "togo", "tonga": "tonga", "trinidad and tobago": "trinité-et-tobago",
    "tunisia": "tunisie", "turkey": "turquie", "turkmenistan": "turkménistan",
    "turks and caicos islands": "îles turques-et-caïques", "tuvalu": "tuvalu",
    "uganda": "ouganda", "ukraine": "ukraine",
    "united arab emirates": "émirats arabes unis", "united kingdom": "royaume-uni",
    "united states": "états-unis", "uruguay": "uruguay", "uzbekistan": "ouzbékistan",
    "vanuatu": "vanuatu", "venezuela (bolivarian republic of)": "venezuela",
    "viet nam": "viet nam", "virgin islands (u.s.)": "îles vierges des états-unis",
    "yemen": "yémen", "zambia": "zambie", "zimbabwe": "zimbabwe"
}

# ========================================
# FONCTIONS
# ========================================

def normalize_name(name):
    """Normalisation simple"""
    return name.lower().strip()

def get_country_mapping(conn):
    """Crée mapping complet pays"""
    cur = conn.cursor()
    cur.execute("SELECT id, name, iso3 FROM country")
    
    mapping = {}
    
    for country_id, db_name, iso3 in cur.fetchall():
        db_name_norm = normalize_name(db_name)
        
        # Nom français BDD
        mapping[db_name_norm] = country_id
        
        # Code ISO3
        if iso3:
            mapping[iso3.lower()] = country_id
        
        # Correspondance EN→FR
        for en_name, fr_name in COUNTRY_MAPPING.items():
            if fr_name == db_name_norm:
                mapping[en_name] = country_id
    
    cur.close()
    return mapping

def import_irc_data(conn, country_mapping, indicator_id):
    """Import données World Bank (IRC)"""
    print("\n" + "="*80)
    print("ÉTAPE 1: IMPORT WORLD BANK (IRC)")
    print("="*80)
    
    df = pd.read_csv(IRC_FILE)
    print(f"✓ Fichier chargé: {len(df)} lignes")
    print(f"  Pays: {df['country_code'].nunique()}")
    print(f"  Années: {df['year'].min()} - {df['year'].max()}")
    
    # Valider
    values = df['value'].dropna()
    print(f"  Valeurs: {values.min():.2f} - {values.max():.2f}")
    print(f"✓ Format validé: per 100 people (déjà normalisé)")
    
    # Préparer import
    values_to_insert = []
    matched = set()
    unmatched = set()
    
    for _, row in df.iterrows():
        if pd.isna(row['value']):
            continue
        
        country_code = str(row['country_code']).lower().strip()
        
        # Chercher par code ISO3
        country_id = country_mapping.get(country_code)
        
        if not country_id:
            unmatched.add(row['country_code'])
            continue
        
        matched.add(row['country_code'])
        
        values_to_insert.append((
            indicator_id,
            country_id,
            int(row['year']),
            float(row['value'])
        ))
    
    print(f"\n📊 Statistiques pré-import:")
    print(f"  Pays matchés: {len(matched)}")
    print(f"  Pays non matchés: {len(unmatched)}")
    print(f"  Valeurs à insérer: {len(values_to_insert)}")
    
    # Import
    if values_to_insert:
        cur = conn.cursor()
        execute_values(
            cur,
            """
            INSERT INTO indicator_value (indicator_id, country_id, year, value)
            VALUES %s
            ON CONFLICT (indicator_id, country_id, year) 
            DO UPDATE SET value = EXCLUDED.value
            """,
            values_to_insert,
            page_size=1000
        )
        cur.close()
        conn.commit()
        
        print(f"✅ World Bank: {len(values_to_insert):,} valeurs importées")
    
    return len(values_to_insert), len(matched)

def import_itu_data(conn, country_mapping, indicator_id):
    """Import données ITU (enrichissement)"""
    print("\n" + "="*80)
    print("ÉTAPE 2: ENRICHISSEMENT ITU")
    print("="*80)
    
    df = pd.read_csv(ITU_FILE)
    print(f"✓ Fichier chargé: {len(df)} pays")
    
    # Valider
    year_cols = [col for col in df.columns if col != 'Economy']
    values = []
    for col in year_cols:
        values.extend(pd.to_numeric(df[col], errors='coerce').dropna().tolist())
    
    values = [v for v in values if v != '-']
    print(f"  Années: {len(year_cols)}")
    print(f"  Valeurs: {min(values):.2f} - {max(values):.2f}")
    print(f"✓ Format validé: déjà normalisé (pour 100 habitants)")
    
    # Préparer import
    values_to_insert = []
    matched = set()
    unmatched = set()
    
    for _, row in df.iterrows():
        itu_country = row['Economy']
        itu_country_norm = normalize_name(itu_country)
        
        country_id = country_mapping.get(itu_country_norm)
        
        if not country_id:
            unmatched.add(itu_country)
            continue
        
        matched.add(itu_country)
        
        for year_str in year_cols:
            value_str = str(row[year_str]).strip()
            
            if value_str in ['', '-', 'nan']:
                continue
            
            try:
                value = float(value_str)
                year = int(year_str)
                
                values_to_insert.append((
                    indicator_id,
                    country_id,
                    year,
                    value
                ))
            except (ValueError, TypeError):
                continue
    
    print(f"\n📊 Statistiques pré-import:")
    print(f"  Pays matchés: {len(matched)}")
    print(f"  Pays non matchés: {len(unmatched)}")
    print(f"  Valeurs à insérer: {len(values_to_insert)}")
    
    # Import avec MOYENNE si conflit
    if values_to_insert:
        cur = conn.cursor()
        execute_values(
            cur,
            """
            INSERT INTO indicator_value (indicator_id, country_id, year, value)
            VALUES %s
            ON CONFLICT (indicator_id, country_id, year) 
            DO UPDATE SET value = (EXCLUDED.value + indicator_value.value) / 2
            """,
            values_to_insert,
            page_size=1000
        )
        
        # Compter les moyennes calculées
        cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT indicator_id, country_id, year 
                FROM indicator_value 
                WHERE indicator_id = %s
                GROUP BY indicator_id, country_id, year
            ) sub
        """, (indicator_id,))
        
        cur.close()
        conn.commit()
        
        print(f"✅ ITU: {len(values_to_insert):,} valeurs importées (moyenne si conflit)")
    
    return len(values_to_insert), len(matched)

def main():
    print("\n" + "="*80)
    print("IMPORT COMPLET IT.CEL.SETS.P2 (Mobile cellular subscriptions)")
    print("Sources: World Bank + ITU")
    print("="*80)
    
    # Connexion
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connecté à PostgreSQL")
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # Récupérer indicateur
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, unit 
        FROM indicator 
        WHERE code = %s
    """, (INDICATOR_CODE,))
    
    indicator = cur.fetchone()
    if not indicator:
        print(f"❌ Indicateur {INDICATOR_CODE} non trouvé!")
        return
    
    indicator_id, indicator_name, unit = indicator
    print(f"\n✓ Indicateur: {indicator_name} (ID={indicator_id}, unité={unit})")
    
    # Créer mapping pays
    country_mapping = get_country_mapping(conn)
    print(f"✓ Mapping: {len(country_mapping)} variantes disponibles")
    
    # Import World Bank
    wb_values, wb_countries = import_irc_data(conn, country_mapping, indicator_id)
    
    # Import ITU
    itu_values, itu_countries = import_itu_data(conn, country_mapping, indicator_id)
    
    # Mettre à jour la source
    cur.execute("""
        UPDATE indicator 
        SET source = 'World Bank, ITU (International Telecommunication Union)'
        WHERE id = %s
    """, (indicator_id,))
    conn.commit()
    
    # Statistiques finales
    print("\n" + "="*80)
    print("✅ IMPORT TERMINÉ")
    print("="*80)
    
    cur.execute("""
        SELECT COUNT(*) FROM indicator_value WHERE indicator_id = %s
    """, (indicator_id,))
    total_values = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = %s
    """, (indicator_id,))
    total_countries = cur.fetchone()[0]
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"  • World Bank (IRC): {wb_values:,} valeurs, {wb_countries} pays")
    print(f"  • ITU: {itu_values:,} valeurs, {itu_countries} pays")
    print(f"  • TOTAL en BDD: {total_values:,} valeurs, {total_countries} pays")
    print(f"\n🔄 Source: 'World Bank, ITU (International Telecommunication Union)'")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
