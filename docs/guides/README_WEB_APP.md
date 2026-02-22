# WorldDataVision - Interface Web Interactive

Application web moderne pour visualiser les données de population mondiale avec une carte interactive.

## 🚀 Fonctionnalités

- 🌍 Carte du monde interactive basée sur SVG
- 📊 Visualisation des données de population par pays
- 🎨 Échelle de couleurs dynamique
- 🔍 Filtres par année, sexe et groupe d'âge
- 📱 Interface responsive
- 🖱️ Interactions : survol pour aperçu, clic pour détails complets
- 📈 Légende et statistiques en temps réel

## 🏗️ Architecture

```
WorldDataVision/
├── backend/              # API Node.js/Express
│   ├── server.js        # Point d'entrée du serveur
│   ├── config/          # Configuration de la base de données
│   ├── routes/          # Routes API
│   ├── controllers/     # Logique métier
│   └── package.json     # Dépendances backend
├── frontend/            # Application React
│   ├── src/
│   │   ├── components/  # Composants React
│   │   ├── services/    # Services API
│   │   ├── assets/      # Ressources statiques
│   │   └── App.js       # Composant principal
│   └── package.json     # Dépendances frontend
├── BDD/                 # Scripts SQL existants
└── Data/                # Données CSV existantes
```

## 📋 Prérequis

- Node.js 16+ et npm
- PostgreSQL 12+
- Git

## ⚙️ Installation et Configuration

### 1. Configuration de la base de données PostgreSQL

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE worlddatavision;

# Se connecter à la base
\c worlddatavision

# Exécuter les scripts de création
\i /home/elias/PROJECT/WorldDataVision/BDD/creation_bdd.sql
\i /home/elias/PROJECT/WorldDataVision/BDD/Parser_country_language.sql
```

### 2. Installation du Backend

```bash
cd backend

# Installer les dépendances
npm install

# Créer le fichier .env
cp .env.example .env

# Éditer .env avec vos identifiants PostgreSQL
nano .env
```

Contenu du fichier `.env` :
```env
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=worlddatavision
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
```

### 3. Installation du Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Créer le fichier .env
cp .env.example .env
```

Contenu du fichier `.env` :
```env
REACT_APP_API_URL=http://localhost:5000/api
```

## 🚀 Démarrage de l'application

### Démarrer le backend (API)

```bash
cd backend
npm start
```

L'API sera accessible sur `http://localhost:5000`

### Démarrer le frontend

```bash
cd frontend
npm start
```

L'interface web sera accessible sur `http://localhost:3000`

## 🔌 Endpoints API

### GET `/api/countries`
Récupère la liste de tous les pays avec leurs codes ISO.

### GET `/api/population/:iso3`
Récupère les données de population pour un pays spécifique.

**Paramètres de requête :**
- `year` : Année (1950-2035)
- `sex` : Sexe (male, female, total)
- `ageGroup` : Groupe d'âge (id du groupe)

### GET `/api/population/summary`
Récupère un résumé des populations pour tous les pays.

**Paramètres de requête :**
- `year` : Année (défaut: année la plus récente)
- `sex` : Sexe (défaut: total)

### GET `/api/years`
Récupère la liste des années disponibles.

### GET `/api/age-groups`
Récupère la liste des groupes d'âge.

### GET `/api/sex-categories`
Récupère les catégories de sexe.

## 📊 Charger vos données réelles

### 1. Préparer un script d'importation des données CSV

Créez un script `import_population_data.js` dans le dossier `backend/scripts/` pour importer vos fichiers CSV :

```bash
cd backend
node scripts/import_population_data.js
```

### 2. Format des données attendues

Vos fichiers CSV de population doivent être parsés et insérés dans la table `population_stat` :

```sql
INSERT INTO population_stat (country_id, age_group_id, sex_id, year, population_count, source)
VALUES (...);
```

Le script d'importation fourni gère automatiquement cette conversion.

## 🎨 Personnalisation

### Modifier les couleurs de la carte

Éditez le fichier `frontend/src/components/WorldMap.js` et modifiez la fonction `getColorForValue()`.

### Ajouter de nouveaux filtres

1. Ajoutez le filtre dans `frontend/src/components/FilterPanel.js`
2. Mettez à jour la requête API dans `frontend/src/services/api.js`
3. Ajoutez l'endpoint correspondant dans `backend/routes/population.js`

## 🐛 Dépannage

### Erreur de connexion à PostgreSQL
- Vérifiez que PostgreSQL est démarré : `sudo systemctl status postgresql`
- Vérifiez vos identifiants dans `.env`
- Assurez-vous que l'utilisateur a les droits sur la base

### Erreur CORS
- Vérifiez que le backend autorise l'origine du frontend dans `server.js`

### Carte ne s'affiche pas
- Vérifiez que le fichier SVG est bien téléchargé
- Ouvrez la console du navigateur pour voir les erreurs

## 📝 Licence

Ce projet utilise le template SVG World Map de Raphaëlle Puschitz.
