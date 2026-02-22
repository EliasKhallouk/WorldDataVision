#!/usr/bin/env python3
"""
Script pour télécharger automatiquement les datasets de sources alternatives
pour compléter les indicateurs IRC.
"""

import requests
import os
import sys

BASE_DIR = '/home/elias/PROJECT/WorldDataVision/Data/IRC'

# URLs directes des datasets téléchargeables automatiquement
DATASETS = {
    'OECD': {
        'revenue_statistics': {
            'url': 'https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/REV/all/all?format=csv',
            'file': 'revenue_statistics.csv',
            'indicator': 'GC.TAX.TOTL.GD.ZS',
            'description': 'Revenus fiscaux (% PIB)'
        },
        'rd_expenditure': {
            'url': 'https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/MSTI_PUB/all/all?format=csv',
            'file': 'msti_rd_statistics.csv',
            'indicator': 'GB.XPD.RSDV.GD.ZS + SP.POP.SCIE.RD.P6',
            'description': 'Dépenses R&D + Chercheurs'
        },
        'external_debt': {
            'url': 'https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/QASA_TABLE8/all/all?format=csv',
            'file': 'external_debt.csv',
            'indicator': 'DT.DOD.DECT.GN.ZS',
            'description': 'Dette externe'
        },
        'patent_statistics': {
            'url': 'https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PATS_IPC/all/all?format=csv',
            'file': 'patent_statistics.csv',
            'indicator': 'IP.PAT.RESD',
            'description': 'Brevets résidents'
        },
    },
    # Les sources nécessitant téléchargement manuel
    'MANUAL_DOWNLOAD': {
        'SIPRI': {
            'url': 'https://milex.sipri.org/sipri',
            'file': 'military_expenditure.xlsx',
            'indicator': 'MS.MIL.XPND.GD.ZS',
            'description': 'Dépenses militaires - Télécharger puis Export to Excel'
        },
        'FAO': {
            'url': 'https://www.fao.org/aquastat/statistics/query/index.html',
            'file': 'aquastat_water_stress.csv',
            'indicator': 'ER.H2O.FWST.ZS',
            'description': 'Stress hydrique - Télécharger manuellement'
        },
        'WIPO': {
            'url': 'https://www3.wipo.int/ipstats/index.htm?tab=patent',
            'file': 'wipo_patents.csv',
            'indicator': 'IP.PAT.RESD',
            'description': 'Brevets WIPO - Télécharger manuellement'
        },
        'BP_Energy': {
            'url': 'https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html',
            'file': 'bp_statistical_review.xlsx',
            'indicator': 'EG.USE.PCAP.KG.OE + EG.USE.COMM.FO.ZS',
            'description': 'BP Energy Review - Télécharger Excel'
        },
        'IEA_Energy': {
            'url': 'https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser',
            'file': 'iea_energy_stats.csv',
            'indicator': 'EG.IMP.CONS.ZS + EG.USE.ELEC.KH.PC',
            'description': 'IEA Energy - Nécessite compte gratuit'
        },
    }
}


def download_dataset(source, dataset_name, dataset_info, dest_dir):
    """Télécharge un dataset depuis une URL"""
    url = dataset_info['url']
    filename = dataset_info['file']
    filepath = os.path.join(dest_dir, filename)
    
    print(f"\n📥 Téléchargement: {source} - {dataset_name}")
    print(f"   URL: {url}")
    print(f"   Destination: {filepath}")
    
    try:
        response = requests.get(url, timeout=60, allow_redirects=True)
        
        # Vérifier si c'est une redirection vers page de login
        if 'login' in response.url.lower() or 'signin' in response.url.lower():
            print(f"   ⚠️ Nécessite authentification - téléchargement manuel requis")
            return False
        
        response.raise_for_status()
        
        # Vérifier que c'est bien du CSV ou du contenu téléchargeable
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type and 'csv' not in content_type:
            print(f"   ⚠️ Réponse HTML au lieu de CSV - URL peut nécessiter interaction")
            return False
        
        # Sauvegarder le fichier
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filepath)
        
        if file_size < 1000:  # Fichier trop petit, probablement une erreur
            print(f"   ⚠️ Fichier trop petit ({file_size} bytes) - probablement une erreur")
            os.remove(filepath)
            return False
        
        print(f"   ✅ Téléchargé: {file_size:,} bytes")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        return False


def main():
    print("="*100)
    print("📥 TÉLÉCHARGEMENT AUTOMATIQUE DES SOURCES ALTERNATIVES IRC")
    print("="*100)
    
    success_count = 0
    failed_count = 0
    manual_count = len(DATASETS.get('MANUAL_DOWNLOAD', {}))
    
    # Téléchargements automatiques
    for source, datasets in DATASETS.items():
        if source == 'MANUAL_DOWNLOAD':
            continue
        
        dest_dir = os.path.join(BASE_DIR, source)
        os.makedirs(dest_dir, exist_ok=True)
        
        print(f"\n{'='*100}")
        print(f"🌐 SOURCE: {source}")
        print(f"{'='*100}")
        
        for dataset_name, dataset_info in datasets.items():
            if download_dataset(source, dataset_name, dataset_info, dest_dir):
                success_count += 1
            else:
                failed_count += 1
    
    # Résumé
    print(f"\n{'='*100}")
    print("📊 RÉSUMÉ DU TÉLÉCHARGEMENT")
    print(f"{'='*100}")
    print(f"✅ Téléchargements réussis: {success_count}")
    print(f"❌ Téléchargements échoués: {failed_count}")
    print(f"📝 Téléchargements manuels requis: {manual_count}")
    
    # Liste des téléchargements manuels
    if manual_count > 0:
        print(f"\n{'='*100}")
        print("📋 DATASETS À TÉLÉCHARGER MANUELLEMENT:")
        print(f"{'='*100}")
        
        for source, info in DATASETS['MANUAL_DOWNLOAD'].items():
            print(f"\n🔗 {source}: {info['description']}")
            print(f"   Indicateur: {info['indicator']}")
            print(f"   URL: {info['url']}")
            print(f"   Sauvegarder dans: {os.path.join(BASE_DIR, source.split('_')[0], info['file'])}")
    
    print(f"\n📁 Fichiers téléchargés dans: {BASE_DIR}")
    print("\n💡 Consultez ALTERNATIVE_SOURCES_IRC.md pour les instructions détaillées")


if __name__ == '__main__':
    main()
