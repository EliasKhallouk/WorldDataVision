#!/usr/bin/env python3
import requests
import json

# Test simple: est-ce que l'API World Bank a plus de données que ce qu'on a déjà?
print("TEST RAPIDE - Comparaison couverture World Bank API vs BDD\n")

# Indicateur à tester
code = 'DT.DOD.DECT.GN.ZS'

# Test quelques pays
test_countries = ['USA', 'FRA', 'DEU', 'CHN', 'BRA', 'IND', 'ZAF', 'NGA', 'ARG', 'THA']

print(f"Indicateur: {code}")
print(f"Test sur {len(test_countries)} pays échantillon\n")

for iso3 in test_countries:
    url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{code}"
    params = {'format': 'json', 'per_page': 100, 'date': '2020:2023'}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 1 and data[1]:
                values = [v for v in data[1] if v.get('value') is not None]
                
                if values:
                    latest = values[0]
                    print(f"{iso3}: ✓ {len(values)} valeurs | Dernier: {latest['date']} = {latest['value']:.2f}%")
                else:
                    print(f"{iso3}: ✗ Pas de valeurs")
            else:
                print(f"{iso3}: ✗ Pas de données")
        else:
            print(f"{iso3}: ✗ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"{iso3}: ✗ Erreur: {e}")

print("\n" + "="*60)
print("Si données trouvées ✓ → L'API World Bank donne accès aux données")
print("Prochaine étape: Vérifier si ce sont des données IMF IDS ou juste World Bank")
print("\nSource officielle IMF IDS:")
print("https://databank.worldbank.org/source/international-debt-statistics")
