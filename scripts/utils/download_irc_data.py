#!/usr/bin/env python3
"""
Script de téléchargement des données pour l'Index de Résilience Civilisationnelle (IRC)
Télécharge toutes les variables depuis l'API de la Banque Mondiale
"""

import requests
import json
import csv
import time
from datetime import datetime
from pathlib import Path
import sys
import argparse

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "Data" / "IRC"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FAILED_FILE = OUTPUT_DIR / "failed_indicators.json"

# URL de base de l'API Banque Mondiale
BASE_URL = "https://api.worldbank.org/v2"

# Paramètres par défaut
START_YEAR = 1960
END_YEAR = 2025
PER_PAGE = 1000
TIMEOUT_SECONDS = 60
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.5

# Liste complète des indicateurs à télécharger (Banque Mondiale uniquement)
INDICATORS = {
    "EG.USE.ELEC.KH.PC": "electricity_use_per_capita",
    "EN.GHG.CO2.PC.CE.AR5": "co2_emissions_per_capita_ar5",
    
    # DÉMOGRAPHIE
    "SP.POP.TOTL": "population_total",
    "SP.POP.0014.TO.ZS": "population_0_14",
    "SP.POP.1564.TO.ZS": "population_15_64",
    "SP.POP.65UP.TO.ZS": "population_65plus",
    "SP.POP.AG.MA.NO": "median_age",
    "SP.POP.DPND": "dependency_ratio",
    "SP.POP.DPND.OL": "old_dependency_ratio",
    "SP.POP.DPND.YG": "young_dependency_ratio",
    "SP.DYN.CBRT.IN": "birth_rate",
    "SP.DYN.CDRT.IN": "death_rate",
    "SP.DYN.TFRT.IN": "fertility_rate",
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.POP.GROW": "population_growth",
    "SM.POP.NETM": "net_migration",
    "SP.URB.TOTL.IN.ZS": "urban_population",
    
    # AGRICULTURE & ALIMENTATION
    "AG.LND.AGRI.ZS": "agricultural_land",
    "AG.LND.ARBL.HA.PC": "arable_land_per_capita",
    "AG.YLD.CREL.KG": "cereal_yield",
    "AG.PRD.FOOD.XD": "food_production_index",
    "AG.PRD.CROP.XD": "crop_production_index",
    "AG.PRD.LVSK.XD": "livestock_production_index",
    "TM.VAL.FOOD.ZS.UN": "food_imports",
    "TX.VAL.FOOD.ZS.UN": "agricultural_exports",
    "ER.H2O.FWST.ZS": "water_stress",
    "ER.H2O.INTR.PC": "renewable_water_per_capita",
    "AG.LND.FRST.ZS": "forest_area",
    
    # ÉNERGIE
    "EG.ELC.PROD.KH": "electricity_production",
    "EG.FEC.RNEW.ZS": "renewable_energy_consumption",
    "EG.USE.COMM.FO.ZS": "fossil_fuel_consumption",
    "EG.ELC.NUCL.ZS": "nuclear_electricity",
    "EG.ELC.HYRO.ZS": "hydro_electricity",
    "EG.IMP.CONS.ZS": "energy_imports_net",
    "NY.GDP.PETR.RT.ZS": "oil_rents",
    "NY.GDP.NGAS.RT.ZS": "natural_gas_rents",
    "NY.GDP.COAL.RT.ZS": "coal_rents",
    "EG.USE.PCAP.KG.OE": "energy_use_per_capita",
    "EG.ELC.ACCS.ZS": "access_electricity",
    
    # GOUVERNANCE (World Governance Indicators)
    "CC.EST": "corruption_control",
    "GE.EST": "government_effectiveness",
    "PV.EST": "political_stability",
    "RL.EST": "rule_of_law",
    "RQ.EST": "regulatory_quality",
    "VA.EST": "voice_accountability",
    
    # FINANCES PUBLIQUES
    "GC.DOD.TOTL.GD.ZS": "government_debt",
    "DT.DOD.DECT.GN.ZS": "external_debt",
    "DT.TDS.DECT.EX.ZS": "debt_service",
    "GC.TAX.TOTL.GD.ZS": "tax_revenue",
    "FI.RES.TOTL.MO": "reserves_months_imports",
    
    # ÉCONOMIE
    "NY.GDP.PCAP.PP.KD": "gdp_per_capita_ppp",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "FP.CPI.TOTL.ZG": "inflation",
    "SL.UEM.TOTL.ZS": "unemployment",
    "BN.CAB.XOKA.GD.ZS": "current_account_balance",
    "BX.KLT.DINV.WD.GD.ZS": "fdi_inflows",
    "MS.MIL.XPND.GD.ZS": "military_expenditure",
    
    # ÉDUCATION & INNOVATION
    "SE.XPD.TOTL.GD.ZS": "education_expenditure",
    "SE.TER.ENRR": "school_enrollment_tertiary",
    "SE.ADT.LITR.ZS": "literacy_rate_adult",
    "GB.XPD.RSDV.GD.ZS": "rd_expenditure",
    "SP.POP.SCIE.RD.P6": "researchers_per_million",
    "IP.PAT.RESD": "patent_applications",
    "IP.JRN.ARTC.SC": "scientific_articles",
    "TX.VAL.TECH.MF.ZS": "high_tech_exports",
    
    # INFRASTRUCTURE NUMÉRIQUE
    "IT.NET.USER.ZS": "internet_users",
    "IT.CEL.SETS.P2": "mobile_subscriptions",
    "IT.NET.BBND.P2": "fixed_broadband",
    "IT.NET.SECR.P6": "secure_internet_servers",
    
    # ENVIRONNEMENT
    "AG.LND.TOTL.K2": "land_area",
    "EN.ATM.CO2E.PC": "co2_emissions_per_capita",
    
    # SANTÉ
    "SH.XPD.CHEX.GD.ZS": "health_expenditure",
    "SH.MED.PHYS.ZS": "physicians_per_1000",
    "SH.MED.BEDS.ZS": "hospital_beds",
    "SP.DYN.IMRT.IN": "infant_mortality",
}

# Certains indicateurs ont des codes alternatifs ou ont changé.
INDICATOR_ALIASES = {
    "SP.POP.AG.MA.NO": ["SP.POP.AG.MA"],  # Âge médian (total)
}

# Sources spécifiques pour certains indicateurs (ex: WGI)
INDICATOR_SOURCES = {
    "CC.EST": 3,
    "GE.EST": 3,
    "PV.EST": 3,
    "RL.EST": 3,
    "RQ.EST": 3,
    "VA.EST": 3,
}


def _fetch_page(session, url, params, attempt=1):
    """Récupère une page avec retries et backoff."""
    try:
        response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        if attempt >= MAX_RETRIES:
            raise
        sleep_time = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
        time.sleep(sleep_time)
        return _fetch_page(session, url, params, attempt + 1)


def _extract_api_message(data):
    """Extrait un message d'erreur éventuel de l'API Banque Mondiale."""
    if isinstance(data, dict) and "message" in data:
        return data.get("message")
    if isinstance(data, list) and data and isinstance(data[0], dict) and "message" in data[0]:
        return data[0].get("message")
    return None


def _build_params(start_year, end_year, page, include_date=True, source=None):
    params = {
        "format": "json",
        "per_page": PER_PAGE,
        "page": page,
    }
    if include_date:
        params["date"] = f"{start_year}:{end_year}"
    if source is not None:
        params["source"] = source
    return params


def download_indicator(indicator_code, indicator_name, start_year=START_YEAR, end_year=END_YEAR):
    """
    Télécharge les données d'un indicateur depuis l'API Banque Mondiale
    
    Args:
        indicator_code: Code de l'indicateur (ex: "SP.POP.TOTL")
        indicator_name: Nom du fichier de sortie (ex: "population_total")
        start_year: Année de début
        end_year: Année de fin
    
    Returns:
        bool: True si succès, False sinon
    """
    print(f"📥 Téléchargement de {indicator_name} ({indicator_code})...", end=" ")
    
    all_data = []
    page = 1
    
    session = requests.Session()
    source = INDICATOR_SOURCES.get(indicator_code)
    try:
        while True:
            # Construction de l'URL
            url = f"{BASE_URL}/country/all/indicator/{indicator_code}"
            params = _build_params(start_year, end_year, page, include_date=True, source=source)
            
            # Requête
            response = _fetch_page(session, url, params)
            
            # Parse JSON
            data = response.json()

            # Message d'erreur explicite de l'API
            api_message = _extract_api_message(data)
            if api_message:
                print(f"⚠️  API message: {api_message}")
                # Tentative avec un alias si l'indicateur est invalide
                if "Invalid value" in str(api_message) and indicator_code in INDICATOR_ALIASES:
                    for alias_code in INDICATOR_ALIASES[indicator_code]:
                        print(f"   ↪️  Tentative avec l'alias {alias_code}")
                        return download_indicator(alias_code, indicator_name, start_year, end_year)
                return False
            
            # L'API retourne [metadata, data]
            if len(data) < 2 or data[1] is None:
                break
            
            metadata = data[0]
            records = data[1]
            
            # Ajouter les enregistrements
            all_data.extend(records)
            
            # Vérifier s'il y a d'autres pages
            total_pages = metadata.get("pages", 1)
            if page >= total_pages:
                break
            
            page += 1
            time.sleep(0.2)  # Pause pour ne pas surcharger l'API
        
        if not all_data:
            # Tentative sans paramètre date (certains indicateurs ont des périodes atypiques)
            url = f"{BASE_URL}/country/all/indicator/{indicator_code}"
            params = _build_params(start_year, end_year, page=1, include_date=False, source=source)
            response = _fetch_page(session, url, params)
            data = response.json()
            api_message = _extract_api_message(data)
            if api_message:
                print(f"⚠️  API message: {api_message}")
                if "Invalid value" in str(api_message) and indicator_code in INDICATOR_ALIASES:
                    for alias_code in INDICATOR_ALIASES[indicator_code]:
                        print(f"   ↪️  Tentative avec l'alias {alias_code}")
                        return download_indicator(alias_code, indicator_name, start_year, end_year)
                return False
            if len(data) >= 2 and data[1]:
                all_data = data[1]
            else:
                print("⚠️  Aucune donnée disponible")
                return False
        
        # Sauvegarder en CSV
        output_file = OUTPUT_DIR / f"{indicator_name}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # En-tête
            writer.writerow([
                "country_code",
                "country_name",
                "indicator_code",
                "indicator_name",
                "year",
                "value",
                "unit",
                "decimal"
            ])
            
            # Données
            for record in all_data:
                if record.get("value") is not None:  # Ignorer les valeurs nulles
                    writer.writerow([
                        record.get("countryiso3code", ""),
                        record.get("country", {}).get("value", ""),
                        record.get("indicator", {}).get("id", ""),
                        record.get("indicator", {}).get("value", ""),
                        record.get("date", ""),
                        record.get("value", ""),
                        record.get("unit", ""),
                        record.get("decimal", "")
                    ])
        
        print(f"✅ {len(all_data)} enregistrements sauvegardés")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur HTTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def create_metadata_file():
    """Crée un fichier de métadonnées avec la liste des indicateurs"""
    metadata = {
        "download_date": datetime.now().isoformat(),
        "source": "World Bank API",
        "api_version": "v2",
        "period": f"{START_YEAR}-{END_YEAR}",
        "total_indicators": len(INDICATORS),
        "indicators": [
            {
                "code": code,
                "name": name,
                "file": f"{name}.csv"
            }
            for code, name in INDICATORS.items()
        ]
    }
    
    metadata_file = OUTPUT_DIR / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Métadonnées sauvegardées dans {metadata_file}")


def _load_failed_indicators(failed_file: Path):
    if not failed_file.exists():
        return []
    try:
        with open(failed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("failed_indicators", [])
    except Exception:
        return []


def _save_failed_indicators(failed_file: Path, failed_indicators):
    payload = {
        "saved_at": datetime.now().isoformat(),
        "failed_indicators": failed_indicators,
    }
    with open(failed_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main():
    """Fonction principale"""
    print("=" * 80)
    print("🌍 TÉLÉCHARGEMENT DES DONNÉES IRC - BANQUE MONDIALE")
    print("=" * 80)
    print(f"📁 Dossier de sortie: {OUTPUT_DIR}")
    print(f"📅 Période: {START_YEAR}-{END_YEAR}")
    print(f"📊 Nombre d'indicateurs: {len(INDICATORS)}")
    print("=" * 80)
    print()
    
    parser = argparse.ArgumentParser(description="Télécharger les indicateurs IRC depuis la Banque Mondiale")
    parser.add_argument(
        "--only-failed",
        action="store_true",
        help="Relancer uniquement les indicateurs échoués lors du dernier run",
    )
    parser.add_argument(
        "--failed-file",
        default=str(FAILED_FILE),
        help="Chemin du fichier d'indicateurs échoués",
    )
    args = parser.parse_args()

    failed_file = Path(args.failed_file)

    # Statistiques
    success_count = 0
    failed_count = 0
    failed_indicators = []

    indicators_to_download = INDICATORS
    if args.only_failed:
        previous_failed = _load_failed_indicators(failed_file)
        if previous_failed:
            indicators_to_download = {code: name for code, name in previous_failed if code in INDICATORS}
            print(f"🔁 Relance des indicateurs échoués: {len(indicators_to_download)}")
        else:
            print("ℹ️ Aucun indicateur échoué trouvé. Téléchargement complet.")
    
    # Téléchargement de chaque indicateur
    total_to_download = len(indicators_to_download)
    try:
        for i, (code, name) in enumerate(indicators_to_download.items(), 1):
            print(f"[{i}/{total_to_download}] ", end="")
            
            if download_indicator(code, name):
                success_count += 1
            else:
                failed_count += 1
                failed_indicators.append((code, name))
            
            # Petite pause entre chaque requête
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n⏹️  Interruption détectée. Sauvegarde des échecs...")
        if failed_indicators:
            _save_failed_indicators(failed_file, failed_indicators)
        return 130
    
    # Créer le fichier de métadonnées
    create_metadata_file()
    
    # Résumé
    print()
    print("=" * 80)
    print("📊 RÉSUMÉ DU TÉLÉCHARGEMENT")
    print("=" * 80)
    print(f"✅ Succès: {success_count}/{len(INDICATORS)}")
    print(f"❌ Échecs: {failed_count}/{len(INDICATORS)}")
    
    if failed_indicators:
        print("\n⚠️  Indicateurs échoués:")
        for code, name in failed_indicators:
            print(f"   - {code} ({name})")
        _save_failed_indicators(failed_file, failed_indicators)
    else:
        if failed_file.exists():
            failed_file.unlink()
    
    print()
    print(f"💾 Fichiers sauvegardés dans: {OUTPUT_DIR}")
    print("=" * 80)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
