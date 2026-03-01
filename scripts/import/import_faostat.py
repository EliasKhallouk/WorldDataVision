#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import données FAOSTAT dans la base IRC
Indicateurs: AG.LND.AGRI.ZS, AG.LND.TOTL.K2, AG.LND.FRST.ZS, AG.LND.ARBL.HA.PC
Stratégie: MOYENNE en cas de conflit
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

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

LANDUSE_FILE = "/home/elias/PROJECT/WorldDataVision/Data/FAOSTAT/Inputs_LandUse_E_All_Data_(Normalized).csv"

# Mapping FAOSTAT → IRC
# Format: 'IRC_CODE': (Item Code, Element Code, factor_conversion, description)
INDICATOR_MAPPING = {
    'AG.LND.AGRI.ZS': (6610, 7209, 1.0, "Agricultural land (% of land area)"),
    'AG.LND.TOTL.K2': (6601, 5110, 0.01, "Land area (1000 ha → km²)"),  # 1000 ha = 10 km²
    'AG.LND.FRST.ZS': (6646, 7210, 1.0, "Forest land (% of land area)"),
    'AG.LND.ARBL.HA.PC': (6621, 7277, 1.0, "Arable land (hectares per person)"),
}

# Mapping pays FAOSTAT (Area) → BDD (iso3/name)
COUNTRY_MAPPING_FAO = {
    "afghanistan": "afghanistan", "albania": "albanie", "algeria": "algérie",
    "angola": "angola", "argentina": "argentine", "armenia": "arménie",
    "australia": "australie", "austria": "autriche", "azerbaijan": "azerbaïdjan",
    "bahamas": "bahamas", "bangladesh": "bangladesh", "belarus": "bélarus",
    "belgium": "belgique", "benin": "bénin", "bolivia (plurinational state of)": "bolivie",
    "bosnia and herzegovina": "bosnie-herzégovine", "botswana": "botswana",
    "brazil": "brésil", "bulgaria": "bulgarie", "burkina faso": "burkina faso",
    "burundi": "burundi", "cambodia": "cambodge", "cameroon": "cameroun",
    "canada": "canada", "central african republic": "république centrafricaine",
    "chad": "tchad", "chile": "chili", "china, mainland": "chine",
    "china": "chine", "colombia": "colombie", "congo": "congo",
    "costa rica": "costa rica", "croatia": "croatie", "cuba": "cuba",
    "cyprus": "chypre", "czechia": "tchéquie", "czech republic": "tchéquie",
    "côte d'ivoire": "côte d'ivoire", "democratic republic of the congo": "congo (rép. dém.)",
    "denmark": "danemark", "djibouti": "djibouti", "dominican republic": "république dominicaine",
    "ecuador": "équateur", "egypt": "égypte", "el salvador": "el salvador",
    "estonia": "estonie", "ethiopia": "éthiopie", "ethiopia pdr": "éthiopie",
    "fiji": "fidji", "finland": "finlande", "france": "france",
    "gabon": "gabon", "gambia": "gambie", "georgia": "géorgie",
    "germany": "allemagne", "ghana": "ghana", "greece": "grèce",
    "guatemala": "guatemala", "guinea": "guinée", "guinea-bissau": "guinée-bissau",
    "guyana": "guyana", "haiti": "haïti", "honduras": "honduras",
    "hungary": "hongrie", "iceland": "islande", "india": "inde",
    "indonesia": "indonésie", "iran (islamic republic of)": "iran",
    "iraq": "iraq", "ireland": "irlande", "israel": "israël",
    "italy": "italie", "jamaica": "jamaïque", "japan": "japon",
    "jordan": "jordanie", "kazakhstan": "kazakhstan", "kenya": "kenya",
    "korea, republic of": "corée (république de)", "kuwait": "koweït",
    "kyrgyzstan": "kirghizistan", "lao people's democratic republic": "laos",
    "latvia": "lettonie", "lebanon": "liban", "lesotho": "lesotho",
    "liberia": "libéria", "libya": "libye", "lithuania": "lituanie",
    "luxembourg": "luxembourg", "madagascar": "madagascar", "malawi": "malawi",
    "malaysia": "malaisie", "mali": "mali", "mauritania": "mauritanie",
    "mauritius": "maurice", "mexico": "mexique", "mongolia": "mongolie",
    "morocco": "maroc", "mozambique": "mozambique", "myanmar": "myanmar",
    "namibia": "namibie", "nepal": "népal", "netherlands": "pays-bas",
    "netherlands (kingdom of the)": "pays-bas", "new zealand": "nouvelle-zélande",
    "nicaragua": "nicaragua", "niger": "niger", "nigeria": "nigéria",
    "north macedonia": "macédoine du nord", "norway": "norvège",
    "pakistan": "pakistan", "panama": "panama", "papua new guinea": "papouasie-nouvelle-guinée",
    "paraguay": "paraguay", "peru": "pérou", "philippines": "philippines",
    "poland": "pologne", "portugal": "portugal", "qatar": "qatar",
    "republic of korea": "corée (république de)", "republic of moldova": "moldavie",
    "romania": "roumanie", "russian federation": "russie", "rwanda": "rwanda",
    "saudi arabia": "arabie saoudite", "senegal": "sénégal", "serbia": "serbie",
    "sierra leone": "sierra leone", "slovakia": "slovaquie", "slovenia": "slovénie",
    "somalia": "somalie", "south africa": "afrique du sud", "south sudan": "soudan du sud",
    "spain": "espagne", "sri lanka": "sri lanka", "sudan": "soudan",
    "sudan (former)": "soudan", "suriname": "suriname", "sweden": "suède",
    "switzerland": "suisse", "syrian arab republic": "syrie", "tajikistan": "tadjikistan",
    "thailand": "thaïlande", "togo": "togo", "trinidad and tobago": "trinité-et-tobago",
    "tunisia": "tunisie", "turkey": "turquie", "turkmenistan": "turkménistan",
    "uganda": "ouganda", "ukraine": "ukraine", "united arab emirates": "émirats arabes unis",
    "united kingdom": "royaume-uni", "united kingdom of great britain and northern ireland": "royaume-uni",
    "united republic of tanzania": "tanzanie", "united states of america": "états-unis",
    "uruguay": "uruguay", "uzbekistan": "ouzbékistan", "venezuela (bolivarian republic of)": "venezuela",
    "viet nam": "viet nam", "yemen": "yémen", "zambia": "zambie", "zimbabwe": "zimbabwe"
}

def get_country_mapping(conn):
    """Crée mapping pays complet"""
    cur = conn.cursor()
    cur.execute("SELECT id, name, iso3 FROM country")
    
    mapping = {}
    for country_id, db_name, iso3 in cur.fetchall():
        db_name_norm = db_name.lower().strip()
        mapping[db_name_norm] = country_id
        
        if iso3:
            mapping[iso3.lower()] = country_id
        
        # Ajouter correspondances FAO
        for fao_name, fr_name in COUNTRY_MAPPING_FAO.items():
            if fr_name == db_name_norm:
                mapping[fao_name] = country_id
    
    cur.close()
    return mapping

def import_faostat_indicator(conn, df, country_mapping, irc_code, item_code, element_code, conversion_factor):
    """Import un indicateur FAOSTAT spécifique"""
    
    # Récupérer l'indicateur dans la BDD
    cur = conn.cursor()
    cur.execute("SELECT id, name, unit FROM indicator WHERE code = %s", (irc_code,))
    indicator = cur.fetchone()
    
    if not indicator:
        print(f"  ❌ Indicateur {irc_code} non trouvé dans la BDD")
        return 0
    
    indicator_id, indicator_name, unit = indicator
    print(f"\n✓ {irc_code}: {indicator_name} (unité: {unit})")
    
    # Filtrer les données FAOSTAT
    subset = df[(df['Item Code'] == item_code) & (df['Element Code'] == element_code)].copy()
    print(f"  Données FAOSTAT: {len(subset):,} observations")
    
    if len(subset) == 0:
        print(f"  ⚠️  Aucune donnée trouvée pour Item={item_code}, Element={element_code}")
        return 0
    
    # Préparer les valeurs à insérer (en évitant les doublons)
    values_dict = {}  # clé = (country_id, year), valeur = value
    matched_countries = set()
    unmatched_countries = set()
    
    for _, row in subset.iterrows():
        area_name = str(row['Area']).lower().strip()
        country_id = country_mapping.get(area_name)
        
        if not country_id:
            unmatched_countries.add(row['Area'])
            continue
        
        matched_countries.add(row['Area'])
        year = int(row['Year'])
        value = row['Value']
        
        if pd.isna(value) or value == '' or value == '-':
            continue
        
        try:
            value_float = float(value) * conversion_factor
            # Si doublon, prendre la moyenne
            key = (country_id, year)
            if key in values_dict:
                values_dict[key] = (values_dict[key] + value_float) / 2
            else:
                values_dict[key] = value_float
        except (ValueError, TypeError):
            continue
    
    # Convertir en liste de tuples
    values_to_insert = [(indicator_id, country_id, year, value) 
                        for (country_id, year), value in values_dict.items()]
    
    print(f"  Pays matchés: {len(matched_countries)}")
    print(f"  Pays non matchés: {len(unmatched_countries)}")
    print(f"  Valeurs à insérer: {len(values_to_insert):,}")
    
    if len(values_to_insert) == 0:
        print(f"  ⚠️  Aucune valeur valide à insérer")
        return 0
    
    # Import avec MOYENNE si conflit
    execute_values(cur, """
        INSERT INTO indicator_value (indicator_id, country_id, year, value)
        VALUES %s
        ON CONFLICT (indicator_id, country_id, year) 
        DO UPDATE SET value = (EXCLUDED.value + indicator_value.value) / 2
    """, values_to_insert, page_size=1000)
    
    conn.commit()
    print(f"  ✅ {len(values_to_insert):,} valeurs importées (moyenne si conflit)")
    
    # Mettre à jour la source
    cur.execute("""
        SELECT source FROM indicator WHERE id = %s
    """, (indicator_id,))
    current_source = cur.fetchone()[0]
    
    if 'FAOSTAT' not in current_source:
        new_source = current_source + ', FAOSTAT'
        cur.execute("UPDATE indicator SET source = %s WHERE id = %s", (new_source, indicator_id))
        conn.commit()
        print(f"  📝 Source mise à jour: {new_source}")
    
    cur.close()
    return len(values_to_insert)

def main():
    print("\n" + "="*80)
    print("IMPORT FAOSTAT - LAND USE")
    print("="*80)
    
    # Connexion
    conn = psycopg2.connect(**DB_CONFIG)
    print("✓ Connecté à PostgreSQL")
    
    # Charger données FAOSTAT
    print(f"\n📥 Chargement {LANDUSE_FILE}...")
    df = pd.read_csv(LANDUSE_FILE, encoding='latin-1', low_memory=False)
    print(f"✓ {len(df):,} lignes chargées")
    
    # Mapping pays
    country_mapping = get_country_mapping(conn)
    print(f"✓ {len(country_mapping)} variantes pays disponibles")
    
    # Import de chaque indicateur
    print("\n" + "="*80)
    print("IMPORT DES INDICATEURS")
    print("="*80)
    
    total_imported = 0
    
    for irc_code, (item_code, element_code, conversion, desc) in INDICATOR_MAPPING.items():
        print(f"\n📊 {desc}")
        imported = import_faostat_indicator(
            conn, df, country_mapping, 
            irc_code, item_code, element_code, conversion
        )
        total_imported += imported
    
    # Résumé final
    print("\n" + "="*80)
    print("✅ IMPORT TERMINÉ")
    print("="*80)
    print(f"Total: {total_imported:,} valeurs importées")
    print(f"Indicateurs enrichis: {len(INDICATOR_MAPPING)}")
    
    conn.close()

if __name__ == "__main__":
    main()
