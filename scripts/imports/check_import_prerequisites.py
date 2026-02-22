#!/usr/bin/env python3
"""
Script de vérification pré-import
Vérifie que tout est prêt pour l'import IMF
"""

import sys
import os

def check_python_version():
    """Vérifie la version de Python."""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3:
        print("❌ Python 3+ requis")
        return False
    return True

def check_psycopg2():
    """Vérifie que psycopg2 est installé."""
    try:
        import psycopg2
        print(f"✅ psycopg2 installé (version {psycopg2.__version__})")
        return True
    except ImportError:
        print("❌ psycopg2 non installé")
        print("   → Installer avec: pip install psycopg2-binary")
        return False

def check_csv_file():
    """Vérifie que le fichier CSV existe."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '../../Data/IRC/imf-dm-export-20260221.csv')
    
    if os.path.exists(csv_path):
        size = os.path.getsize(csv_path)
        print(f"✅ Fichier CSV trouvé ({size:,} octets)")
        print(f"   📂 {csv_path}")
        return True
    else:
        print(f"❌ Fichier CSV non trouvé")
        print(f"   📂 Recherché: {csv_path}")
        return False

def check_database_connection():
    """Vérifie la connexion à la base de données."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            user='elias',
            host='localhost',
            database='worlddatavision',
            password='MaBaseDeDonnee',
            port=5432
        )
        cursor = conn.cursor()
        
        # Vérifier que la table indicator existe
        cursor.execute("""
            SELECT COUNT(*) FROM indicator 
            WHERE code = 'GC.DOD.TOTL.GD.ZS'
        """)
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Connexion DB OK + Indicateur GC.DOD.TOTL.GD.ZS trouvé")
        else:
            print(f"⚠️  Connexion DB OK mais indicateur GC.DOD.TOTL.GD.ZS absent")
            print(f"   → L'indicateur sera créé lors de l'import")
        
        # Compter les pays
        cursor.execute("SELECT COUNT(*) FROM country")
        nb_pays = cursor.fetchone()[0]
        print(f"✅ {nb_pays} pays dans la base")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion DB: {e}")
        return False

def main():
    """Fonction principale."""
    print("═" * 60)
    print("🔍 Vérification pré-import IMF")
    print("═" * 60)
    print()
    
    checks = [
        ("Python version", check_python_version),
        ("Module psycopg2", check_psycopg2),
        ("Fichier CSV source", check_csv_file),
        ("Connexion base de données", check_database_connection),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"📋 {name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results.append(False)
        print()
    
    print("═" * 60)
    
    if all(results):
        print("✅ Toutes les vérifications sont OK!")
        print("🚀 Vous pouvez lancer l'import:")
        print("   python3 import_imf_debt_data.py")
        print("═" * 60)
        return 0
    else:
        print("❌ Certaines vérifications ont échoué")
        print("⚠️  Corriger les problèmes avant de lancer l'import")
        print("═" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
