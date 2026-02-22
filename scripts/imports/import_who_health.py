#!/usr/bin/env python3
"""
Import données OMS pour indicateurs santé IRC
"""

import psycopg2
import requests
import time
from collections import defaultdict

# Connexion BDD
conn = psycopg2.connect(
    dbname="worlddatavision",
    user="elias",
    password="MaBaseDeDonnee",
    host="localhost"
)
cursor = conn.cursor()

print("=" * 80)
print("IMPORT OMS - INDICATEURS SANTÉ")
print("=" * 80)
print()

# Mapping IRC → OMS (codes validés)
who_mappings = {
    'SP.DYN.IMRT.IN': {
        'who_code': 'MDG_0000000001',
        'name': 'Mortalité infantile',
        'description': 'Infant mortality rate (deaths per 1000 live births)'
    },
    'SP.DYN.LE00.IN': {
        'who_code': 'WHOSIS_000001',
        'name': 'Espérance de vie',
        'description': 'Life expectancy at birth (years)'
    },
    'SH.MED.PHYS.ZS': {
        'who_code': 'HRH_26',
        'name': 'Médecins par 1000',
        'description': 'Physicians density (per 1000 population)'
    },
    'SH.MED.BEDS.ZS': {
        'who_code': 'hospital beds',  # À trouver code exact
        'name': 'Lits d\'hôpital',
        'description': 'Hospital beds (per 1000 population)',
        'skip': True  # Pas de code exact trouvé
    },
    'SH.XPD.CHEX.GD.ZS': {
        'who_code': 'che_pc_usd',
        'name': 'Dépenses de santé',
        'description': 'Current health expenditure (CHE) per capita in US$'
    }
}

WHO_BASE = "https://ghoapi.azureedge.net/api"

# Récupérer pays de la BDD
cursor.execute("SELECT id, iso3, name FROM country WHERE iso3 IS NOT NULL AND iso3 != ''")
countries = {row[1]: {'id': row[0], 'name': row[2]} for row in cursor.fetchall()}

print(f"✓ {len(countries)} pays dans la BDD\n")

stats = {
    'total_indicators': 0,
    'total_requests': 0,
    'successful_requests': 0,
    'new_values': 0,
    'averaged_values': 0,
    'errors': 0,
    'skipped': 0
}

for irc_code, mapping in who_mappings.items():
    if mapping.get('skip'):
        stats['skipped'] += 1
        continue
    
    who_code = mapping['who_code']
    
    print("=" * 80)
    print(f"INDICATEUR: {irc_code}")
    print(f"  Nom: {mapping['name']}")
    print(f"  Code OMS: {who_code}")
    print("=" * 80)
    print()
    
    # Vérifier couverture actuelle
    cursor.execute("""
        SELECT COUNT(DISTINCT country_id)
        FROM indicator_value
        WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)
    """, (irc_code,))
    
    current_coverage = cursor.fetchone()[0]
    print(f"Couverture actuelle: {current_coverage} pays")
    
    # Télécharger données OMS
    print(f"Téléchargement depuis OMS...")
    stats['total_requests'] += 1
    
    try:
        url = f"{WHO_BASE}/{who_code}"
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            values = data.get('value', [])
            
            print(f"✓ {len(values)} observations OMS reçues")
            
            if not values:
                print(f"✗ Aucune donnée\n")
                continue
            
            stats['successful_requests'] += 1
            
            # Obtenir l'ID de l'indicateur
            cursor.execute("SELECT id FROM indicator WHERE code = %s", (irc_code,))
            indicator_result = cursor.fetchone()
            
            if not indicator_result:
                print(f"✗ Indicateur {irc_code} non trouvé en BDD\n")
                continue
            
            indicator_id = indicator_result[0]
            
            # Regrouper par pays et année
            data_by_country_year = defaultdict(list)
            
            for value in values:
                iso3 = value.get('SpatialDim')
                year = value.get('TimeDim')
                numeric_value = value.get('NumericValue')
                
                if iso3 and year and numeric_value is not None:
                    try:
                        year = int(year)
                        if iso3 in countries:
                            data_by_country_year[(iso3, year)].append(float(numeric_value))
                    except (ValueError, TypeError):
                        continue
            
            print(f"✓ {len(data_by_country_year)} paires pays-année uniques")
            
            # Moyenner si plusieurs valeurs par pays-année
            processed_data = {}
            for (iso3, year), vals in data_by_country_year.items():
                processed_data[(iso3, year)] = sum(vals) / len(vals)
            
            # Insérer/mettre à jour en BDD
            new_values = 0
            averaged_values = 0
            new_countries = set()
            
            # Traiter par batch pour performance
            batch_size = 1000
            items = list(processed_data.items())
            
            for i in range(0, len(items), batch_size):
                batch = items[i:i+batch_size]
                
                for (iso3, year), value in batch:
                    country_id = countries[iso3]['id']
                    
                    # Vérifier si existe
                    cursor.execute("""
                        SELECT id, value, source 
                        FROM indicator_value 
                        WHERE indicator_id = %s AND country_id = %s AND year = %s
                    """, (indicator_id, country_id, year))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Moyenner avec valeur existante
                        existing_id, existing_value, existing_source = existing
                        existing_source = existing_source or ""
                        
                        # Vérifier si OMS déjà dans la source
                        if 'OMS' not in existing_source and 'WHO' not in existing_source:
                            new_value = (existing_value + value) / 2
                            new_source = existing_source + " + OMS (WHO GHO)" if existing_source else "OMS (WHO GHO)"
                            
                            cursor.execute("""
                                UPDATE indicator_value 
                                SET value = %s, source = %s 
                                WHERE id = %s
                            """, (new_value, new_source, existing_id))
                            
                            averaged_values += 1
                    else:
                        # Nouvelle valeur
                        cursor.execute("""
                            INSERT INTO indicator_value 
                            (indicator_id, country_id, year, value, source) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (indicator_id, country_id, year, value, 'OMS (WHO Global Health Observatory)'))
                        
                        new_values += 1
                        new_countries.add(country_id)
                
                # Commit par batch
                if (i // batch_size) % 5 == 0:
                    conn.commit()
                    print(f"  ... traité {min(i+batch_size, len(items))}/{len(items)}")
            
            # Commit après chaque indicateur
            conn.commit()
            
            # Vérifier nouvelle couverture
            cursor.execute("""
                SELECT COUNT(DISTINCT country_id)
                FROM indicator_value
                WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)
            """, (irc_code,))
            
            new_coverage = cursor.fetchone()[0]
            gain = new_coverage - current_coverage
            
            print(f"\n✅ RÉSULTAT:")
            print(f"  Nouvelles valeurs: {new_values}")
            print(f"  Valeurs moyennées: {averaged_values}")
            print(f"  Nouveaux pays: {len(new_countries)}")
            print(f"  Couverture: {current_coverage} → {new_coverage} (+{gain})")
            print()
            
            stats['new_values'] += new_values
            stats['averaged_values'] += averaged_values
            stats['total_indicators'] += 1
            
        else:
            print(f"✗ Erreur HTTP: {response.status_code}\n")
            stats['errors'] += 1
            
    except Exception as e:
        print(f"✗ Erreur: {e}\n")
        stats['errors'] += 1
    
    time.sleep(1)  # Rate limiting

# Mettre à jour les sources dans la table indicator
print("=" * 80)
print("MISE À JOUR DES SOURCES")
print("=" * 80)
print()

for irc_code in who_mappings.keys():
    if who_mappings[irc_code].get('skip'):
        continue
    
    cursor.execute("""
        SELECT source 
        FROM indicator 
        WHERE code = %s
    """, (irc_code,))
    
    result = cursor.fetchone()
    if result:
        current_source = result[0] or ""
        
        if 'OMS' not in current_source and 'WHO' not in current_source:
            new_source = current_source + " + OMS (WHO GHO)" if current_source else "OMS (WHO Global Health Observatory)"
            
            cursor.execute("""
                UPDATE indicator 
                SET source = %s 
                WHERE code = %s
            """, (new_source, irc_code))
            
            print(f"✓ {irc_code}: Source mise à jour")

conn.commit()

# Statistiques finales
print("\n" + "=" * 80)
print("STATISTIQUES FINALES")
print("=" * 80)
print()
print(f"Indicateurs traités: {stats['total_indicators']}/{len(who_mappings) - stats['skipped']}")
print(f"Requêtes totales: {stats['total_requests']}")
print(f"Requêtes réussies: {stats['successful_requests']}")
print(f"Nouvelles valeurs: {stats['new_values']}")
print(f"Valeurs moyennées: {stats['averaged_values']}")
print(f"Erreurs: {stats['errors']}")
print(f"Ignorés: {stats['skipped']}")

print("\n" + "=" * 80)
print("COUVERTURE FINALE")
print("=" * 80)
print()

for irc_code in who_mappings.keys():
    cursor.execute("""
        SELECT COUNT(DISTINCT country_id)
        FROM indicator_value
        WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)
    """, (irc_code,))
    
    coverage = cursor.fetchone()[0]
    status = "🟢" if coverage >= 200 else "🟡" if coverage >= 150 else "🔴"
    print(f"{status} {irc_code}: {coverage} pays")

cursor.close()
conn.close()

print("\n✅ Import OMS terminé")
