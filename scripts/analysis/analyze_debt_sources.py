#!/usr/bin/env python3
"""
Analyser les définitions exactes des indicateurs de dette et trouver des sources compatibles
"""

import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_debt_indicators():
    """Récupérer les définitions des indicateurs de dette"""
    
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        code, 
        name, 
        description, 
        source,
        COUNT(DISTINCT iv.country_id) as coverage
    FROM indicator i
    LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
    WHERE code IN ('DT.DOD.DECT.GN.ZS', 'DT.TDS.DECT.EX.ZS')
    GROUP BY i.id, code, name, description, source
    ORDER BY code;
    """
    
    cursor.execute(query)
    
    print("="*80)
    print("DÉFINITIONS DES INDICATEURS DE DETTE (World Bank)")
    print("="*80)
    
    indicators = []
    
    for row in cursor.fetchall():
        code, name, desc, source, coverage = row
        
        print(f"\n📊 {code}")
        print(f"   Nom: {name}")
        print(f"   Description: {desc if desc else 'N/A'}")
        print(f"   Source: {source}")
        print(f"   Couverture: {coverage} pays")
        
        indicators.append({
            'code': code,
            'name': name,
            'description': desc,
            'source': source,
            'coverage': coverage
        })
    
    cursor.close()
    conn.close()
    
    return indicators

def analyze_semantic_requirements():
    """Analyser les exigences sémantiques précises"""
    
    print(f"\n{'='*80}")
    print("ANALYSE SÉMANTIQUE")
    print(f"{'='*80}\n")
    
    print("📌 DT.DOD.DECT.GN.ZS - Dette extérieure")
    print("   DÉFINITION WORLD BANK:")
    print("   Dette extérieure totale = somme de la dette publique extérieure")
    print("   ET de la dette privée extérieure garantie publiquement")
    print("   EN POURCENTAGE du RNB (Revenu National Brut)")
    print()
    print("   ⚠️  ATTENTION SÉMANTIQUE:")
    print("   - Dette EXTERNE (due aux créanciers étrangers)")
    print("   - ≠ Dette PUBLIQUE totale (qui inclut dette domestique)")
    print("   - ≠ Dette GOUVERNEMENTALE seule")
    print("   - Inclut dette privée GARANTIE par le gouvernement")
    print()
    
    print("📌 DT.TDS.DECT.EX.ZS - Service de la dette")
    print("   DÉFINITION WORLD BANK:")
    print("   Service de la dette = paiements du principal + intérêts")
    print("   sur la dette extérieure à long terme")
    print("   EN POURCENTAGE des exportations de biens et services")
    print()
    print("   ⚠️  ATTENTION SÉMANTIQUE:")
    print("   - Dette EXTÉRIEURE seulement (pas domestique)")
    print("   - Long terme seulement (>1 an)")
    print("   - Paiements réels (principal + intérêts)")
    print("   - % des EXPORTATIONS (pas du PIB)")
    print()

def analyze_available_sources():
    """Analyser les sources potentielles et leur compatibilité sémantique"""
    
    print(f"\n{'='*80}")
    print("SOURCES POTENTIELLES - ANALYSE DE COMPATIBILITÉ")
    print(f"{'='*80}\n")
    
    sources = {
        "IMF International Debt Statistics (IDS)": {
            "url": "https://data.imf.org/?sk=7CB6619C-CF87-48DC-9443-2973E161ABEB",
            "coverage": "~140 pays",
            "data": "Dette extérieure publique et privée",
            "semantic": "✅ COMPATIBLE - Même définition que WB",
            "format": "API disponible (JSON)",
            "access": "Gratuit",
            "notes": "FMI et Banque Mondiale utilisent la même méthodologie"
        },
        "IMF World Economic Outlook (WEO)": {
            "url": "https://www.imf.org/en/Publications/WEO/weo-database",
            "coverage": "~190 pays",
            "data": "Dette publique générale (% PIB)",
            "semantic": "❌ INCOMPATIBLE - Dette PUBLIQUE, pas EXTERNE",
            "format": "Excel/CSV",
            "access": "Gratuit",
            "notes": "DÉJÀ TESTÉ - Rejeté pour incompatibilité sémantique"
        },
        "OECD External Debt Statistics": {
            "url": "https://stats.oecd.org/",
            "coverage": "~50 pays (membres OECD + quelques autres)",
            "data": "Dette extérieure détaillée par secteur",
            "semantic": "✅ COMPATIBLE - Même définition",
            "format": "SDMX-JSON, CSV",
            "access": "Gratuit",
            "notes": "Excellente qualité mais couverture limitée"
        },
        "Banques Régionales de Développement": {
            "url": "AfDB, ADB, IDB APIs",
            "coverage": "~80-100 pays",
            "data": "Dette extérieure et service de la dette",
            "semantic": "✅ COMPATIBLE - Standards internationaux",
            "format": "Variable (API, Excel)",
            "access": "Gratuit",
            "notes": "Couvre Afrique, Asie, Amérique Latine"
        },
        "UN National Accounts": {
            "url": "https://unstats.un.org/",
            "coverage": "~200 pays",
            "data": "Comptes nationaux (dette dans SNA)",
            "semantic": "⚠️  PARTIEL - Peut inclure dette domestique",
            "format": "CSV, API",
            "access": "Gratuit",
            "notes": "Vérifier définition exacte par indicateur"
        },
        "Eurostat Government Finance Statistics": {
            "url": "https://ec.europa.eu/eurostat",
            "coverage": "~40 pays européens",
            "data": "Dette gouvernementale consolidée",
            "semantic": "❌ INCOMPATIBLE - Dette PUBLIQUE, pas nécessairement EXTERNE",
            "format": "TSV, SDMX",
            "access": "Gratuit",
            "notes": "Eurostat mesure dette publique brute (Maastricht)"
        }
    }
    
    for source_name, info in sources.items():
        semantic_symbol = info['semantic'].split()[0]
        print(f"{semantic_symbol} {source_name}")
        print(f"   Couverture: {info['coverage']}")
        print(f"   Données: {info['data']}")
        print(f"   Sémantique: {info['semantic']}")
        print(f"   Format: {info['format']}")
        print(f"   Notes: {info['notes']}")
        print()

def recommend_priority():
    """Recommandations finales"""
    
    print(f"\n{'='*80}")
    print("RECOMMANDATIONS PRIORITAIRES")
    print(f"{'='*80}\n")
    
    print("🎯 PRIORITÉ 1: FMI International Debt Statistics (IDS)")
    print("   ✅ Sémantique: IDENTIQUE à World Bank (même méthodologie)")
    print("   ✅ Couverture: ~140 pays")
    print("   ✅ API disponible")
    print("   ✅ Gratuit")
    print("   📝 Action: Utiliser API FMI IDS pour compléter les 2 indicateurs")
    print()
    
    print("🎯 PRIORITÉ 2: OECD External Debt Statistics")
    print("   ✅ Sémantique: Compatible")
    print("   ⚠️  Couverture: Limitée (~50 pays)")
    print("   ✅ Qualité: Excellente")
    print("   📝 Action: Compléter pour pays OECD manquants")
    print()
    
    print("🎯 PRIORITÉ 3: Banques Régionales")
    print("   ✅ Sémantique: Compatible (standards internationaux)")
    print("   ✅ Couverture: Bonne pour régions spécifiques")
    print("   ⚠️  Format: Variable")
    print("   📝 Action: AfDB pour Afrique, ADB pour Asie, IDB pour Amérique Latine")
    print()
    
    print("❌ À ÉVITER:")
    print("   • IMF WEO → Dette PUBLIQUE (pas externe)")
    print("   • Eurostat → Dette publique brute (Maastricht)")
    print("   • UN SNA → Vérifier d'abord la définition exacte")
    print()
    
    print("💡 STRATÉGIE:")
    print("   1. Commencer par FMI IDS (API, facile, sémantiquement correct)")
    print("   2. Compléter avec OECD si besoin")
    print("   3. Banques régionales en dernier recours")
    print()
    
    print("⚠️  VALIDATION OBLIGATOIRE:")
    print("   Avant d'importer toute donnée, vérifier que:")
    print("   • Dette EXTERNE (pas publique totale)")
    print("   • Inclut secteur privé garanti")
    print("   • Service de dette = % EXPORTATIONS (pas PIB)")

def main():
    print("="*80)
    print("ANALYSE DETTE EXTERNE - RECHERCHE DE SOURCES COMPATIBLES")
    print("Catégorie 1 (Économie)")
    print("="*80)
    
    # Get current indicators
    indicators = get_debt_indicators()
    
    # Analyze semantic requirements
    analyze_semantic_requirements()
    
    # Analyze available sources
    analyze_available_sources()
    
    # Recommendations
    recommend_priority()

if __name__ == '__main__':
    main()
