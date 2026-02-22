# 📥 Import de Données Our World in Data (OWID)

## 🎯 Objectif
Compléter les indicateurs IRC ayant une faible couverture en utilisant les données Our World in Data.

## 📊 Indicateurs IRC à Compléter

Les 12 indicateurs suivants seront enrichis avec les données OWID:

| Code World Bank | Couverture Actuelle | Dataset OWID | Description |
|-----------------|---------------------|--------------|-------------|
| `SE.ADT.LITR.ZS` | 177 pays | literacy-rates-among-adults | Taux d'alphabétisation adultes |
| `SP.POP.SCIE.RD.P6` | 144 pays | researchers-in-rd-per-million-people | Chercheurs en R&D |
| `GB.XPD.RSDV.GD.ZS` | 153 pays | research-and-development-expenditure-of-gdp | Dépenses R&D (% PIB) |
| `EG.USE.ELEC.KH.PC` | 150 pays | per-capita-electricity-use | Consommation électricité/habitant |
| `EG.USE.PCAP.KG.OE` | 179 pays | per-capita-energy-use | Consommation énergie/habitant |
| `AG.YLD.CREL.KG` | 181 pays | cereal-yield | Rendement céréales |
| `ER.H2O.FWST.ZS` | 178 pays | water-stress | Stress hydrique |
| `MS.MIL.XPND.GD.ZS` | 164 pays | military-expenditure-as-a-share-of-gdp | Dépenses militaires (% PIB) |
| `EG.IMP.CONS.ZS` | 145 pays | energy-imports-as-a-share-of-energy-use | Importations nettes énergie |
| `EG.USE.COMM.FO.ZS` | 179 pays | fossil-fuels-share-energy | Consommation fossiles (%) |
| `IP.PAT.RESD` | 158 pays | patent-applications-by-residents | Brevets résidents |
| `GC.TAX.TOTL.GD.ZS` | 161 pays | total-tax-revenue-gdp | Revenus fiscaux (% PIB) |

## 📥 Étape 1: Télécharger les Datasets OWID

### Option A: Téléchargement Manuel (Recommandé)

Pour chaque indicateur, visitez Our World in Data et téléchargez le CSV complet:

1. **Taux d'alphabétisation adultes**
   - URL: https://ourworldindata.org/grapher/literacy-rate-adults
   - Bouton: "Download" → "Full data (CSV)"
   - Sauvegarder: `Data/IRC/OWID/literacy-rates-among-adults.csv`

2. **Chercheurs en R&D**
   - URL: https://ourworldindata.org/grapher/researchers-in-rd
   - Sauvegarder: `Data/IRC/OWID/researchers-in-rd-per-million-people.csv`

3. **Dépenses R&D**
   - URL: https://ourworldindata.org/grapher/research-spending-gdp
   - Sauvegarder: `Data/IRC/OWID/research-and-development-expenditure-of-gdp.csv`

4. **Consommation électricité**
   - URL: https://ourworldindata.org/grapher/per-capita-electricity-consumption
   - Sauvegarder: `Data/IRC/OWID/per-capita-electricity-use.csv`

5. **Consommation énergie**
   - URL: https://ourworldindata.org/grapher/per-capita-energy-use
   - Sauvegarder: `Data/IRC/OWID/per-capita-energy-use.csv`

6. **Rendement céréales**
   - URL: https://ourworldindata.org/grapher/cereal-yield
   - Sauvegarder: `Data/IRC/OWID/cereal-yield.csv`

7. x **Stress hydrique**
   - URL: https://ourworldindata.org/grapher/water-stress
   - Sauvegarder: `Data/IRC/OWID/water-stress.csv`

8. **Dépenses militaires**
   - URL: https://ourworldindata.org/grapher/military-expenditure-as-a-share-of-gdp
   - Sauvegarder: `Data/IRC/OWID/military-expenditure-as-a-share-of-gdp.csv`

9. x **Importations énergie**
   - URL: https://ourworldindata.org/grapher/energy-imports
   - Sauvegarder: `Data/IRC/OWID/energy-imports-as-a-share-of-energy-use.csv`

10. **Combustibles fossiles**
    - URL: https://ourworldindata.org/grapher/fossil-fuels-share-energy
    - Sauvegarder: `Data/IRC/OWID/fossil-fuels-share-energy.csv`

11. x **Brevets résidents**
    - URL: https://ourworldindata.org/grapher/patent-applications-residents
    - Sauvegarder: `Data/IRC/OWID/patent-applications-by-residents.csv`

12. **Revenus fiscaux**
    - URL: https://ourworldindata.org/grapher/tax-revenues-as-a-share-of-gdp-ictd
    - Sauvegarder: `Data/IRC/OWID/total-tax-revenue-gdp.csv`

### Option B: Script Automatique (Peut Échouer)

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
./download_owid_datasets.sh
```

⚠️ **Note**: Le téléchargement automatique peut échouer. Préférez l'Option A.

## 📂 Structure des Fichiers

Créez le dossier OWID:
```bash
mkdir -p /home/elias/PROJECT/WorldDataVision/Data/IRC/OWID
```

Structure attendue:
```
Data/IRC/OWID/
├── literacy-rates-among-adults.csv
├── researchers-in-rd-per-million-people.csv
├── research-and-development-expenditure-of-gdp.csv
├── per-capita-electricity-use.csv
├── per-capita-energy-use.csv
├── cereal-yield.csv
├── water-stress.csv
├── military-expenditure-as-a-share-of-gdp.csv
├── energy-imports-as-a-share-of-energy-use.csv
├── fossil-fuels-share-energy.csv
├── patent-applications-by-residents.csv
└── total-tax-revenue-gdp.csv
```

## 🚀 Étape 2: Exécuter l'Import

Une fois tous les fichiers téléchargés:

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
source ../../.venv/bin/activate
python3 import_owid_data.py
```

## 📊 Stratégie d'Import

Le script `import_owid_data.py` fonctionne ainsi:

1. **Lecture des CSV OWID**: Format standard (Entity, Code, Year, [Value])
2. **Matching des pays**: Utilise les codes ISO3 (identiques à UNESCO)
3. **Fusion intelligente**:
   - Si **donnée absente**: INSERT valeur OWID
   - Si **donnée existante**: UPDATE avec `(World Bank + OWID) / 2`
4. **Mise à jour source**: `"World Bank + Our World in Data ([description])"`
5. **Exclusion automatique**: Ignore les agrégats (OWID_WRL, régions SDG, etc.)

## ✅ Validation

Après l'import, vérifiez l'amélioration de la couverture:

```bash
# Réexécuter le diagnostic IRC
cd ../../notebooks
jupyter notebook diagnostic_irc_completeness.ipynb
```

Comparez les résultats **avant/après** pour les 12 indicateurs.

## 📈 Résultats Attendus

- **Amélioration couverture**: +10-30 pays par indicateur
- **Enrichissement temporel**: Données historiques étendues
- **Qualité**: Moyenne World Bank + OWID = données robustes
- **Taux de succès attendu**: ~98% (comme IMF et UNESCO)

## 🔍 Vérification des Unités

⚠️ **IMPORTANT**: Vérifiez que les unités sont identiques entre World Bank et OWID:

| Indicateur | Unité World Bank | Unité OWID | Compatible? |
|------------|------------------|------------|-------------|
| SE.ADT.LITR.ZS | % (15+) | % (15+) | ✅ OUI |
| SP.POP.SCIE.RD.P6 | par million | par million | ✅ OUI |
| GB.XPD.RSDV.GD.ZS | % du PIB | % du PIB | ✅ OUI |
| EG.USE.ELEC.KH.PC | kWh/capita | kWh/capita | ✅ OUI |
| EG.USE.PCAP.KG.OE | kg oil eq/capita | kWh/capita | ⚠️ CONVERSION |
| AG.YLD.CREL.KG | kg/hectare | tonnes/hectare | ⚠️ CONVERSION |
| MS.MIL.XPND.GD.ZS | % du PIB | % du PIB | ✅ OUI |
| GC.TAX.TOTL.GD.ZS | % du PIB | % du PIB | ✅ OUI |

Si les unités diffèrent, ajustez le script avant import!

## 🛠️ Debugging

En cas d'erreur:

```bash
# Vérifier les fichiers téléchargés
ls -lh /home/elias/PROJECT/WorldDataVision/Data/IRC/OWID/

# Tester la lecture d'un fichier
head -20 /home/elias/PROJECT/WorldDataVision/Data/IRC/OWID/literacy-rates-among-adults.csv

# Vérifier les colonnes
head -1 /home/elias/PROJECT/WorldDataVision/Data/IRC/OWID/*.csv
```

## 📝 Notes

- Les fichiers OWID contiennent souvent des **agrégats régionaux** (OWID_WRL, etc.) qui seront automatiquement ignorés
- OWID utilise les **codes ISO3 standard** (pas besoin de mapping complexe comme IMF)
- La **stratégie d'averaging** garantit qu'aucune donnée World Bank n'est écrasée
- Les sources sont **mises à jour automatiquement** pour traçabilité
