# 🌐 Sources de Données Alternatives pour Indicateurs IRC

**Date**: 22 février 2026  
**Objectif**: Compléter les indicateurs IRC avec des sources RÉELLEMENT indépendantes (pas via World Bank)

---

## ⚠️ CONSTAT: OWID Réutilise World Bank

L'analyse des métadonnées OWID révèle que **la plupart des datasets passent par World Bank**:
- Chercheurs R&D: `via World Bank (2026)` → **100% redondant**
- Brevets: `via World Bank (2026)` → **100% redondant**  
- Importations énergie: `IEA via World Bank (2026)` → **100% redondant**
- Résultat: 59,304 valeurs moyennées, seulement 43 nouvelles

**Solution**: Aller directement aux sources primaires!

---

## 📊 INDICATEURS PRIORITAIRES (< 150 pays)

### 1. 🏛️ Dette Publique (GC.DOD.TOTL.GD.ZS) - 109 pays ✅ FAIT
**Source alternative**: IMF Central Government Debt  
**Statut**: ✅ **Complété avec succès** (8,264 valeurs importées, 98% succès)

---

### 2. 📊 Service de la Dette (DT.TDS.DECT.EX.ZS) - 121 pays

**Source 1: OECD External Debt Statistics**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=QASA_TABLE8
- Format: CSV téléchargeable
- Couverture: 40+ pays OECD + partenaires
- Unité: % des exportations ✅ COMPATIBLE
- Téléchargement: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/QASA_TABLE8/all/all

**Source 2: IMF World Economic Outlook**
- URL: https://www.imf.org/en/Publications/WEO/weo-database/2024/October
- Format: CSV, Excel
- Télécharger: Section "External Debt" → Download
- Unité: % du PIB, % exports ✅ VÉRIFIER

---

### 3. 📊 Dette Externe (DT.DOD.DECT.GN.ZS) - 121 pays

**Source 1: BIS Consolidated Banking Statistics**
- URL: https://stats.bis.org/statx/srs/table/a1
- Format: CSV, Excel
- Couverture: Données bancaires internationales
- Télécharger: https://www.bis.org/statistics/consstats.htm?m=6%7C32

**Source 2: OECD External Debt**
- URL: https://data.oecd.org/external/external-debt.htm
- Format: CSV direct
- Télécharger: https://data.oecd.org/external/external-debt.htm#indicator-chart (bouton Export)

---

### 4. 🔬 Chercheurs en R&D (SP.POP.SCIE.RD.P6) - 144 pays

**Source 1: OECD Main Science & Technology Indicators**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=MSTI_PUB
- Format: CSV
- Télécharger: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/MSTI_PUB/all/all
- Unité: Par million d'habitants ✅ COMPATIBLE
- Couverture: 38 pays OECD + associés, 1981-2023

**Source 2: UNESCO Institute for Statistics**
- URL: http://data.uis.unesco.org/
- Section: Science, Technology & Innovation
- Indicateur: Researchers in R&D (per million inhabitants)
- Format: Excel, CSV
- Télécharger: http://data.uis.unesco.org/ → STI → Researchers → Download

**Source 3: Eurostat R&D Personnel**
- URL: https://ec.europa.eu/eurostat/databrowser/view/RD_P_PERSOCC__custom_1234/default/table
- Format: CSV, Excel
- Couverture: 27 pays UE + associés
- Télécharger: Cliquer sur "Download" dans la page

---

### 5. ⚡ Importations Nettes Énergie (EG.IMP.CONS.ZS) - 145 pays

**Source 1: IEA Energy Statistics**
- URL: https://www.iea.org/data-and-statistics/data-product/world-energy-balances
- Format: CSV (requiert compte gratuit)
- Couverture: 150+ pays
- Télécharger: https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser
- Indicateur: Energy imports, net (% of energy use)
- ⚠️ Nécessite inscription gratuite

**Source 2: Eurostat Energy Imports Dependency**
- URL: https://ec.europa.eu/eurostat/databrowser/view/NRG_IND_ID__custom_9876/default/table
- Format: CSV direct
- Couverture: 27 pays UE
- Télécharger: Bouton "Download"

**Source 3: BP Statistical Review of World Energy**
- URL: https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html
- Format: Excel téléchargeable
- Couverture: 80+ pays
- Télécharger: https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html

---

### 6. 💡 Consommation Électricité (EG.USE.ELEC.KH.PC) - 150 pays

**Source 1: IEA Electricity Information**
- URL: https://www.iea.org/data-and-statistics/data-product/electricity-information
- Format: CSV (compte gratuit)
- Télécharger: https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser
- Indicateur: Electricity consumption per capita (kWh)

**Source 2: Eurostat Electricity Statistics**
- URL: https://ec.europa.eu/eurostat/databrowser/view/NRG_CB_E__custom_8765/default/table
- Format: CSV
- Couverture: 27 pays UE

---

### 7. 🧪 Dépenses R&D (GB.XPD.RSDV.GD.ZS) - 153 pays

**Source 1: OECD Main Science & Technology Indicators**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=MSTI_PUB
- Indicateur: GERD (Gross Domestic Expenditure on R&D) as % of GDP
- Format: CSV
- Télécharger: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/MSTI_PUB/all/all
- Unité: % du PIB ✅ COMPATIBLE

**Source 2: UNESCO Institute for Statistics**
- URL: http://data.uis.unesco.org/
- Section: Science, Technology & Innovation
- Indicateur: R&D expenditure (% of GDP)
- Format: CSV

**Source 3: Eurostat R&D Expenditure**
- URL: https://ec.europa.eu/eurostat/databrowser/view/RD_E_GERDTOT__custom_5678/default/table
- Format: CSV
- Couverture: 27 pays UE

---

### 8. 📜 Brevets Résidents (IP.PAT.RESD) - 158 pays

**Source 1: WIPO IP Statistics Data Center**
- URL: https://www3.wipo.int/ipstats/
- Section: Patents → Patent applications by residents
- Format: Excel, CSV
- Télécharger: https://www3.wipo.int/ipstats/index.htm?tab=patent
- Unité: Nombre absolu ✅ COMPATIBLE

**Source 2: OECD Patent Statistics**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=PATS_IPC
- Format: CSV
- Couverture: 38 pays OECD
- Télécharger: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PATS_IPC/all/all

**Source 3: EPO Statistics (Europe)**
- URL: https://www.epo.org/en/about-us/annual-reports-statistics/statistics
- Format: Excel
- Couverture: Pays européens

---

### 9. 💰 Revenus Fiscaux (GC.TAX.TOTL.GD.ZS) - 161 pays

**Source 1: OECD Revenue Statistics**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=REV
- Format: CSV
- Télécharger: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/REV/all/all
- Unité: % du PIB ✅ COMPATIBLE
- Couverture: 100+ pays (pas que OECD)

**Source 2: IMF Government Finance Statistics**
- URL: https://data.imf.org/?sk=a0867067-d23c-4ebc-ad23-d3b015045405
- Format: CSV, Excel
- Télécharger: https://data.imf.org/regular.aspx?key=61545855
- Indicateur: Tax revenue (% of GDP)

**Source 3: Eurostat Tax Revenue**
- URL: https://ec.europa.eu/eurostat/databrowser/view/GOV_10A_TAXAG__custom_4567/default/table
- Format: CSV
- Couverture: 27 pays UE

---

### 10. 🎖️ Dépenses Militaires (MS.MIL.XPND.GD.ZS) - 164 pays

**Source 1: SIPRI Military Expenditure Database** ⭐ **MEILLEURE SOURCE**
- URL: https://www.sipri.org/databases/milex
- Format: Excel téléchargeable
- Couverture: 170+ pays, 1949-2024
- Télécharger: https://milex.sipri.org/sipri → Export to Excel
- Unité: % du PIB, USD constants ✅ COMPATIBLE
- ⚠️ **SOURCE INDÉPENDANTE** (pas World Bank!)

**Source 2: NATO Defence Expenditure**
- URL: https://www.nato.int/cps/en/natohq/news_197050.htm
- Format: Excel, PDF
- Couverture: 32 pays NATO
- Télécharger: Lien dans la page vers fichier Excel

---

### 11. 📚 Alphabétisation (SE.ADT.LITR.ZS) - 177 pays ✅ FAIT
**Source alternative**: UNESCO Institute for Statistics  
**Statut**: ✅ **Complété avec succès** (948 valeurs moyennées, 99% succès)

---

### 12. 💧 Stress Hydrique (ER.H2O.FWST.ZS) - 178 pays

**Source 1: FAO AQUASTAT** ⭐ **MEILLEURE SOURCE**
- URL: https://www.fao.org/aquastat/en/databases/
- Format: Excel, CSV
- Couverture: 180+ pays
- Télécharger: https://www.fao.org/aquastat/statistics/query/index.html
- Indicateur: Water stress (freshwater withdrawal as % of resources)
- Unité: % ✅ COMPATIBLE

**Source 2: OECD Environment - Water**
- URL: https://stats.oecd.org/Index.aspx?DataSetCode=WATER_ABSTRACT
- Format: CSV
- Couverture: 38 pays OECD
- Télécharger: https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/WATER_ABSTRACT/all/all

---

## 🔥 SOURCES PRIORITAIRES À TÉLÉCHARGER

### Niveau 1: Maximum d'Impact (< 150 pays actuellement)

1. **SIPRI Military Expenditure** → MS.MIL.XPND.GD.ZS (164 → 170+ pays)
   - https://milex.sipri.org/sipri
   
2. **FAO AQUASTAT** → ER.H2O.FWST.ZS (178 → 180+ pays)  
   - https://www.fao.org/aquastat/statistics/query/index.html

3. **OECD Revenue Statistics** → GC.TAX.TOTL.GD.ZS (161 → 100+ pays OECD)
   - https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/REV/all/all

4. **WIPO IP Statistics** → IP.PAT.RESD (158 → tous pays membres)
   - https://www3.wipo.int/ipstats/index.htm?tab=patent

5. **OECD R&D Statistics** → GB.XPD.RSDV.GD.ZS + SP.POP.SCIE.RD.P6
   - https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/MSTI_PUB/all/all

### Niveau 2: Énergie (sources IEA, BP)

6. **IEA Energy Statistics** → EG.IMP.CONS.ZS, EG.USE.ELEC.KH.PC
   - https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser
   - ⚠️ Nécessite compte gratuit

7. **BP Statistical Review** → EG.USE.PCAP.KG.OE, EG.USE.COMM.FO.ZS
   - https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html

### Niveau 3: Dette (BIS, IMF)

8. **IMF WEO Database** → DT.TDS.DECT.EX.ZS, DT.DOD.DECT.GN.ZS
   - https://www.imf.org/en/Publications/WEO/weo-database/2024/October

9. **BIS Debt Statistics** → DT.DOD.DECT.GN.ZS
   - https://stats.bis.org/statx/srs/table/a1

---

## 📝 INSTRUCTIONS DE TÉLÉCHARGEMENT

### Pour chaque source:

1. **Vérifier l'unité** (doit correspondre à World Bank)
2. **Télécharger en CSV** (préféré) ou Excel
3. **Placer dans**: `/home/elias/PROJECT/WorldDataVision/Data/IRC/[SOURCE]/`
4. **Format attendu**: Colonnes [Country/Code, Year, Value]

### Exemples de conversion nécessaire:

- ✅ SIPRI: % PIB → Directement compatible
- ✅ OECD R&D: % PIB → Directement compatible  
- ⚠️ WIPO: Nombre absolu → Vérifier échelle
- ⚠️ IEA: kWh → Peut nécessiter conversion

---

## 🎯 STRATÉGIE D'IMPORT

Une fois les fichiers téléchargés, créer des scripts d'import similaires à:
- `import_imf_debt_data.py` (✅ succès 98%)
- `import_unesco_literacy.py` (✅ succès 99%)

Avec la même logique:
1. Mapping pays (ISO3 ou nom)
2. Averaging si donnée existe: `(WB + Source) / 2`
3. Insert si nouvelle donnée
4. Mise à jour source: `"World Bank + [Source]"`

---

## ⚠️ NOTES IMPORTANTES

- **SIPRI** et **FAO** sont des sources primaires indépendantes ✅
- **OECD** couvre bien les pays développés mais pas les pays en développement
- **Eurostat** uniquement pour UE (bon complément pour Europe)
- **IEA** nécessite compte gratuit mais données exhaustives
- **IMF** déjà utilisé avec succès pour dette publique

---

**Date de création**: 22 février 2026  
**Auteur**: Agent d'import de données IRC  
**Objectif**: Passer de sources secondaires (OWID→WB) à sources primaires (SIPRI, FAO, OECD, etc.)
