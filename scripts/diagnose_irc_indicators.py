#!/usr/bin/env python3
"""
Étape 1 : Diagnostic des indicateurs IRC déjà dans la base de données.
Compare les indicateurs IRC à télécharger avec ceux déjà présents.
"""

import json
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Configuration DB
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "worlddatavision")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Liste des indicateurs IRC qu'on a téléchargé
IRC_DATA_DIR = Path(__file__).parent.parent / "Data" / "IRC"
METADATA_FILE = IRC_DATA_DIR / "metadata.json"

def load_irc_indicators():
    """Charge la liste des indicateurs IRC depuis metadata.json"""
    if not METADATA_FILE.exists():
        print(f"❌ Fichier metadata non trouvé: {METADATA_FILE}")
        return {}
    
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    indicators = {}
    for ind in data.get("indicators", []):
        indicators[ind["code"]] = ind["name"]
    
    return indicators

def get_db_indicators():
    """Récupère les indicateurs déjà dans la base de données"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT code, name FROM indicator;")
        indicators = {}
        for row in cursor.fetchall():
            indicators[row["code"]] = row["name"]
        
        cursor.close()
        conn.close()
        
        return indicators
    except Exception as e:
        print(f"❌ Erreur de connexion à la base: {e}")
        return {}

def main():
    print("=" * 80)
    print("🔍 DIAGNOSTIC DES INDICATEURS IRC")
    print("=" * 80)
    
    # Charger les indicateurs IRC
    irc_indicators = load_irc_indicators()
    print(f"\n📊 Indicateurs IRC à intégrer: {len(irc_indicators)}")
    
    if not irc_indicators:
        print("❌ Aucun indicateur IRC trouvé dans metadata.json")
        return
    
    # Charger les indicateurs de la base
    db_indicators = get_db_indicators()
    print(f"💾 Indicateurs déjà dans la base: {len(db_indicators)}")
    
    # Diagnostic
    already_present = []
    missing = []
    
    for code, name in irc_indicators.items():
        if code in db_indicators:
            already_present.append((code, name, db_indicators[code]))
        else:
            missing.append((code, name))
    
    # Affichage
    print("\n" + "=" * 80)
    print(f"✅ DÉJÀ PRÉSENTS: {len(already_present)}")
    print("=" * 80)
    
    if already_present:
        for code, name, db_name in already_present:
            match = "✅" if name.lower() == db_name.lower() else "⚠️"
            print(f"{match} {code:20s} | IRC: {name}")
            if name.lower() != db_name.lower():
                print(f"                      | BDD: {db_name}")
    else:
        print("(aucun)")
    
    print("\n" + "=" * 80)
    print(f"❌ À AJOUTER: {len(missing)}")
    print("=" * 80)
    
    if missing:
        for code, name in missing:
            print(f"  {code:20s} | {name}")
    else:
        print("(tous les indicateurs sont déjà présents)")
    
    # Sauvegarde du diagnostic
    diagnostic = {
        "total_irc_indicators": len(irc_indicators),
        "already_present": len(already_present),
        "missing": len(missing),
        "to_add": [{"code": code, "name": name} for code, name in missing],
        "already_present_detail": [
            {"code": code, "irc_name": name, "db_name": db_name}
            for code, name, db_name in already_present
        ]
    }
    
    diagnostic_file = IRC_DATA_DIR / "diagnostic_indicators.json"
    with open(diagnostic_file, "w", encoding="utf-8") as f:
        json.dump(diagnostic, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"📋 Diagnostic sauvegardé: {diagnostic_file}")
    print("=" * 80)
    
    return diagnostic

if __name__ == "__main__":
    main()
