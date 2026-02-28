#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul complet de l'Index de Résilience Civilisationnelle (IRC)
Version 1.1 - 28 février 2026

Ce script implémente la méthodologie IRC complète :
1. Normalisation des indicateurs (winsorization + min-max)
2. Calcul des sous-piliers (moyenne géométrique)
3. Agrégation finale (moyenne pondérée)
4. Stockage dans la base de données

Piliers IRC :
- Démographie (25%) : 18 indicateurs
- Économie (20%) : 15 indicateurs  
- Gouvernance (20%) : 15 indicateurs
- Capital Humain (15%) : 11 indicateurs
- Souveraineté Matérielle (10%) : 8 indicateurs
- Innovation (5%) : 4 indicateurs
- Environnement (5%) : 4 indicateurs
TOTAL : 75 indicateurs
"""

import psycopg2
import pandas as pd
import numpy as np
from scipy import stats
import sys
from datetime import datetime

# Configuration de la base de données (connexion via socket Unix)
DB_CONFIG = {
    'dbname': 'worlddatavision',
    'user': 'elias'
    # Pas de host/port = utilise le socket Unix par défaut
}

# Définition des piliers IRC selon la méthodologie v1.1
IRC_STRUCTURE = {
    'Démographie': {
        'weight': 0.25,
        'indicators': [
            'SP.POP.TOTL', 'SP.POP.0014.TO.ZS', 'SP.POP.1564.TO.ZS', 'SP.POP.65UP.TO.ZS',
            'SP.DYN.TFRT.IN', 'SP.DYN.CBRT.IN', 'SP.DYN.CDRT.IN', 'SM.POP.NETM',
            'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS', 'SP.POP.DPND',
            'SP.POP.AG.MA.NO', 'SP.POP.AG.FE.NO', 'SP.POP.1564.MA.NO', 'SP.POP.1564.FE.NO',
            'SP.POP.0014.MA.NO', 'SP.POP.0014.FE.NO', 'SP.POP.65UP.MA.NO'
        ]
    },
    'Économie': {
        'weight': 0.20,
        'indicators': [
            'NY.GDP.MKTP.CD', 'NY.GDP.PCAP.CD', 'NY.GDP.MKTP.KD.ZG',
            'SL.UEM.TOTL.ZS', 'FP.CPI.TOTL.ZG', 'GC.DOD.TOTL.GD.ZS',
            'NE.EXP.GNFS.ZS', 'NE.IMP.GNFS.ZS', 'BX.KLT.DINV.WD.GD.ZS',
            'DT.DOD.DECT.GN.ZS', 'NY.GNS.ICTR.ZS', 'NE.CON.PRVT.ZS',
            'NE.CON.GOVT.ZS', 'GC.TAX.TOTL.GD.ZS', 'NY.ADJ.NNTY.PC.KD'
        ]
    },
    'Gouvernance': {
        'weight': 0.20,
        'indicators': [
            'CC.EST', 'GE.EST', 'PV.EST', 'RQ.EST', 'RL.EST', 'VA.EST',
            'IQ.CPA.TRAN.XQ', 'IQ.CPA.PUBS.XQ', 'IQ.CPA.DEBT.XQ', 'IQ.CPA.ENVR.XQ',
            'IQ.CPA.PROP.XQ', 'IQ.CPA.SOCI.XQ', 'IQ.CPA.FINM.XQ', 'IQ.CPA.IRAI.XQ',
            'SH.STA.STNT.ZS'
        ]
    },
    'Capital Humain': {
        'weight': 0.15,
        'indicators': [
            'SE.PRM.ENRR', 'SE.SEC.ENRR', 'SE.TER.ENRR',
            'SE.ADT.LITR.ZS', 'SE.XPD.TOTL.GD.ZS',
            'SP.DYN.LE00.IN', 'SP.DYN.IMRT.IN', 'SH.DYN.MORT',
            'SH.XPD.CHEX.GD.ZS', 'SH.MED.PHYS.ZS', 'SH.H2O.BASW.ZS'
        ]
    },
    'Souveraineté Matérielle': {
        'weight': 0.10,
        'indicators': [
            'EG.USE.PCAP.KG.OE', 'EG.USE.COMM.FO.ZS', 'EG.FEC.RNEW.ZS',
            'EG.USE.ELEC.KH.PC', 'EG.ELC.NUCL.ZS', 'EG.ELC.HYRO.ZS',
            'AG.LND.AGRI.ZS', 'AG.PRD.FOOD.XD'
        ]
    },
    'Innovation': {
        'weight': 0.05,
        'indicators': [
            'GB.XPD.RSDV.GD.ZS', 'IP.PAT.RESD', 'IT.NET.USER.ZS', 'IT.CEL.SETS.P2'
        ]
    },
    'Environnement': {
        'weight': 0.05,
        'indicators': [
            'AG.LND.FRST.ZS', 'ER.PTD.TOTL.ZS', 'EN.ATM.PM25.MC.M3', 'AG.LND.PRCP.MM'
        ]
    }
}


def connect_db():
    """Connexion à la base de données PostgreSQL via socket Unix"""
    try:
        # Connexion via socket Unix (pas de host = utilise /var/run/postgresql)
        conn = psycopg2.connect(
            dbname='worlddatavision',
            user='elias'
        )
        print("✅ Connexion à la base de données réussie")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")
        sys.exit(1)


def load_indicator_data(conn, year=2020):
    """
    Charge toutes les données d'indicateurs pour une année donnée
    
    Args:
        conn: Connexion PostgreSQL
        year: Année pour laquelle calculer l'IRC (par défaut 2020)
    
    Returns:
        DataFrame avec country_code, indicator_code, value
    """
    query = """
    SELECT 
        c.iso3 as country_code,
        i.code as indicator_code,
        iv.value
    FROM indicator_value iv
    JOIN indicator i ON iv.indicator_id = i.id
    JOIN country c ON iv.country_id = c.id
    WHERE iv.year = %s
        AND iv.value IS NOT NULL
    ORDER BY c.iso3, i.code;
    """
    
    print(f"\n📊 Chargement des données pour l'année {year}...")
    df = pd.read_sql(query, conn, params=(year,))
    print(f"   ✓ {len(df)} valeurs chargées")
    print(f"   ✓ {df['country_code'].nunique()} pays")
    print(f"   ✓ {df['indicator_code'].nunique()} indicateurs")
    
    return df


def normalize_indicator(values, direction='positive'):
    """
    Normalisation d'un indicateur (winsorization + min-max)
    
    Args:
        values: Serie pandas avec les valeurs
        direction: 'positive' si plus = mieux, 'negative' si moins = mieux
    
    Returns:
        Serie normalisée [0, 1]
    """
    if len(values) < 2:
        return values
    
    # Étape 1 : Winsorization (traitement des valeurs extrêmes)
    # On limite aux percentiles 2.5 et 97.5
    p25 = np.percentile(values.dropna(), 2.5)
    p975 = np.percentile(values.dropna(), 97.5)
    winsorized = values.clip(lower=p25, upper=p975)
    
    # Étape 2 : Normalisation min-max [0, 1]
    min_val = winsorized.min()
    max_val = winsorized.max()
    
    if max_val - min_val == 0:
        return pd.Series([0.5] * len(values), index=values.index)
    
    normalized = (winsorized - min_val) / (max_val - min_val)
    
    # Étape 3 : Inverser si l'indicateur est négatif (moins = mieux)
    if direction == 'negative':
        normalized = 1 - normalized
    
    return normalized


def get_indicator_direction(indicator_code):
    """
    Détermine si un indicateur est positif (plus = mieux) ou négatif (moins = mieux)
    
    Returns:
        'positive' ou 'negative'
    """
    # Indicateurs négatifs (moins = mieux)
    negative_indicators = {
        'SP.DYN.CDRT.IN',  # Taux de mortalité
        'SP.DYN.IMRT.IN',  # Mortalité infantile
        'SH.DYN.MORT',     # Mortalité maternelle
        'SL.UEM.TOTL.ZS',  # Chômage
        'FP.CPI.TOTL.ZG',  # Inflation
        'GC.DOD.TOTL.GD.ZS',  # Dette publique
        'DT.DOD.DECT.GN.ZS',  # Dette extérieure
        'EN.ATM.PM25.MC.M3',  # Pollution PM2.5
        'SH.STA.STNT.ZS',  # Malnutrition
        'SP.POP.DPND',     # Ratio de dépendance (parfois)
    }
    
    return 'negative' if indicator_code in negative_indicators else 'positive'


def calculate_irc_step1_normalization(df):
    """
    Étape 1 : Normalisation de tous les indicateurs
    
    Args:
        df: DataFrame avec country_code, indicator_code, value
    
    Returns:
        DataFrame pivot avec countries en lignes et indicateurs normalisés en colonnes
    """
    print("\n🔄 Étape 1 : Normalisation des indicateurs...")
    
    # Pivoter pour avoir les indicateurs en colonnes
    df_pivot = df.pivot(index='country_code', columns='indicator_code', values='value')
    
    # Normaliser chaque indicateur
    df_normalized = pd.DataFrame(index=df_pivot.index)
    
    for indicator in df_pivot.columns:
        direction = get_indicator_direction(indicator)
        df_normalized[indicator] = normalize_indicator(df_pivot[indicator], direction)
    
    print(f"   ✓ {len(df_normalized.columns)} indicateurs normalisés")
    print(f"   ✓ {len(df_normalized)} pays")
    
    return df_normalized


def calculate_irc_step2_subpillars(df_normalized):
    """
    Étape 2 : Calcul des sous-piliers (moyenne géométrique des indicateurs)
    
    Args:
        df_normalized: DataFrame avec indicateurs normalisés
    
    Returns:
        DataFrame avec les 7 piliers calculés
    """
    print("\n🔄 Étape 2 : Calcul des sous-piliers (moyenne géométrique)...")
    
    results = pd.DataFrame(index=df_normalized.index)
    
    for pillar_name, pillar_data in IRC_STRUCTURE.items():
        indicators = pillar_data['indicators']
        
        # Filtrer les indicateurs disponibles
        available = [ind for ind in indicators if ind in df_normalized.columns]
        
        if not available:
            print(f"   ⚠️  {pillar_name} : aucun indicateur disponible")
            results[pillar_name] = np.nan
            continue
        
        # Calculer la moyenne géométrique
        # Pour éviter les problèmes avec les 0, on ajoute un epsilon
        epsilon = 1e-10
        pillar_df = df_normalized[available] + epsilon
        
        # Moyenne géométrique = exp(mean(log(x)))
        results[pillar_name] = np.exp(np.log(pillar_df).mean(axis=1))
        
        # Retirer l'epsilon
        results[pillar_name] = results[pillar_name] - epsilon
        
        # S'assurer que les valeurs restent dans [0, 1]
        results[pillar_name] = results[pillar_name].clip(0, 1)
        
        print(f"   ✓ {pillar_name} : {len(available)}/{len(indicators)} indicateurs (poids: {pillar_data['weight']*100:.0f}%)")
    
    return results


def calculate_irc_step3_final(df_pillars):
    """
    Étape 3 : Calcul de l'IRC final (moyenne pondérée des piliers)
    
    Args:
        df_pillars: DataFrame avec les 7 piliers
    
    Returns:
        DataFrame avec IRC final et ranking
    """
    print("\n🔄 Étape 3 : Calcul de l'IRC final (moyenne pondérée)...")
    
    results = pd.DataFrame(index=df_pillars.index)
    
    # Calculer l'IRC comme moyenne pondérée des piliers
    irc_score = pd.Series(0.0, index=df_pillars.index)
    
    for pillar_name, pillar_data in IRC_STRUCTURE.items():
        weight = pillar_data['weight']
        irc_score += df_pillars[pillar_name] * weight
    
    results['irc_score'] = irc_score
    
    # Mettre à l'échelle sur 100
    results['irc_100'] = results['irc_score'] * 100
    
    # Calculer le rang
    results['irc_rank'] = results['irc_100'].rank(ascending=False, method='min')
    
    # Ajouter les piliers
    for pillar in df_pillars.columns:
        results[f'{pillar.lower()}_score'] = df_pillars[pillar] * 100
    
    print(f"   ✓ IRC calculé pour {len(results)} pays")
    print(f"   ✓ Score moyen : {results['irc_100'].mean():.2f}/100")
    print(f"   ✓ Score min : {results['irc_100'].min():.2f}/100")
    print(f"   ✓ Score max : {results['irc_100'].max():.2f}/100")
    
    return results


def save_to_database(conn, df_results, year):
    """
    Sauvegarde les résultats IRC dans la base de données
    
    Args:
        conn: Connexion PostgreSQL
        df_results: DataFrame avec les résultats IRC
        year: Année de calcul
    """
    print(f"\n💾 Sauvegarde dans la base de données...")
    
    cursor = conn.cursor()
    
    # Créer la table si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS irc_results (
        id SERIAL PRIMARY KEY,
        country_id INTEGER REFERENCES country(id),
        year INTEGER NOT NULL,
        irc_score DECIMAL(5, 2),
        irc_rank INTEGER,
        demographie_score DECIMAL(5, 2),
        economie_score DECIMAL(5, 2),
        gouvernance_score DECIMAL(5, 2),
        capital_humain_score DECIMAL(5, 2),
        souverainete_materielle_score DECIMAL(5, 2),
        innovation_score DECIMAL(5, 2),
        environnement_score DECIMAL(5, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(country_id, year)
    );
    """)
    
    # Supprimer les résultats existants pour cette année
    cursor.execute("DELETE FROM irc_results WHERE year = %s", (year,))
    print(f"   ✓ Anciennes données supprimées pour l'année {year}")
    
    # Insérer les nouveaux résultats
    inserted = 0
    skipped = 0
    for country_code in df_results.index:
        # Récupérer l'ID du pays
        cursor.execute("SELECT id FROM country WHERE iso3 = %s", (country_code,))
        result = cursor.fetchone()
        
        if not result:
            print(f"   ⚠️  Pays {country_code} non trouvé dans la base")
            skipped += 1
            continue
        
        country_id = result[0]
        row = df_results.loc[country_code]
        
        # Vérifier que l'IRC n'est pas NaN
        if pd.isna(row['irc_100']):
            print(f"   ⚠️  Pays {country_code} : IRC non calculable (données manquantes)")
            skipped += 1
            continue
        
        cursor.execute("""
        INSERT INTO irc_results (
            country_id, year, irc_score, irc_rank,
            demographie_score, economie_score, gouvernance_score, capital_humain_score,
            souverainete_materielle_score, innovation_score, environnement_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            country_id, year, 
            float(row['irc_100']), int(row['irc_rank']),
            float(row.get('démographie_score', 0) if pd.notna(row.get('démographie_score', 0)) else 0),
            float(row.get('économie_score', 0) if pd.notna(row.get('économie_score', 0)) else 0),
            float(row.get('gouvernance_score', 0) if pd.notna(row.get('gouvernance_score', 0)) else 0),
            float(row.get('capital humain_score', 0) if pd.notna(row.get('capital humain_score', 0)) else 0),
            float(row.get('souveraineté matérielle_score', 0) if pd.notna(row.get('souveraineté matérielle_score', 0)) else 0),
            float(row.get('innovation_score', 0) if pd.notna(row.get('innovation_score', 0)) else 0),
            float(row.get('environnement_score', 0) if pd.notna(row.get('environnement_score', 0)) else 0)
        ))
        inserted += 1
    
    conn.commit()
    print(f"   ✓ {inserted} résultats insérés dans la base")
    if skipped > 0:
        print(f"   ⚠️  {skipped} pays ignorés (données insuffisantes)")


def main():
    """Fonction principale"""
    print("=" * 70)
    print("CALCUL DE L'INDEX DE RÉSILIENCE CIVILISATIONNELLE (IRC)")
    print("Version 1.1 - 28 février 2026")
    print("=" * 70)
    
    # Année de calcul (peut être passée en argument)
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2020
    
    # Connexion à la base
    conn = connect_db()
    
    try:
        # Étape 0 : Charger les données
        df = load_indicator_data(conn, year)
        
        # Étape 1 : Normalisation
        df_normalized = calculate_irc_step1_normalization(df)
        
        # Étape 2 : Calcul des sous-piliers
        df_pillars = calculate_irc_step2_subpillars(df_normalized)
        
        # Étape 3 : Calcul IRC final
        df_results = calculate_irc_step3_final(df_pillars)
        
        # Étape 4 : Sauvegarde
        save_to_database(conn, df_results, year)
        
        # Afficher le top 10
        print("\n🏆 TOP 10 IRC " + str(year))
        print("=" * 70)
        top10 = df_results.nlargest(10, 'irc_100')
        for i, (country, row) in enumerate(top10.iterrows(), 1):
            print(f"{i:2d}. {country:3s} : {row['irc_100']:6.2f}/100")
        
        # Afficher le bottom 10
        print("\n⚠️  BOTTOM 10 IRC " + str(year))
        print("=" * 70)
        bottom10 = df_results.nsmallest(10, 'irc_100')
        for i, (country, row) in enumerate(bottom10.iterrows(), 1):
            print(f"{i:2d}. {country:3s} : {row['irc_100']:6.2f}/100")
        
        print("\n✅ Calcul IRC terminé avec succès !")
        print(f"📊 Résultats disponibles dans la table 'irc_results'")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du calcul IRC : {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()
