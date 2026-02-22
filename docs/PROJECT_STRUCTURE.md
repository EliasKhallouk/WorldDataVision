# WorldDataVision - Structure du projet

## 📁 Organisation des fichiers

```
WorldDataVision/
│
├── 📄 README.md                     # Documentation d'origine du projet
├── 📄 README_WEB_APP.md            # Documentation complète de l'application web
├── 📄 QUICKSTART.md                # Guide de démarrage rapide
├── 📄 DATA_INTEGRATION.md          # Guide d'intégration des données
├── 🔧 setup.sh                     # Script d'installation automatique
│
├── 📂 BDD/                         # Scripts SQL
│   ├── creation_bdd.sql            # Création des tables
│   └── Parser_country_language.sql # Import des pays et langues
│
├── 📂 Data/                        # Fichiers de données CSV
│   ├── API_SP.POP.TOTL_DS2_en_csv_v2_40826.csv
│   ├── API_SP.POP.TOTL.FE.IN_DS2_en_csv_v2_1037.csv
│   ├── API_SP.POP.TOTL.MA.IN_DS2_en_csv_v2_4601.csv
│   └── country-codes.csv
│
├── 📂 backend/                     # API Node.js/Express
│   ├── 📄 package.json             # Dépendances backend
│   ├── 📄 server.js                # Point d'entrée du serveur
│   ├── 📄 .env.example             # Template de configuration
│   │
│   ├── 📂 config/
│   │   └── database.js             # Configuration PostgreSQL
│   │
│   ├── 📂 routes/
│   │   ├── countries.js            # Routes pour les pays
│   │   ├── population.js           # Routes pour les données de population
│   │   └── metadata.js             # Routes pour les métadonnées
│   │
│   └── 📂 scripts/
│       └── import_population_data.js # Script d'import des CSV
│
└── 📂 frontend/                    # Application React
    ├── 📄 package.json             # Dépendances frontend
    │
    ├── 📂 public/
    │   ├── index.html              # Page HTML principale
    │   └── world-map.svg           # Carte SVG du monde (téléchargée)
    │
    └── 📂 src/
        ├── 📄 index.js             # Point d'entrée React
        ├── 📄 index.css            # Styles globaux
        ├── 📄 App.js               # Composant principal
        ├── 📄 App.css              # Styles de l'app
        │
        ├── 📂 components/
        │   ├── WorldMap.js         # Carte interactive
        │   ├── WorldMap.css
        │   ├── FilterPanel.js      # Panneau de filtres
        │   ├── FilterPanel.css
        │   ├── Legend.js           # Légende de la carte
        │   ├── Legend.css
        │   ├── CountryDetails.js   # Modal de détails pays
        │   └── CountryDetails.css
        │
        ├── 📂 services/
        │   └── api.js              # Service d'API
        │
        └── 📂 utils/
            └── helpers.js          # Fonctions utilitaires
```

## 🔑 Fichiers clés

### Backend

| Fichier | Description |
|---------|-------------|
| `server.js` | Serveur Express, point d'entrée de l'API |
| `config/database.js` | Pool de connexion PostgreSQL |
| `routes/countries.js` | API pour récupérer les informations des pays |
| `routes/population.js` | API pour les données de population |
| `routes/metadata.js` | API pour les métadonnées (années, groupes d'âge, etc.) |
| `scripts/import_population_data.js` | Import automatique des données CSV |

### Frontend

| Fichier | Description |
|---------|-------------|
| `App.js` | Composant principal, gestion de l'état global |
| `components/WorldMap.js` | Carte SVG interactive avec coloration dynamique |
| `components/FilterPanel.js` | Filtres (année, sexe) |
| `components/Legend.js` | Légende avec échelle de couleurs |
| `components/CountryDetails.js` | Modal avec graphiques détaillés |
| `services/api.js` | Client HTTP pour communiquer avec le backend |
| `utils/helpers.js` | Formatage des nombres, calcul de couleurs |

## 🚀 Flux de données

```
┌─────────────┐
│ PostgreSQL  │ ← Données importées depuis CSV
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │ ← API Express (port 5000)
│   Node.js   │   Routes: /api/countries, /api/population, etc.
└──────┬──────┘
       │
       ↓ HTTP/REST
       │
┌─────────────┐
│  Frontend   │ ← Application React (port 3000)
│    React    │   Composants interactifs
└─────────────┘
       │
       ↓
┌─────────────┐
│ Navigateur  │ ← Interface utilisateur
│  (Chrome,   │   Carte interactive, filtres, graphiques
│  Firefox)   │
└─────────────┘
```

## 🎯 Points d'entrée

### Pour développer

1. **Backend**: Commencez par `backend/server.js`
2. **Frontend**: Commencez par `frontend/src/App.js`
3. **Base de données**: Consultez `BDD/creation_bdd.sql`

### Pour personnaliser

1. **Ajouter une route API**: Créez un fichier dans `backend/routes/`
2. **Ajouter un composant**: Créez un fichier dans `frontend/src/components/`
3. **Modifier les couleurs**: Éditez `frontend/src/utils/helpers.js` → `getColorForValue()`
4. **Ajouter un filtre**: Modifiez `frontend/src/components/FilterPanel.js`

## 📊 Données

### Tables PostgreSQL utilisées

- `country` - Liste des pays
- `population_stat` - Données de population
- `age_group` - Groupes d'âge
- `sex` - Catégories (male, female, total)
- `year_table` - Années disponibles (1950-2035)

### Fichiers CSV sources

- Population totale par pays et année
- Population féminine par pays et année
- Population masculine par pays et année

## 🔧 Technologies utilisées

### Backend
- Node.js 16+
- Express.js (serveur web)
- pg (client PostgreSQL)
- dotenv (variables d'environnement)
- cors (gestion CORS)
- csv-parser (import CSV)

### Frontend
- React 18
- Axios (requêtes HTTP)
- D3.js (manipulation SVG)
- Recharts (graphiques)

### Base de données
- PostgreSQL 12+

## 📝 Conventions de code

### Backend
- Routes dans `routes/`
- Logique métier dans les routes
- Connexion DB centralisée dans `config/`
- Scripts utilitaires dans `scripts/`

### Frontend
- Composants dans `components/`
- Un fichier CSS par composant
- Services API dans `services/`
- Utilitaires dans `utils/`

## 🐛 Débogage

### Logs backend
```bash
cd backend
npm start
# Les logs s'affichent dans le terminal
```

### Logs frontend
- Ouvrez la console du navigateur (F12)
- Vérifiez l'onglet Network pour les requêtes API
- Vérifiez l'onglet Console pour les erreurs React

### Base de données
```bash
psql -U postgres -d worlddatavision
# Requêtes SQL pour inspecter les données
```
