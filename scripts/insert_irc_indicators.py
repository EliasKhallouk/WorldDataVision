#!/usr/bin/env python3
"""
Étape 2 : Insérer les 69 indicateurs IRC manquants dans la table indicator.
"""

import psycopg2
from psycopg2.extras import execute_values
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "worlddatavision")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Mapping : (code, name, description, unit, category_code, source)
INDICATORS_TO_ADD = [
    # Démographie
    ("SP.POP.TOTL", "Population totale", "Population totale en milieu d'année", "nombre", "demographic", "Banque Mondiale"),
    ("SP.POP.0014.TO.ZS", "Population 0-14 ans (%)", "Population âgée de 0 à 14 ans (% de la population totale)", "%", "demographic", "Banque Mondiale"),
    ("SP.POP.1564.TO.ZS", "Population 15-64 ans (%)", "Population âgée de 15 à 64 ans (% de la population totale)", "%", "demographic", "Banque Mondiale"),
    ("SP.POP.65UP.TO.ZS", "Population 65+ ans (%)", "Population âgée de 65 ans et plus (% de la population totale)", "%", "demographic", "Banque Mondiale"),
    ("SP.POP.AG.MA.NO", "Âge médian", "Âge médian de la population (années)", "années", "demographic", "Calculé"),
    ("SP.POP.DPND", "Ratio de dépendance total", "Ratio de dépendance (% population active)", "%", "demographic", "Banque Mondiale"),
    ("SP.POP.DPND.OL", "Ratio de dépendance des âgés", "Ratio de dépendance des personnes âgées (% pop 15-64)", "%", "demographic", "Banque Mondiale"),
    ("SP.POP.DPND.YG", "Ratio de dépendance des jeunes", "Ratio de dépendance des jeunes (% pop 15-64)", "%", "demographic", "Banque Mondiale"),
    ("SP.DYN.CBRT.IN", "Taux de natalité", "Taux de natalité (naissances pour 1000 habitants)", "pour 1000", "demographic", "Banque Mondiale"),
    ("SP.DYN.CDRT.IN", "Taux de mortalité", "Taux de mortalité (décès pour 1000 habitants)", "pour 1000", "demographic", "Banque Mondiale"),
    ("SP.POP.GROW", "Croissance de la population", "Taux de croissance annuelle de la population (%)", "%", "demographic", "Banque Mondiale"),
    ("SM.POP.NETM", "Solde migratoire net", "Solde migratoire net (nombre de migrants)", "nombre", "demographic", "Banque Mondiale"),
    ("SP.URB.TOTL.IN.ZS", "Population urbaine", "Population urbaine (% de la population totale)", "%", "demographic", "Banque Mondiale"),
    
    # Agriculture
    ("AG.LND.AGRI.ZS", "Terres agricoles", "Terres agricoles (% de la superficie terrestre)", "%", "agriculture", "Banque Mondiale"),
    ("AG.LND.ARBL.HA.PC", "Terres arables par habitant", "Terres arables (hectares par habitant)", "ha/hab", "agriculture", "Banque Mondiale"),
    ("AG.YLD.CREL.KG", "Rendement des céréales", "Rendement des cultures céréalières (kg/ha)", "kg/ha", "agriculture", "Banque Mondiale"),
    ("AG.PRD.FOOD.XD", "Indice de production alimentaire", "Indice de production alimentaire (2004-2006 = 100)", "indice", "agriculture", "Banque Mondiale"),
    ("AG.PRD.CROP.XD", "Indice de production végétale", "Indice de production des cultures (2004-2006 = 100)", "indice", "agriculture", "Banque Mondiale"),
    ("AG.PRD.LVSK.XD", "Indice de production animale", "Indice de production du bétail (2004-2006 = 100)", "indice", "agriculture", "Banque Mondiale"),
    ("TM.VAL.FOOD.ZS.UN", "Importations alimentaires", "Importations alimentaires (% des importations totales)", "%", "agriculture", "Banque Mondiale"),
    ("TX.VAL.FOOD.ZS.UN", "Exportations agricoles", "Exportations agricoles (% des exportations totales)", "%", "agriculture", "Banque Mondiale"),
    ("ER.H2O.FWST.ZS", "Stress hydrique", "Prélèvement d'eau de surface (% des ressources renouvelables)", "%", "agriculture", "Banque Mondiale"),
    ("ER.H2O.INTR.PC", "Eau renouvelable par habitant", "Ressources en eau interne renouvelables (m³/habitant)", "m³/hab", "agriculture", "Banque Mondiale"),
    ("AG.LND.FRST.ZS", "Superficie forestière", "Superficie forestière (% de la superficie terrestre)", "%", "agriculture", "Banque Mondiale"),
    
    # Énergie
    ("EG.ELC.PROD.KH", "Production d'électricité", "Production d'électricité (kWh)", "kWh", "energy", "Banque Mondiale"),
    ("EG.FEC.RNEW.ZS", "Consommation énergies renouvelables", "Consommation d'énergies renouvelables (% du total)", "%", "energy", "Banque Mondiale"),
    ("EG.USE.COMM.FO.ZS", "Consommation combustibles fossiles", "Consommation de combustibles fossiles (% du total)", "%", "energy", "Banque Mondiale"),
    ("EG.ELC.NUCL.ZS", "Électricité nucléaire", "Production d'électricité nucléaire (% du total)", "%", "energy", "Banque Mondiale"),
    ("EG.ELC.HYRO.ZS", "Électricité hydroélectrique", "Production d'électricité hydroélectrique (% du total)", "%", "energy", "Banque Mondiale"),
    ("EG.IMP.CONS.ZS", "Importations nettes d'énergie", "Importations nettes d'énergie (% de la consommation)", "%", "energy", "Banque Mondiale"),
    ("NY.GDP.PETR.RT.ZS", "Rente pétrolière", "Rente pétrolière (% du PIB)", "%", "energy", "Banque Mondiale"),
    ("NY.GDP.NGAS.RT.ZS", "Rente gazière", "Rente gazière naturelle (% du PIB)", "%", "energy", "Banque Mondiale"),
    ("NY.GDP.COAL.RT.ZS", "Rente minière charbon", "Rente minière du charbon (% du PIB)", "%", "energy", "Banque Mondiale"),
    ("EG.USE.PCAP.KG.OE", "Consommation énergétique par habitant", "Consommation d'énergie (kg équivalent pétrole/habitant)", "kg oe/hab", "energy", "Banque Mondiale"),
    ("EG.ELC.ACCS.ZS", "Accès à l'électricité", "Population avec accès à l'électricité (%)", "%", "energy", "Banque Mondiale"),
    ("EG.USE.ELEC.KH.PC", "Consommation d'électricité par habitant", "Consommation d'électricité (kWh par habitant)", "kWh/hab", "energy", "Banque Mondiale"),
    
    # Gouvernance
    ("CC.EST", "Contrôle de la corruption", "Indice de contrôle de la corruption (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("GE.EST", "Efficacité gouvernementale", "Indice d'efficacité gouvernementale (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("PV.EST", "Stabilité politique", "Indice de stabilité politique et absence de violence (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("RL.EST", "État de droit", "Indice d'état de droit (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("RQ.EST", "Qualité réglementaire", "Indice de qualité réglementaire (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("VA.EST", "Voix et responsabilité", "Indice de voix et responsabilité (WGI)", "indice", "institutional", "World Bank Governance Indicators"),
    ("DT.DOD.DECT.GN.ZS", "Dette externe", "Dette externe (% du RNB)", "%", "economy", "Banque Mondiale"),
    ("DT.TDS.DECT.EX.ZS", "Service de la dette", "Service de la dette (% des exportations)", "%", "economy", "Banque Mondiale"),
    ("FI.RES.TOTL.MO", "Réserves de change", "Réserves de change (mois d'importations)", "mois", "economy", "Banque Mondiale"),
    
    # Économie
    ("NY.GDP.MKTP.KD.ZG", "Croissance du PIB", "Croissance du PIB (% annuel)", "%", "economy", "Banque Mondiale"),
    ("FP.CPI.TOTL.ZG", "Inflation", "Indice des prix à la consommation (% annuel)", "%", "economy", "Banque Mondiale"),
    ("SL.UEM.TOTL.ZS", "Taux de chômage", "Taux de chômage (% de la population active)", "%", "economy", "Banque Mondiale"),
    ("BN.CAB.XOKA.GD.ZS", "Balance courante", "Balance courante (% du PIB)", "%", "economy", "Banque Mondiale"),
    ("BX.KLT.DINV.WD.GD.ZS", "Investissements directs étrangers", "Investissements directs étrangers (% du PIB)", "%", "economy", "Banque Mondiale"),
    ("MS.MIL.XPND.GD.ZS", "Dépenses militaires", "Dépenses militaires (% du PIB)", "%", "economy", "Banque Mondiale"),
    
    # Éducation & Technologie
    ("SE.TER.ENRR", "Scolarisation tertiaire", "Taux brut de scolarisation dans le supérieur (%)", "%", "social", "Banque Mondiale"),
    ("SE.ADT.LITR.ZS", "Taux d'alphabétisation adultes", "Taux d'alphabétisation des adultes (%)", "%", "social", "Banque Mondiale"),
    ("GB.XPD.RSDV.GD.ZS", "Dépenses R&D", "Dépenses en recherche et développement (% du PIB)", "%", "technology", "Banque Mondiale"),
    ("SP.POP.SCIE.RD.P6", "Chercheurs par million", "Chercheurs (ETP par million d'habitants)", "par million", "technology", "Banque Mondiale"),
    ("IP.PAT.RESD", "Demandes de brevets", "Demandes de brevets déposées par les résidents", "nombre", "technology", "Banque Mondiale"),
    ("IP.JRN.ARTC.SC", "Articles scientifiques", "Articles de revues scientifiques et techniques", "nombre", "technology", "Banque Mondiale"),
    ("TX.VAL.TECH.MF.ZS", "Exportations haute technologie", "Exportations de produits de haute technologie (% des exportations manufacturées)", "%", "technology", "Banque Mondiale"),
    ("IT.NET.USER.ZS", "Utilisateurs Internet", "Utilisateurs d'Internet (% de la population)", "%", "technology", "Banque Mondiale"),
    ("IT.CEL.SETS.P2", "Abonnements mobiles", "Abonnements à la téléphonie mobile (pour 100 habitants)", "pour 100", "technology", "Banque Mondiale"),
    ("IT.NET.BBND.P2", "Abonnements haut débit", "Abonnements au haut débit fixe (pour 100 habitants)", "pour 100", "technology", "Banque Mondiale"),
    ("IT.NET.SECR.P6", "Serveurs sécurisés", "Serveurs Internet sécurisés (pour 1 million d'habitants)", "pour 1M", "technology", "Banque Mondiale"),
    
    # Environnement & Santé
    ("AG.LND.TOTL.K2", "Superficie terrestre", "Superficie terrestre (km²)", "km²", "environment", "Banque Mondiale"),
    ("EN.ATM.CO2E.PC", "Émissions CO2 par habitant", "Émissions de dioxyde de carbone (tonnes métriques par habitant)", "t/hab", "environment", "Banque Mondiale"),
    ("EN.GHG.CO2.PC.CE.AR5", "Émissions CO2 (AR5)", "Émissions de CO2 excluant LULUCF par habitant (t CO2e/capita)", "t/hab", "environment", "Banque Mondiale"),
    ("SH.XPD.CHEX.GD.ZS", "Dépenses de santé", "Dépenses de santé actuelle (% du PIB)", "%", "social", "Banque Mondiale"),
    ("SH.MED.PHYS.ZS", "Médecins par 1000", "Médecins (pour 1000 habitants)", "pour 1000", "social", "Banque Mondiale"),
    ("SH.MED.BEDS.ZS", "Lits d'hôpital", "Lits d'hôpital (pour 1000 habitants)", "pour 1000", "social", "Banque Mondiale"),
    ("SP.DYN.IMRT.IN", "Mortalité infantile", "Mortalité infantile (pour 1000 naissances vivantes)", "pour 1000", "social", "Banque Mondiale"),
]

def main():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        
        print("=" * 80)
        print("📝 ÉTAPE 2 : INSERTION DES INDICATEURS IRC")
        print("=" * 80)
        
        # Vérifier les catégories
        cursor.execute("SELECT id, code FROM indicator_category")
        categories = {code: id for id, code in cursor.fetchall()}
        
        missing_categories = set()
        for _, _, _, _, cat_code, _ in INDICATORS_TO_ADD:
            if cat_code not in categories:
                missing_categories.add(cat_code)
        
        if missing_categories:
            print(f"⚠️ Catégories manquantes: {missing_categories}")
            print("Création des catégories manquantes...")
            
            category_data = {
                "agriculture": ("Agriculture", "Indicateurs agricoles et alimentaires"),
                "energy": ("Énergie", "Indicateurs énergétiques"),
                "technology": ("Technologie", "Indicateurs technologiques et innovants"),
            }
            
            for cat_code in missing_categories:
                if cat_code in category_data:
                    cat_name, cat_desc = category_data[cat_code]
                    cursor.execute(
                        "INSERT INTO indicator_category (code, name, description) VALUES (%s, %s, %s) ON CONFLICT (code) DO NOTHING",
                        (cat_code, cat_name, cat_desc)
                    )
            
            conn.commit()
            
            # Recharger les catégories
            cursor.execute("SELECT id, code FROM indicator_category")
            categories = {code: id for id, code in cursor.fetchall()}
            print("✅ Catégories créées")
        
        # Insérer les indicateurs
        insert_count = 0
        skip_count = 0
        
        for code, name, description, unit, category_code, source in INDICATORS_TO_ADD:
            category_id = categories.get(category_code)
            if category_id is None:
                print(f"⚠️ Catégorie non trouvée pour {code}: {category_code}")
                skip_count += 1
                continue
            
            cursor.execute(
                """INSERT INTO indicator (code, name, description, unit, category_id, source) 
                   VALUES (%s, %s, %s, %s, %s, %s) 
                   ON CONFLICT (code) DO NOTHING""",
                (code, name, description, unit, category_id, source)
            )
            
            if cursor.rowcount > 0:
                insert_count += 1
        
        conn.commit()
        
        # Vérification
        cursor.execute("SELECT COUNT(*) FROM indicator")
        total = cursor.fetchone()[0]
        
        cursor.execute(
            """SELECT COUNT(*) FROM indicator WHERE code IN (
                'SP.POP.TOTL', 'SP.POP.0014.TO.ZS', 'SP.POP.1564.TO.ZS', 'SP.POP.65UP.TO.ZS',
                'SP.POP.AG.MA.NO', 'SP.POP.DPND', 'SP.POP.DPND.OL', 'SP.POP.DPND.YG',
                'SP.DYN.CBRT.IN', 'SP.DYN.CDRT.IN', 'SP.POP.GROW', 'SM.POP.NETM',
                'SP.URB.TOTL.IN.ZS', 'AG.LND.AGRI.ZS', 'AG.LND.ARBL.HA.PC', 'AG.YLD.CREL.KG',
                'AG.PRD.FOOD.XD', 'AG.PRD.CROP.XD', 'AG.PRD.LVSK.XD', 'TM.VAL.FOOD.ZS.UN',
                'TX.VAL.FOOD.ZS.UN', 'ER.H2O.FWST.ZS', 'ER.H2O.INTR.PC', 'AG.LND.FRST.ZS',
                'EG.ELC.PROD.KH', 'EG.FEC.RNEW.ZS', 'EG.USE.COMM.FO.ZS', 'EG.ELC.NUCL.ZS',
                'EG.ELC.HYRO.ZS', 'EG.IMP.CONS.ZS', 'NY.GDP.PETR.RT.ZS', 'NY.GDP.NGAS.RT.ZS',
                'NY.GDP.COAL.RT.ZS', 'EG.USE.PCAP.KG.OE', 'EG.ELC.ACCS.ZS', 'EG.USE.ELEC.KH.PC',
                'CC.EST', 'GE.EST', 'PV.EST', 'RL.EST', 'RQ.EST', 'VA.EST', 'DT.DOD.DECT.GN.ZS',
                'DT.TDS.DECT.EX.ZS', 'FI.RES.TOTL.MO', 'NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG',
                'SL.UEM.TOTL.ZS', 'BN.CAB.XOKA.GD.ZS', 'BX.KLT.DINV.WD.GD.ZS', 'MS.MIL.XPND.GD.ZS',
                'SE.TER.ENRR', 'SE.ADT.LITR.ZS', 'GB.XPD.RSDV.GD.ZS', 'SP.POP.SCIE.RD.P6',
                'IP.PAT.RESD', 'IP.JRN.ARTC.SC', 'TX.VAL.TECH.MF.ZS', 'IT.NET.USER.ZS',
                'IT.CEL.SETS.P2', 'IT.NET.BBND.P2', 'IT.NET.SECR.P6', 'AG.LND.TOTL.K2',
                'EN.ATM.CO2E.PC', 'EN.GHG.CO2.PC.CE.AR5', 'SH.XPD.CHEX.GD.ZS', 'SH.MED.PHYS.ZS',
                'SH.MED.BEDS.ZS', 'SP.DYN.IMRT.IN'
            )"""
        )
        irc_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 80)
        print("✅ RÉSULTATS")
        print("=" * 80)
        print(f"✅ Indicateurs insérés: {insert_count}")
        print(f"⏭️ Indicateurs ignorés (déjà présents): {skip_count}")
        print(f"📊 Total indicateurs IRC dans la base: {irc_count}")
        print(f"📚 Total indicateurs dans la base: {total}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
