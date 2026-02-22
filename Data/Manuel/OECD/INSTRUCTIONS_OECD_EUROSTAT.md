
# INSTRUCTIONS - Téléchargement Manuel OECD

L'API OECD étant difficile d'accès, voici la procédure manuelle :

## 1. CHERCHEURS EN R&D

**Source:** OECD Main Science and Technology Indicators (MSTI)
**URL:** https://stats.oecd.org/Index.aspx?DataSetCode=MSTI_PUB

**Étapes:**
1. Aller sur OECD.Stat Data Explorer
2. Chercher "Main Science and Technology Indicators"
3. Sélectionner: "Total researchers" ou "Researchers per thousand employment"
4. Exporter CSV avec:
   - Tous les pays
   - Toutes les années disponibles
   - Valeurs en ETP (équivalent temps plein)

**Mapping:** 
- OECD "Researchers per 1000 employment" → SP.POP.SCIE.RD.P6 (après conversion)
- Formule: (chercheurs / 1000 emplois) × (population active / population totale) × 1000000

## 2. DÉPENSES R&D (% PIB)

**Source:** OECD Main Science and Technology Indicators (MSTI)
**URL:** https://stats.oecd.org/Index.aspx?DataSetCode=MSTI_PUB

**Étapes:**
1. Chercher "Gross domestic expenditure on R&D"
2. Sélectionner: "GERD as a percentage of GDP"
3. Exporter CSV

**Mapping:**
- OECD "GERD as % of GDP" → GB.XPD.RSDV.GD.ZS (correspondance directe)

## 3. BREVETS (Demandes résidents)

**Source:** OECD Patent Statistics
**URL:** https://stats.oecd.org/Index.aspx?DataSetCode=PAT_IPC

**Étapes:**
1. Chercher "Patent applications"
2. Sélectionner: "Applications by residents"
3. Exporter CSV

**Mapping:**
- OECD "Patent applications by residents" → IP.PAT.RESD (correspondance directe)

## ALTERNATIVE: Eurostat (pour pays européens)

**URL:** https://ec.europa.eu/eurostat/data/database

**Datasets:**
- `rd_p_persocc` - Chercheurs par occupation
- `rd_e_gerdtot` - Dépenses R&D totales
- `pat_ep_ntot` - Applications brevets EPO

**Avantage:** Couverture excellente pour UE27 + pays associés (~35 pays)
**Format:** CSV téléchargeable directement

## Gain attendu

Si OECD + Eurostat combinés:
- Chercheurs: 145 → ~165 pays (+20)
- R&D: 155 → ~170 pays (+15)
- Brevets: 173 → ~180 pays (+7)

Total: 38 pays OECD + 27 UE + quelques associés = ~50 pays uniques
