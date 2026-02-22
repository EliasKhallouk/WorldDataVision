# 🗂️ Guide de Navigation Rapide - WorldDataVision

## 📍 Où Trouver Quoi ?

### 💾 Importer des Données
```bash
cd scripts/imports/
```
- `import_eia_*.py` - Données énergie (EIA)
- `import_ember_*.py` - Données climat (Ember)
- `import_eurostat_*.py` - Données Europe (Eurostat)
- `import_who_*.py` - Données santé (OMS/WHO)
- `import_unesco_*.py` - Données éducation (UNESCO)
- `import_imf_*.py` - Données dette (FMI)
- `import_owid_*.py` - Our World in Data
- `import_fao_*.py` - Données eau (FAO)
- `import_wipo_*.py` - Données brevets (WIPO)
- `import_wb_*.py` - World Bank

### 🔍 Analyser et Diagnostiquer
```bash
cd scripts/analysis/
```
- `analyze_*.py` - Analyses thématiques
- `diagnose_*.py` - Diagnostics de problèmes
- `test_*.py` - Tests d'APIs externes

### 🛠️ Utilitaires
```bash
cd scripts/utils/
```
- `compute_irc.js` - Calcul de l'IRC
- `validate_irc_data.js` - Validation données IRC
- `generate_irc_report_pdf.py` - Génération rapport PDF
- `download_*.py` - Téléchargement datasets

### 🧪 Tests Backend
```bash
cd backend/tests/
```
- `test_*.js` - Tests fonctionnels
- `check_*.js` - Vérifications BDD

### 📊 Analyser avec Jupyter
```bash
cd notebooks/
jupyter notebook diagnostic_irc_completeness.ipynb
```

### 💾 Base de Données
```bash
cd BDD/
psql -U elias -d worlddatavision -f creation_bdd.sql
```

### 📝 Requêtes SQL
```bash
cd sql_queries/
psql -U elias -d worlddatavision -f <requete>.sql
```

### 📚 Documentation
```bash
cd docs/
```
- Guides, corrections, documentations techniques
- `archives/` - Fichiers obsolètes

## ⚡ Commandes Rapides

### Démarrer le Projet
```bash
# Backend
cd backend && npm start

# Frontend (terminal séparé)
cd frontend && npm start
```

### Lancer un Import
```bash
# Python
cd scripts/imports && python3 import_<source>_<type>.py

# Node.js
cd scripts/imports && node import_<type>_data.js
```

### Analyser la Complétude IRC
```bash
cd scripts/analysis
python3 diagnose_irc_indicators.py
```

### Calculer l'IRC
```bash
cd scripts/utils
node compute_irc.js
```

### Tests Rapides
```bash
cd backend/tests
node check_<aspect>.js
```

## 🎯 Exemples d'Utilisation

### Importer Données OMS (Santé)
```bash
cd scripts/imports
python3 import_who_simple.py
```

### Analyser Couverture Indicateurs
```bash
cd scripts/analysis
python3 diagnose_irc_indicators.py
```

### Générer Rapport IRC PDF
```bash
cd scripts/utils
python3 generate_irc_report_pdf.py
```

### Tester API Backend
```bash
cd backend/tests
node check_debt_sources.js
```

## 📁 Structure Rapide

```
WorldDataVision/
├── backend/          → Serveur Node.js + API
│   └── tests/        → Tests backend
├── frontend/         → Application React
├── scripts/
│   ├── imports/      → Scripts d'import (47 fichiers)
│   ├── analysis/     → Scripts d'analyse (9 fichiers)
│   └── utils/        → Utilitaires (10 fichiers)
├── notebooks/        → Jupyter pour analyse exploratoire
├── BDD/              → Scripts SQL
├── Data/             → Datasets bruts
├── docs/             → Documentation
│   └── archives/     → Fichiers obsolètes
├── sql_queries/      → Requêtes réutilisables
└── images/           → Captures/visualisations
```

## 🔗 Fichiers Importants

- `README.md` - Documentation principale
- `ORGANISATION.md` - Structure détaillée
- `REORGANISATION_SUMMARY.txt` - Résumé réorganisation
- `QUICKSTART.md` - Démarrage rapide
- `setup.sh` - Installation

---
*Dernière mise à jour : 22 février 2026*
