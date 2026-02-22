# WorldDataVision - Guide de démarrage rapide

## Installation rapide

```bash
# Rendre le script exécutable
chmod +x setup.sh

# Exécuter le script d'installation
./setup.sh
```

## Configuration de la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE worlddatavision;

# Se connecter à la base
\c worlddatavision

# Exécuter les scripts SQL
\i BDD/creation_bdd.sql
\i BDD/Parser_country_language.sql
```

## Configuration du backend

Éditez `backend/.env`:

```env
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=worlddatavision
DB_USER=votre_utilisateur_postgres
DB_PASSWORD=votre_mot_de_passe
NODE_ENV=development
```

## Importer les données de population

```bash
cd backend
npm run import-data
```

## Démarrer l'application

### Terminal 1 - Backend
```bash
cd backend
npm start
```

### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

## Accès

- **Frontend**: http://localhost:3000
- **API**: http://localhost:5000
- **Documentation API**: http://localhost:5000/api

## Problèmes courants

### PostgreSQL n'est pas accessible
```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql

# Vérifier le statut
sudo systemctl status postgresql
```

### Port déjà utilisé
Modifiez le `PORT` dans `backend/.env` ou `frontend/.env`

### Carte SVG ne s'affiche pas
Téléchargez manuellement depuis:
https://github.com/raphaellepuschitz/SVG-World-Map

Et placez le fichier dans `frontend/public/world-map.svg`
