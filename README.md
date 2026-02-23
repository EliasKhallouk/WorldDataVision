# 🌍 WorldDataVision

## Plateforme d'Analyse de la Résilience Civilisationnelle Mondiale

Projet de visualisation et d'analyse des données mondiales pour calculer l'**Index de Résilience Civilisationnelle (IRC)** - un indicateur composite de 75 indicateurs socio-économiques couvrant 217 pays sur la période 1950-2035.

---

## 🎯 Objectif du Projet

**Répondre à la question fondamentale :**  
*"Quels pays sont réellement préparés à traverser les 20 prochaines années ?"*

L'IRC mesure la capacité d'un pays à maintenir son développement et sa stabilité face aux défis du 21ème siècle : transitions démographique, énergétique, climatique, technologique, et géopolitique.

---

## 📊 État Actuel (22 février 2026)

### Données Importées ✅

- **75 indicateurs IRC** (augmenté de 74 → 75 avec import OMS)
- **6 sources de données** : World Bank, OMS, UNESCO, Eurostat, Ember, EIA
- **217 pays** couverts
- **>115,000 valeurs** importées
- **92% des indicateurs** avec couverture excellente (≥200 pays)

### Dernière Optimisation : Import OMS (22 février 2026)

- **12,774 valeurs** ajoutées depuis WHO Global Health Observatory
- Catégorie Santé optimisée : **75% d'excellents** (6/8 indicateurs ≥200 pays)
- Indicateurs enrichis :
  - SP.DYN.IMRT.IN : 196 → 200 pays (+4)
  - SP.DYN.LE00.IN : 212 → 216 pays (+4)

### Réorganisation Complète ✅

- **76 scripts** organisés (imports/analysis/utils)
- **40+ documents** hiérarchisés (guides/specs/reports)
- Structure professionnelle avec .gitignore, README partout

---

## 🏗️ Architecture IRC

```
IRC Global (0-100)
├─ [25%] Démographie & Structure Population (15 indicateurs)
├─ [20%] Économie & Stabilité (7 indicateurs)
├─ [20%] Gouvernance & Institutions (6 indicateurs)
├─ [15%] Capital Humain - Santé + Éducation (8 indicateurs)
├─ [10%] Souveraineté Matérielle - Énergie + Agriculture (20 indicateurs)
├─ [5%]  Innovation & Technologie (9 indicateurs)
└─ [5%]  Durabilité Environnementale (5 indicateurs)
```

**Méthodologie :** Normalisation winsorisée → Moyenne géométrique (sous-piliers) → Agrégation pondérée (piliers)

**Documentation complète :** [METHODOLOGIE_CALCUL_IRC.md](docs/METHODOLOGIE_CALCUL_IRC.md) v1.1

---

## 🚀 Démarrage Rapide

### Lancer l'Application

```bash
# Backend API (Terminal 1)
cd backend
npm start        # Port 5000

# Frontend UI (Terminal 2)
cd frontend
npm start        # Port 3000
```

**Accès :**
- 🌐 Interface web : http://localhost:3000
- 🔌 API : http://localhost:5000/api

### Import Données OMS (Optionnel)

```bash
# Activer environnement Python
source .venv/bin/activate

# Import OMS (déjà effectué, mais peut être re-lancé)
python scripts/imports/import_who_simple.py
```

---

## 📚 Documentation

### 🆕 Documents Récents (22 février 2026)

- **[📊 État du Projet](docs/ETAT_PROJET_22FEV2026.md)** - Vue complète de l'état actuel
- **[📖 Sources de Données](docs/SOURCES_DONNEES.md)** - Guide des 6 sources (World Bank, OMS, UNESCO, etc.)
- **[📝 Journal des MAJ](docs/JOURNAL_MAJ_22FEV2026.md)** - Détail des mises à jour documentation

### 📘 Documentation IRC

- **[Méthodologie IRC v1.1](docs/METHODOLOGIE_CALCUL_IRC.md)** - Calcul complet de l'IRC
- **[Liste 75 Indicateurs](docs/LISTE_INDICATEURS_IRC.md)** - Tous les indicateurs détaillés
- **[Prochaines Étapes](docs/reports/NEXT_STEPS.md)** - Plan détaillé 7 semaines

### 📗 Guides Utilisateur

- **[Index Documentation](docs/INDEX.md)** - Index complet de tous les documents
- **[Quickstart](docs/guides/QUICKSTART.md)** - Démarrage rapide
- **[Commandes](docs/guides/COMMANDS.md)** - Aide-mémoire commandes

### 📙 Organisation

- **[Navigation](NAVIGATION.md)** - Guide de navigation projet
- **[Organisation](ORGANISATION.md)** - Structure détaillée
- **[Projet Organisé](PROJET_ORGANISE.md)** - Vue d'ensemble organisation

---

## 🗂️ Structure du Projet

```
WorldDataVision/
├── docs/                          # 📚 Documentation (40+ fichiers)
│   ├── guides/                    # Guides utilisateurs
│   ├── specs/                     # Spécifications techniques
│   ├── reports/                   # Rapports d'analyse
│   ├── METHODOLOGIE_CALCUL_IRC.md # Méthodologie v1.1
│   ├── LISTE_INDICATEURS_IRC.md   # 75 indicateurs
│   ├── SOURCES_DONNEES.md         # Guide 6 sources ⭐
│   └── ETAT_PROJET_22FEV2026.md   # État actuel ⭐
│
├── scripts/                       # 🛠️ Scripts (76 fichiers)
│   ├── imports/                   # 47 scripts d'import
│   ├── analysis/                  # 9 scripts d'analyse
│   └── utils/                     # 10 utilitaires
│
├── backend/                       # ⚙️ API Node.js/Express
│   ├── config/                    # Configuration PostgreSQL
│   ├── routes/                    # Routes API
│   ├── tests/                     # Tests unitaires
│   └── server.js                  # Serveur (port 5000)
│
├── frontend/                      # 🌐 Application React
│   ├── src/
│   │   ├── components/            # Composants UI
│   │   ├── services/              # Client API
│   │   └── utils/                 # Utilitaires
│   └── public/                    # Fichiers statiques
│
├── BDD/                           # 💾 Scripts SQL
│   └── creation_bdd.sql           # Schéma base de données
│
├── Data/                          # 📂 Données sources
│   ├── Raw/                       # Données brutes
│   ├── Processed/                 # Données traitées
│   └── Archives/                  # Anciennes versions
│
├── notebooks/                     # 📓 Jupyter Notebooks
│   └── diagnostic_*.ipynb         # Analyses IRC
│
├── logs/                          # 📋 Logs centralisés
├── sql_queries/                   # 💾 Requêtes SQL
└── images/                        # 🖼️ Ressources graphiques
```

---

## 🛠️ Stack Technique

### Backend
- **Node.js 18+** - Runtime JavaScript
- **Express.js** - Framework API RESTful
- **PostgreSQL 14+** - Base de données relationnelle
- **pg** - Client PostgreSQL pour Node.js

### Frontend
- **React 18** - Framework UI
- **D3.js** - Visualisations interactives
- **Recharts** - Graphiques
- **Leaflet** - Cartes interactives (futur)

### Scripts & Analyse
- **Python 3.10+** - Scripts d'import
- **Jupyter** - Notebooks d'analyse
- **pandas, numpy** - Analyse de données
- **psycopg2** - Client PostgreSQL pour Python

### Base de Données
- **PostgreSQL** - SGBD principal
- **Tables :** country (217 pays), indicator (75 indicateurs), indicator_value (>115K valeurs), year_table (1950-2035)

---

## 📊 Sources de Données

1. **🏦 World Bank API** - Source principale (74 indicateurs)
2. **🏥 OMS (WHO GHO)** - Santé (2 indicateurs enrichis) ⭐ Nouveau
3. **🎓 UNESCO** - Éducation et Innovation
4. **🇪🇺 Eurostat** - Innovation Europe
5. **⚡ Ember Climate** - Électricité mondiale
6. **🛢️ EIA (US)** - Données énergétiques

**Documentation complète :** [SOURCES_DONNEES.md](docs/SOURCES_DONNEES.md)

---

## 📈 Statistiques Projet

### Données
- **75 indicateurs** IRC (catégories : Démographie, Économie, Gouvernance, Santé, Éducation, Énergie, Agriculture, Environnement, Innovation, Technologies)
- **217 pays** couverts
- **>115,000 valeurs** importées
- **Période :** 1950-2035 (86 années)
- **Couverture :** 92% des indicateurs avec ≥200 pays

### Code
- **~2,500 lignes** backend (Node.js)
- **~4,000 lignes** frontend (React)
- **76 scripts** Python (imports, analysis, utils)
- **40+ documents** markdown (guides, specs, reports)

---

## 🎯 Prochaines Étapes

### Phase 1 : Calcul IRC (Priorité Haute 🔴)

1. **Normalisation** des 75 indicateurs (winsorization p2.5-p97.5)
2. **Calcul sous-piliers** (moyenne géométrique pondérée)
3. **Agrégation piliers** et IRC global (0-100)
4. **Export résultats** (CSV/JSON + table PostgreSQL)

### Phase 2 : Validation Scientifique (Priorité Haute 🟠)

- Tests corrélations (IRC vs HDI, Democracy Index, PIB)
- Analyse sensibilité (variation pondérations ±20%)
- Validation historique (Venezuela, Corée du Sud, COVID-19)

### Phase 3 : API & Frontend IRC (Priorité Moyenne 🟡)

- Routes API IRC (`/api/irc/score`, `/ranking`, `/evolution`)
- Dashboard IRC (carte choroplèthe, radar chart, évolution)
- Visualisations interactives

**Plan complet :** [NEXT_STEPS.md](docs/reports/NEXT_STEPS.md) (7 semaines détaillées)

---

## 🤝 Contribution

### Branches de Travail

- `main` - Production stable
- `develop` - Développement en cours
- `feature/*` - Nouvelles fonctionnalités
- `fix/*` - Corrections de bugs

### Workflow Git

```bash
# Créer branche feature
git checkout -b feature/calcul-irc

# Commits réguliers
git add .
git commit -m "feat: implémentation normalisation IRC"

# Push et merge request
git push origin feature/calcul-irc
```

---

## 📄 Licence

Ce projet est un projet éducatif et de recherche.

---

## 📞 Contact

**Projet :** WorldDataVision  
**Utilisateur :** Elias  
**Environnement :** Linux  
**Localisation :** `/home/elias/PROJECT/WorldDataVision`

---

## 📝 Changelog

### 22 février 2026
- ✅ Import 12,774 valeurs OMS (WHO Global Health Observatory)
- ✅ Enrichissement SP.DYN.IMRT.IN (mortalité infantile) : 196 → 200 pays
- ✅ Enrichissement SP.DYN.LE00.IN (espérance de vie) : 212 → 216 pays
- ✅ Catégorie Santé optimisée : 75% d'indicateurs excellents
- ✅ Réorganisation complète projet (76 scripts, 40+ docs)
- ✅ Documentation mise à jour (v1.1, nouveaux guides)
- ✅ Total indicateurs IRC : 74 → 75

### 21 février 2026
- ✅ Imports UNESCO, Eurostat, Ember, EIA
- ✅ Optimisation catégories Innovation (100%) et Énergie (92%)
- ✅ Méthodologie IRC v1.0 définie

### Avant 21 février 2026
- ✅ Import initial World Bank (74 indicateurs)
- ✅ Configuration base PostgreSQL
- ✅ Développement backend API (Express.js)
- ✅ Développement frontend (React)

---

**Dernière mise à jour : 22 février 2026**  
**Statut : ✅ Données optimisées - Prêt pour calcul IRC**

**Source** :
 - https://data.worldbank.org/indicator/SP.POP.TOTL
 - https://simplelocalize.io/data/countries/?q=French

---

## 🎯 Premiers pas

1. **Lisez [NEXT_STEPS.md](NEXT_STEPS.md)** pour une vue d'ensemble des étapes
2. **Exécutez `./setup.sh`** pour installer automatiquement les dépendances
3. **Suivez [QUICKSTART.md](QUICKSTART.md)** pour le démarrage rapide
4. **Consultez [README_WEB_APP.md](README_WEB_APP.md)** pour la documentation complète

---

## 📸 Aperçu de l'interface

L'application affiche :
- Une carte du monde interactive colorée selon les données de population
- Des filtres pour sélectionner l'année et la catégorie (homme/femme/total)
- Une légende avec échelle de couleurs
- Des statistiques globales
- Un modal de détails avec graphiques pour chaque pays (clic sur pays)

---

## 🤝 Support

Toute la documentation nécessaire est incluse dans les fichiers `.md` listés ci-dessus.

Pour des questions spécifiques :
- Configuration : voir [QUICKSTART.md](QUICKSTART.md)
- Personnalisation : voir [CUSTOMIZATION.md](CUSTOMIZATION.md)
- Intégration de données : voir [DATA_INTEGRATION.md](DATA_INTEGRATION.md)
- Commandes : voir [COMMANDS.md](COMMANDS.md)

---

**Projet de base de données pour les données démographiques mondiales avec interface web interactive.**
- https://data.worldbank.org/indicator/SP.POP.TOTL.MA.IN
- https://data.worldbank.org/indicator/SP.POP.TOTL.FE.IN