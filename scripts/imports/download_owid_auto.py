#!/usr/bin/env python3
"""
Script pour télécharger automatiquement les datasets Our World in Data
via leur API/CSV GitHub.
"""

import requests
import os

OWID_DIR = '/home/elias/PROJECT/WorldDataVision/Data/IRC/OWID'

# Mapping des datasets OWID (nom court utilisé dans les URLs)
OWID_DATASETS = {
    'literacy-rate-adults': 'literacy-rates-among-adults.csv',
    'researchers-in-rd': 'researchers-in-rd-per-million-people.csv',
    'research-spending-gdp': 'research-and-development-expenditure-of-gdp.csv',
    'per-capita-electricity-consumption': 'per-capita-electricity-use.csv',
    'per-capita-energy-use': 'per-capita-energy-use.csv',
    'cereal-yield': 'cereal-yield.csv',
    'water-stress': 'water-stress.csv',
    'military-expenditure-as-a-share-of-gdp': 'military-expenditure-as-a-share-of-gdp.csv',
    'energy-imports': 'energy-imports-as-a-share-of-energy-use.csv',
    'fossil-fuels-share-energy': 'fossil-fuels-share-energy.csv',
    'patent-applications-residents': 'patent-applications-by-residents.csv',
    'tax-revenues-as-a-share-of-gdp-ictd': 'total-tax-revenue-gdp.csv',
}


def download_owid_dataset(chart_name, filename):
    """
    Télécharge un dataset OWID depuis leur API.
    URL format: https://ourworldindata.org/grapher/{chart_name}.csv?v=1&csvType=full
    """
    url = f"https://ourworldindata.org/grapher/{chart_name}.csv?v=1&csvType=full&useColumnShortNames=false"
    
    print(f"📥 Téléchargement: {chart_name}...")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Vérifier que c'est bien du CSV
        content = response.text
        if not content.startswith('Entity') and 'Year' not in content[:200]:
            print(f"   ⚠️ Le contenu ne semble pas être un CSV valide")
            return False
        
        # Sauvegarder le fichier
        file_path = os.path.join(OWID_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Vérifier la taille
        file_size = os.path.getsize(file_path)
        rows = len(content.split('\n')) - 1
        
        print(f"   ✅ Téléchargé: {file_size:,} bytes, ~{rows:,} lignes")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        return False


def main():
    print("="*80)
    print("📥 TÉLÉCHARGEMENT AUTOMATIQUE DES DATASETS OUR WORLD IN DATA")
    print("="*80)
    print(f"Dossier destination: {OWID_DIR}\n")
    
    if not os.path.exists(OWID_DIR):
        os.makedirs(OWID_DIR)
        print(f"✓ Dossier créé: {OWID_DIR}\n")
    
    success = 0
    failed = 0
    
    for chart_name, filename in OWID_DATASETS.items():
        if download_owid_dataset(chart_name, filename):
            success += 1
        else:
            failed += 1
        print()
    
    print("="*80)
    print("📊 RÉSUMÉ")
    print("="*80)
    print(f"✅ Succès: {success}/{len(OWID_DATASETS)}")
    print(f"❌ Échecs: {failed}/{len(OWID_DATASETS)}")
    
    if failed > 0:
        print("\n⚠️ Certains fichiers n'ont pas pu être téléchargés.")
        print("Téléchargez-les manuellement depuis:")
        print("https://ourworldindata.org/charts")
        print("\nConsultez OWID_IMPORT_GUIDE.md pour les instructions détaillées.")
    else:
        print("\n✅ Tous les fichiers ont été téléchargés avec succès!")
        print("Vous pouvez maintenant exécuter: python3 import_owid_data.py")
    
    print(f"\n📁 Fichiers téléchargés dans: {OWID_DIR}")


if __name__ == '__main__':
    main()
