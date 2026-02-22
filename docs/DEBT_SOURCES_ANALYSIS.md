================================================================================
ANALYSE DETTE EXTERNE - SOURCES SÉMANTIQUEMENT COMPATIBLES
Catégorie 1 (Économie)
================================================================================

📊 INDICATEURS À AMÉLIORER (121 pays actuellement):

1. DT.DOD.DECT.GN.ZS - Dette extérieure (% RNB)
   Définition: Dette extérieure TOTALE = dette publique externe + dette privée garantie
   ≠ Dette publique totale
   ≠ Dette gouvernementale seule
   
2. DT.TDS.DECT.EX.ZS - Service dette (% exportations)
   Définition: Paiements (principal + intérêts) sur dette EXTERNE long terme
   EN % des EXPORTATIONS (pas PIB)

================================================================================
SOURCES ANALYSÉES
================================================================================

✅ COMPATIBLE - FMI International Debt Statistics (IDS)
   URL: https://data.imf.org/?sk=7CB6619C-CF87-48DC-9443-2973E161ABEB
   Couverture: ~140 pays
   Sémantique: IDENTIQUE à World Bank (même méthodologie FMI/WB)
   Format: API JSON disponible
   Accès: Gratuit
   ⭐ RECOMMANDÉ EN PRIORITÉ

✅ COMPATIBLE - OECD External Debt Statistics
   URL: https://stats.oecd.org/
   Couverture: ~50 pays (OECD + quelques émergents)
   Sémantique: Compatible, même définition
   Format: SDMX-JSON, CSV
   Accès: Gratuit
   Note: Excellente qualité mais couverture limitée

✅ COMPATIBLE - Banques Régionales de Développement
   Sources: AfDB, ADB, IDB
   Couverture: ~80-100 pays (par région)
   Sémantique: Compatible (standards internationaux)
   Format: Variable (API, Excel)
   Accès: Gratuit
   Note: Complément pour pays en développement

❌ INCOMPATIBLE - IMF World Economic Outlook (WEO)
   Raison: Dette PUBLIQUE totale, pas dette EXTERNE
   Déjà rejeté: Erreur sémantique détectée précédemment
   
❌ INCOMPATIBLE - Eurostat Government Finance
   Raison: Dette publique brute (critères Maastricht), pas externe
   Inclut: Dette domestique
   
⚠️  À VÉRIFIER - UN National Accounts
   Raison: Définition variable selon indicateur SNA
   Action: Vérifier méthodologie exacte avant utilisation

================================================================================
STRATÉGIE RECOMMANDÉE
================================================================================

ÉTAPE 1: FMI International Debt Statistics (IDS)
  → API disponible
  → Même méthodologie que World Bank
  → Gain estimé: +15-25 pays (121 → 140-145)
  → SÉMANTIQUEMENT CORRECT ✅

ÉTAPE 2: OECD (si besoin)
  → Compléter pays développés manquants
  → Gain: +5-10 pays
  
ÉTAPE 3: Banques régionales (si besoin)
  → AfDB pour Afrique
  → ADB pour Asie-Pacifique
  → IDB pour Amérique Latine
  → Gain: +10-15 pays

VALIDATION OBLIGATOIRE AVANT IMPORT:
  ✓ Dette EXTERNE (pas publique totale)
  ✓ Inclut secteur privé garanti
  ✓ Service dette en % EXPORTATIONS (pas PIB)
  ✓ Même unités que World Bank

================================================================================
PROCHAINE ACTION
================================================================================

Tester l'API FMI IDS pour:
  1. Vérifier disponibilité des données
  2. Valider compatibilité sémantique exacte
  3. Mapper aux indicateurs IRC
  4. Importer si validation OK

URL API: https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service
