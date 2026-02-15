# 🌍 WorldDataVision

## Application web interactive de visualisation de données démographiques mondiales

Une application web moderne construite avec React et Node.js pour visualiser les données de population mondiale sur une carte interactive.

---

## 🎉 Nouveau : Interface Web Interactive !

Une **interface web complète** a été créée pour visualiser vos données sur une carte du monde interactive !

### ✨ Fonctionnalités principales

- 🗺️ **Carte interactive** basée sur SVG avec coloration dynamique
- 🎛️ **Filtres** par année et sexe
- 📊 **Graphiques** d'évolution et pyramide des âges
- 📱 **Responsive** - fonctionne sur tous les appareils
- 🔌 **API RESTful** complète pour accéder aux données

### 🚀 Démarrage rapide

```bash
# 1. Installation automatique
./setup.sh

# 2. Configuration PostgreSQL (exécuter les scripts SQL)
psql -U postgres -c "CREATE DATABASE worlddatavision;"
psql -U postgres -d worlddatavision -f BDD/creation_bdd.sql
psql -U postgres -d worlddatavision -f BDD/Parser_country_language.sql

# 3. Importer les données
cd backend && npm run import-data

# 4. Lancer l'application (2 terminaux)
cd backend && npm start     # Terminal 1
cd frontend && npm start    # Terminal 2

# 5. Accéder à l'application
# Interface: http://localhost:3000
# API: http://localhost:5000/api
```

---

## 📚 Documentation complète

| Fichier | Description |
|---------|-------------|
| **[WELCOME.txt](WELCOME.txt)** | Message de bienvenue avec vue d'ensemble |
| **[README_WEB_APP.md](README_WEB_APP.md)** | 📖 Documentation complète de l'application |
| **[QUICKSTART.md](QUICKSTART.md)** | ⚡ Guide de démarrage rapide (5 minutes) |
| **[SUMMARY.md](SUMMARY.md)** | 📊 Résumé visuel de ce qui a été créé |
| **[NEXT_STEPS.md](NEXT_STEPS.md)** | ➡️ Prochaines étapes à suivre |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | 🏗️ Architecture et structure du projet |
| **[CUSTOMIZATION.md](CUSTOMIZATION.md)** | 🎨 Guide de personnalisation |
| **[DATA_INTEGRATION.md](DATA_INTEGRATION.md)** | 🔌 Comment brancher vos données |
| **[COMMANDS.md](COMMANDS.md)** | 💻 Aide-mémoire de toutes les commandes |

---

## 🏗️ Structure du projet

```
WorldDataVision/
├── backend/              # API Node.js/Express
│   ├── config/          # Configuration PostgreSQL
│   ├── routes/          # Routes API (countries, population, metadata)
│   ├── scripts/         # Scripts d'import de données
│   └── server.js        # Serveur Express
│
├── frontend/            # Application React
│   ├── public/          # Fichiers statiques + carte SVG
│   └── src/
│       ├── components/  # WorldMap, FilterPanel, Legend, CountryDetails
│       ├── services/    # Client API
│       └── utils/       # Fonctions utilitaires
│
├── BDD/                 # Scripts SQL
│   ├── creation_bdd.sql
│   └── Parser_country_language.sql
│
├── Data/                # Fichiers CSV de données
│   └── ...
│
├── setup.sh             # Script d'installation automatique
└── *.md                 # Documentation complète
```

---

## 🛠️ Technologies utilisées

- **Backend:** Node.js + Express + PostgreSQL
- **Frontend:** React + D3.js + Recharts
- **Base de données:** PostgreSQL 12+
- **Carte:** SVG World Map (template GitHub)

---

## 📊 Données

Le projet utilise des données de population de la Banque Mondiale :
- Population totale par pays et année
- Population par sexe (hommes/femmes)
- Années : 1950-2035
- 249 pays

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