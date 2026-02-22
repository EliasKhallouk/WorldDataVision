#!/usr/bin/env python3
"""
Analyse des indicateurs de santé IRC et test API OMS
"""

import psycopg2
import pandas as pd
import requests
import time

# Connexion BDD
conn = psycopg2.connect(
    dbname="worlddatavision",
    user="elias",
    password="MaBaseDeDonnee",
    host="localhost"
)

print("=" * 80)
print("ANALYSE INDICATEURS SANTÉ - IRC")
print("=" * 80)
print()

# Récupérer les indicateurs de santé (Catégorie 2)
query = """
SELECT 
    i.code,
    i.name,
    i.description,
    i.source,
    i.unit,
    COUNT(DISTINCT iv.country_id) as country_count,
    MIN(iv.year) as first_year,
    MAX(iv.year) as last_year,
    COUNT(*) as total_values
FROM indicator i
LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
WHERE i.category_id = 2
GROUP BY i.id, i.code, i.name, i.description, i.source, i.unit
ORDER BY country_count ASC;
"""

df = pd.read_sql(query, conn)

print(f"✓ {len(df)} indicateurs de santé trouvés\n")
print("=" * 80)
print("COUVERTURE ACTUELLE")
print("=" * 80)
print()

for _, row in df.iterrows():
    status = "🔴" if row['country_count'] < 150 else "🟡" if row['country_count'] < 200 else "🟢"
    print(f"{status} {row['code']}")
    print(f"   {row['name']}")
    print(f"   Couverture: {row['country_count']} pays")
    print(f"   Source: {row['source']}")
    print(f"   Période: {row['first_year']} - {row['last_year']}")
    print()

# Trier par priorité (plus faible couverture)
print("=" * 80)
print("PRIORITÉS (couverture la plus faible)")
print("=" * 80)
print()

priorities = df.nsmallest(5, 'country_count')
for idx, row in priorities.iterrows():
    print(f"{idx+1}. {row['code']}: {row['country_count']} pays - {row['name']}")

print("\n" + "=" * 80)
print("TEST API OMS (WHO Global Health Observatory)")
print("=" * 80)
print()

# API OMS - Global Health Observatory
# Documentation: https://www.who.int/data/gho/info/gho-odata-api

WHO_BASE = "https://ghoapi.azureedge.net/api"

# Mapping IRC codes vers codes OMS possibles
who_mappings = {
    'SP.DYN.IMRT.IN': {
        'who_codes': ['MDG_0000000001', 'INFANTMORTALITY', 'CME_MRM0'],
        'name': 'Infant mortality rate'
    },
    'SP.DYN.LE00.IN': {
        'who_codes': ['WHOSIS_000001', 'LIFE_0000000030', 'LIFEXPECTANCY'],
        'name': 'Life expectancy at birth'
    },
    'SH.DYN.MORT': {
        'who_codes': ['MDG_0000000007', 'CHILDMORTALITY', 'CME_MRM1'],
        'name': 'Under-5 mortality rate'
    },
    'SH.STA.MMRT': {
        'who_codes': ['MDG_0000000026', 'MATERNALMORTALITY', 'MMR'],
        'name': 'Maternal mortality ratio'
    },
    'SH.IMM.MEAS': {
        'who_codes': ['WHS4_100', 'IMMUNIZATION_MEASLES', 'MCV'],
        'name': 'Measles immunization coverage'
    }
}

print("1. Test de la structure API OMS...")
print()

try:
    # Lister les indicateurs disponibles
    url = f"{WHO_BASE}/Indicator"
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        indicators = data.get('value', [])
        print(f"✓ API accessible: {len(indicators)} indicateurs OMS disponibles")
        
        # Chercher nos indicateurs
        print("\n2. Recherche indicateurs IRC dans catalogue OMS...")
        print()
        
        health_keywords = ['mortality', 'life expectancy', 'immunization', 'maternal', 'infant', 'child']
        found_indicators = []
        
        for ind in indicators[:100]:  # Échantillon
            code = ind.get('IndicatorCode', '')
            name = ind.get('IndicatorName', '').lower()
            
            if any(kw in name for kw in health_keywords):
                found_indicators.append({
                    'code': code,
                    'name': ind.get('IndicatorName', '')
                })
        
        print(f"✓ {len(found_indicators)} indicateurs santé potentiels trouvés:")
        for ind in found_indicators[:10]:
            print(f"  - {ind['code']}: {ind['name']}")
        
    else:
        print(f"✗ API non accessible: HTTP {response.status_code}")
        
except Exception as e:
    print(f"✗ Erreur API: {e}")

print("\n" + "=" * 80)
print("3. Test récupération données (échantillon)")
print("=" * 80)
print()

# Tester avec un indicateur spécifique
test_indicator = 'MDG_0000000001'  # Infant mortality
test_country = 'FRA'

try:
    url = f"{WHO_BASE}/{test_indicator}"
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        values = data.get('value', [])
        
        if values:
            print(f"✓ Données trouvées pour {test_indicator}")
            print(f"  Total observations: {len(values)}")
            
            # Filtrer pour la France
            fra_data = [v for v in values if v.get('SpatialDim') == test_country]
            
            if fra_data:
                print(f"  France: {len(fra_data)} observations")
                latest = sorted(fra_data, key=lambda x: x.get('TimeDim', 0), reverse=True)[0]
                print(f"  Dernier: {latest.get('TimeDim')} = {latest.get('NumericValue')}")
            else:
                print(f"  Pas de données France")
    else:
        print(f"✗ Échec: HTTP {response.status_code}")
        
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)
print()

print("Indicateurs santé IRC identifiés:")
for _, row in df.iterrows():
    print(f"  • {row['code']}: {row['country_count']} pays")

print("\nProchaine étape:")
print("  1. Mapper codes IRC → codes OMS exact")
print("  2. Télécharger données OMS pour chaque indicateur")
print("  3. Valider compatibilité sémantique")
print("  4. Importer si validation OK")

conn.close()
print("\n✓ Analyse terminée")
