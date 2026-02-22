# 📁 Organisation du Projet WorldDataVision

Ce document décrit la structure organisée du projet après réorganisation du 22 février 2026.

## 📂 Structure des Dossiers

```
WorldDataVision/
│
├── 📁 backend/                    # Serveur Node.js
│   ├── config/                   # Configuration (database.js)
│   ├── routes/                   # Routes API (countries, indicators, population)
│   ├── tests/                    # Tests et vérifications backend
│   │   ├── check_*.js           # Scripts de vérification
│   │   ├── test_*.js            # Tests unitaires
│   │   └── quick_test.js        # Tests rapides
│   ├── server.js                # Point d'entrée serveur
│   ├── import_who.js            # Import OMS/WHO
│   └── package.json             # Dépendances Node.js
│
├── 📁 frontend/                   # Application React
│   ├── public/                   # Fichiers statiques
│   ├── src/                      # Code source React
│   │   ├── components/          # Composants UI
│   │   ├── services/            # Services API
│   │   └── utils/               # Utilitaires
│   └── package.json             # Dépendances React
│
├── 📁 scripts/                    # Scripts Python
│   ├── 📁 imports/               # Scripts d'import de données
│   │   ├── import_eia_*.py      # Import données EIA (énergie)
│   │   ├── import_imf_debt.py   # Import données FMI (dette)
│   │   ├── import_who_*.py      # Import données OMS (santé)
│   │   ├── import_owid_*.py     # Import Our World in Data
│   │   ├── import_unesco_*.py   # Import UNESCO (éducation)
│   │   └── import_*.js          # Imports Node.js (population, âge, etc.)
│   │
│   ├── 📁 analysis/              # Scripts d'analyse
│   │   ├── analyze_*.py         # Analyses diverses (dette, EIA, santé)
│   │   ├── diagnose_*.py        # Diagnostics
│   │   └── test_*.py            # Tests d'API externes
│   │
│   ├── 📁 utils/                 # Scripts utilitaires
│   │   ├── compute_irc.js       # Calcul de l'IRC
│   │   ├── validate_irc_data.js # Validation données IRC
│   │   ├── generate_*.py        # Génération rapports/données
│   │   ├── download_*.py        # Téléchargement datasets
│   │   └── insert_*.py          # Insertion en base
│   │
│   └── requirements_irc.txt     # Dépendances Python
│
├── 📁 notebooks/                  # Jupyter Notebooks
│   └── diagnostic_irc_completeness.ipynb  # Analyse complétude IRC
│
├── 📁 BDD/                        # Scripts SQL base de données
│   ├── creation_bdd.sql         # Création schéma
│   └── Parser_*.sql             # Parsers données
│
├── 📁 Data/                       # Données brutes
│   ├── Age/                      # Données démographiques par âge
│   ├── POP.*.csv                # Données population World Bank
│   └── country-codes.csv        # Codes pays
│
├── 📁 docs/                       # Documentation
│   ├── archives/                # Fichiers obsolètes archivés
│   ├── API_INDICATORS_DOCUMENTATION.md
│   ├── GUIDE_*.md               # Guides utilisateur
│   ├── CORRECTION_*.md          # Notes de correction
│   └── IMPLEMENTATION_*.md      # Documentation technique
│
├── 📁 sql_queries/               # Requêtes SQL réutilisables
│   ├── check_who.sql            # Vérification import OMS
│   └── temp_query.sql           # Requêtes temporaires
│
├── 📁 images/                     # Images et captures d'écran
│   └── variable-*.png           # Visualisations
│
├── 📁 tests/                      # Tests globaux projet
│
├── 📁 analysis_outputs/          # Résultats d'analyses
│
├── 📄 README.md                   # Documentation principale
├── 📄 QUICKSTART.md              # Démarrage rapide
├── 📄 setup.sh                   # Script installation
└── 📄 download-map.sh            # Téléchargement carte monde

```

## 🎯 Conventions de Nommage

### Scripts d'Import (`scripts/imports/`)
- `import_<source>_*.py` - Import depuis une source externe
- Exemples : `import_eia_corrected.py`, `import_who_simple.py`

### Scripts d'Analyse (`scripts/analysis/`)
- `analyze_<sujet>.py` - Analyse d'un sujet
- `diagnose_<probleme>.py` - Diagnostic d'un problème
- `test_<api>.py` - Test d'une API externe
- Exemples : `analyze_health_who.py`, `diagnose_irc_indicators.py`

### Scripts Utilitaires (`scripts/utils/`)
- `generate_*.py` - Génération de rapports/données
- `download_*.py` - Téléchargement de datasets
- `compute_*.js` - Calculs complexes
- `validate_*.js` - Validation de données

### Tests Backend (`backend/tests/`)
- `test_*.js` - Tests unitaires/fonctionnels
- `check_*.js` - Vérifications et diagnostics
- `quick_test.js` - Tests rapides

## 📊 Flux de Travail

### 1. Import de Données
```bash
# Python
cd scripts/imports/
python3 import_<source>_<indicateur>.py

# Node.js
node import_<type>_data.js
```

### 2. Analyse et Diagnostic
```bash
cd scripts/analysis/
python3 analyze_<sujet>.py
python3 diagnose_<probleme>.py
```

### 3. Génération Rapports
```bash
cd scripts/utils/
python3 generate_irc_report_pdf.py
node compute_irc.js
```

### 4. Validation
```bash
cd backend/tests/
node check_<aspect>.js
node test_<fonctionnalite>.js
```

## 🔧 Maintenance

### Ajouter un Nouveau Script

1. **Import de données** → `scripts/imports/`
2. **Analyse/Diagnostic** → `scripts/analysis/`
3. **Utilitaire** → `scripts/utils/`
4. **Test backend** → `backend/tests/`

### Archiver un Fichier Obsolète

```bash
mv <fichier> docs/archives/
```

### Nettoyer les Fichiers Temporaires

```bash
# Depuis la racine du projet
rm -f *.log
rm -f *~
rm -f *.tmp
```

## 📝 Notes

- Les notebooks Jupyter sont dans `notebooks/` pour l'analyse exploratoire
- Les logs d'import sont généralement dans le même dossier que le script
- La documentation est centralisée dans `docs/`
- Les requêtes SQL réutilisables sont dans `sql_queries/`

## 🚀 Commandes Rapides

```bash
# Démarrer le backend
cd backend && npm start

# Démarrer le frontend
cd frontend && npm start

# Installer les dépendances Python
pip install -r scripts/requirements_irc.txt

# Lancer un diagnostic complet
python3 scripts/analysis/diagnose_irc_indicators.py
```

---

*Dernière mise à jour : 22 février 2026*
