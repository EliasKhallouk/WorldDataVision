#!/usr/bin/env python3
"""
Import IMF International Debt Statistics data
External debt indicators for IRC Category 1
"""

import requests
import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    dbname="worlddatavision",
    user="elias",
    host="localhost"
)
cursor = conn.cursor()

print("=" * 80)
print("IMPORT FMI - INTERNATIONAL DEBT STATISTICS")
print("=" * 80)

# IRC indicators to improve
indicators = {
    'DT.DOD.DECT.GN.ZS': 'External debt stocks (% of GNI)',
    'DT.TDS.DECT.EX.ZS': 'Total debt service (% of exports of goods, services and primary income)'
}

# Step 1: Test multiple IMF API endpoints
print("\n1. Test des sources de données FMI...\n")

sources_to_test = [
    {
        'name': 'World Bank IDS Portal API',
        'url_template': 'https://api.worldbank.org/v2/country/{iso3}/indicator/{code}',
        'params': {'format': 'json', 'per_page': 100, 'date': '1980:2023'},
        'type': 'worldbank'
    },
    {
        'name': 'IMF Data Mapper API',
        'url_template': 'https://www.imf.org/external/datamapper/api/v1/{code}/{iso3}',
        'params': {},
        'type': 'imf_mapper'
    },
    {
        'name': 'IMF SDMX REST API',
        'url_template': 'http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IDS/A.{iso3}.{code}',
        'params': {},
        'type': 'imf_sdmx'
    }
]

# Get country ISO3 codes
cursor.execute("SELECT iso3_code FROM country WHERE iso3_code IS NOT NULL AND iso3_code != '' ORDER BY iso3_code")
countries = [row[0] for row in cursor.fetchall()]

print(f"Pays dans la base: {len(countries)}")

# Test each source with a sample country (USA)
test_country = 'USA'
working_source = None

for source in sources_to_test:
    print(f"\nTest: {source['name']}")
    print(f"  URL: {source['url_template']}")
    
    try:
        # Test with external debt indicator
        test_code = 'DT.DOD.DECT.GN.ZS'
        
        if source['type'] == 'worldbank':
            url = source['url_template'].format(iso3=test_country, code=test_code)
        elif source['type'] == 'imf_mapper':
            # IMF might use different codes - try variations
            url = source['url_template'].format(code='DEBT', iso3=test_country)
        else:
            # SDMX might need specific indicator codes
            url = source['url_template'].format(iso3=test_country, code=test_code)
        
        response = requests.get(url, params=source['params'], timeout=30)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got valid data
            has_data = False
            
            if source['type'] == 'worldbank':
                if len(data) > 1 and data[1]:
                    has_data = True
                    print(f"  ✓ Données trouvées: {len(data[1])} observations")
                    # Show sample
                    for item in data[1][:3]:
                        if item.get('value'):
                            print(f"    {item['date']}: {item['value']:.2f}")
            
            elif source['type'] == 'imf_mapper':
                if 'values' in data or 'data' in data:
                    has_data = True
                    print(f"  ✓ Structure trouvée")
            
            elif source['type'] == 'imf_sdmx':
                if 'CompactData' in data:
                    has_data = True
                    print(f"  ✓ Structure SDMX trouvée")
            
            if has_data and not working_source:
                working_source = source
                print(f"  ✅ SOURCE FONCTIONNELLE")
        else:
            print(f"  ✗ Échec HTTP")
            
    except Exception as e:
        print(f"  ✗ Erreur: {str(e)[:100]}")

# Step 2: If we found a working source, proceed with import
if not working_source:
    print("\n" + "=" * 80)
    print("❌ AUCUNE SOURCE API FONCTIONNELLE")
    print("=" * 80)
    print("\nAlternatives à explorer:")
    print("1. Télécharger bulk file FMI IDS (si disponible)")
    print("2. Utiliser OECD External Debt Statistics")
    print("3. Banques régionales de développement (AfDB, ADB, IDB)")
    print("\nVérifier manuellement:")
    print("- https://data.imf.org/")
    print("- https://www.imf.org/external/datamapper/datasets")
    print("- https://databank.worldbank.org/source/international-debt-statistics")
    
    cursor.close()
    conn.close()
    exit(1)

print("\n" + "=" * 80)
print(f"✓ SOURCE SÉLECTIONNÉE: {working_source['name']}")
print("=" * 80)

# Step 3: Import data
print("\n2. Import des données...\n")

stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'new_values': 0,
    'averaged_values': 0,
    'errors': 0
}

for indicator_code in indicators.keys():
    print(f"\nIndicateur: {indicator_code}")
    print(f"  {indicators[indicator_code]}")
    
    # Get current coverage
    cursor.execute("""
        SELECT COUNT(DISTINCT country_id)
        FROM indicator_value
        WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)
    """, (indicator_code,))
    
    current_coverage = cursor.fetchone()[0]
    print(f"  Couverture actuelle: {current_coverage} pays")
    
    new_countries = set()
    
    for country in countries[:10]:  # Test with first 10 countries
        stats['total_requests'] += 1
        
        try:
            if working_source['type'] == 'worldbank':
                url = working_source['url_template'].format(iso3=country, code=indicator_code)
                response = requests.get(url, params=working_source['params'], timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if len(data) > 1 and data[1]:
                        stats['successful_requests'] += 1
                        
                        # Get country ID
                        cursor.execute("SELECT id FROM country WHERE iso3_code = %s", (country,))
                        country_result = cursor.fetchone()
                        
                        if not country_result:
                            continue
                        
                        country_id = country_result[0]
                        new_countries.add(country_id)
                        
                        # Get indicator ID
                        cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
                        indicator_id = cursor.fetchone()[0]
                        
                        # Process values
                        for item in data[1]:
                            year = int(item['date'])
                            value = item.get('value')
                            
                            if value is None:
                                continue
                            
                            # Check if value exists
                            cursor.execute("""
                                SELECT id, value, source 
                                FROM indicator_value 
                                WHERE indicator_id = %s AND country_id = %s AND year = %s
                            """, (indicator_id, country_id, year))
                            
                            existing = cursor.fetchone()
                            
                            if existing:
                                # Average with existing
                                existing_id, existing_value, existing_source = existing
                                
                                # Avoid duplicating WB data
                                if 'World Bank' in existing_source and 'IMF' not in existing_source:
                                    new_value = (existing_value + value) / 2
                                    new_source = existing_source + " + IMF IDS"
                                    
                                    cursor.execute("""
                                        UPDATE indicator_value 
                                        SET value = %s, source = %s 
                                        WHERE id = %s
                                    """, (new_value, new_source, existing_id))
                                    
                                    stats['averaged_values'] += 1
                            else:
                                # Insert new value
                                cursor.execute("""
                                    INSERT INTO indicator_value 
                                    (indicator_id, country_id, year, value, source) 
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (indicator_id, country_id, year, value, 'IMF International Debt Statistics'))
                                
                                stats['new_values'] += 1
                        
        except Exception as e:
            stats['errors'] += 1
            if stats['errors'] <= 3:
                print(f"    Erreur {country}: {str(e)[:50]}")
    
    print(f"  Nouveaux pays avec données: {len(new_countries)}")

# Commit changes
conn.commit()

# Final statistics
print("\n" + "=" * 80)
print("RÉSULTATS")
print("=" * 80)
print(f"Requêtes totales: {stats['total_requests']}")
print(f"Requêtes réussies: {stats['successful_requests']}")
print(f"Nouvelles valeurs: {stats['new_values']}")
print(f"Valeurs moyennées: {stats['averaged_values']}")
print(f"Erreurs: {stats['errors']}")

# Final coverage
print("\nCouverture finale:")
for indicator_code in indicators.keys():
    cursor.execute("""
        SELECT COUNT(DISTINCT country_id)
        FROM indicator_value
        WHERE indicator_id = (SELECT id FROM indicator WHERE code = %s)
    """, (indicator_code,))
    
    final_coverage = cursor.fetchone()[0]
    print(f"  {indicator_code}: {final_coverage} pays")

cursor.close()
conn.close()

print("\n✓ Import terminé")
