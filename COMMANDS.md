# Aide-mémoire des commandes

## 🚀 Installation initiale

```bash
# Rendre le script exécutable
chmod +x setup.sh

# Lancer l'installation automatique
./setup.sh
```

## 🗄️ Configuration PostgreSQL

```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql

# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE worlddatavision;

# Se connecter à la base
\c worlddatavision

# Exécuter les scripts SQL
\i /home/elias/PROJECT/WorldDataVision/BDD/creation_bdd.sql
\i /home/elias/PROJECT/WorldDataVision/BDD/Parser_country_language.sql

# Quitter psql
\q
```

## 🔧 Backend

```bash
# Aller dans le dossier backend
cd backend

# Installer les dépendances
npm install

# Copier le fichier de configuration
cp .env.example .env

# Éditer la configuration
nano .env

# Importer les données CSV
npm run import-data

# Démarrer le serveur (mode production)
npm start

# Démarrer en mode développement (avec auto-reload)
npm run dev
```

## 🎨 Frontend

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Copier le fichier de configuration
cp .env.example .env

# Démarrer l'application
npm start

# Créer un build de production
npm run build
```

## 🔍 Tests et vérification

```bash
# Tester la connexion à la base de données
cd backend
node -e "require('./config/database').query('SELECT NOW()').then(r => console.log('OK:', r.rows[0]))"

# Vérifier le nombre de données importées
psql -U postgres -d worlddatavision -c "SELECT COUNT(*) FROM population_stat;"

# Tester l'API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/countries
```

## 📊 Requêtes SQL utiles

```sql
-- Compter les pays
SELECT COUNT(*) FROM country;

-- Compter les données de population
SELECT COUNT(*) FROM population_stat;

-- Voir les 10 pays les plus peuplés (année 2020)
SELECT c.name, SUM(ps.population_count) as total
FROM population_stat ps
JOIN country c ON ps.country_id = c.id
JOIN sex s ON ps.sex_id = s.id
WHERE ps.year = 2020 AND s.code = 'total'
GROUP BY c.name
ORDER BY total DESC
LIMIT 10;

-- Voir les années disponibles
SELECT DISTINCT year FROM population_stat ORDER BY year;

-- Vérifier les données d'un pays spécifique
SELECT * FROM population_stat ps
JOIN country c ON ps.country_id = c.id
WHERE c.iso3 = 'FRA'
ORDER BY ps.year DESC
LIMIT 10;
```

## 🐛 Dépannage

### PostgreSQL ne démarre pas
```bash
# Vérifier le statut
sudo systemctl status postgresql

# Redémarrer PostgreSQL
sudo systemctl restart postgresql

# Voir les logs
sudo journalctl -u postgresql -n 50
```

### Port déjà utilisé

```bash
# Trouver le processus utilisant le port 5000
sudo lsof -i :5000

# Tuer le processus (remplacer PID par le numéro du processus)
kill -9 PID

# Ou changer le port dans backend/.env
echo "PORT=5001" >> backend/.env
```

### Erreur de connexion à la base de données

```bash
# Vérifier que PostgreSQL écoute
psql -U postgres -c "SHOW port;"

# Tester la connexion
psql -U postgres -d worlddatavision -c "SELECT 1;"

# Vérifier les identifiants dans .env
cat backend/.env
```

### Carte SVG ne s'affiche pas

```bash
# Vérifier que le fichier existe
ls -lh frontend/public/world-map.svg

# Re-télécharger si nécessaire
curl -L -o frontend/public/world-map.svg \
  "https://raw.githubusercontent.com/raphaellepuschitz/SVG-World-Map/master/world.svg"
```

## 🔄 Mise à jour des données

```bash
# Re-importer les données (écrase les anciennes)
cd backend
npm run import-data

# Importer uniquement certains fichiers
# Modifier backend/scripts/import_population_data.js
```

## 📦 Déploiement

### Build de production

```bash
# Backend (rien à builder, mais configurer les variables d'environnement)
cd backend
export NODE_ENV=production
export DB_HOST=votre_serveur
export DB_PASSWORD=votre_mdp

# Frontend
cd frontend
npm run build
# Les fichiers sont dans frontend/build/
```

### Servir avec Nginx

```nginx
# Configuration Nginx
server {
    listen 80;
    server_name votre-domaine.com;

    # Frontend
    location / {
        root /chemin/vers/frontend/build;
        try_files $uri /index.html;
    }

    # API Backend
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔐 Sécurité

### Créer un utilisateur PostgreSQL dédié

```sql
-- Se connecter en tant que postgres
psql -U postgres

-- Créer un utilisateur
CREATE USER worlddata_user WITH PASSWORD 'votre_mot_de_passe_fort';

-- Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE worlddatavision TO worlddata_user;

-- Se connecter à la base
\c worlddatavision

-- Donner les permissions sur les tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO worlddata_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO worlddata_user;
```

### Variables d'environnement en production

```bash
# Ne JAMAIS commiter le fichier .env
echo ".env" >> .gitignore

# Utiliser des secrets managers (ex: AWS Secrets Manager, Azure Key Vault)
# Ou des variables d'environnement système
export DB_PASSWORD="mot_de_passe_secret"
```

## 📝 Git

```bash
# Initialiser un dépôt Git
git init

# Ajouter les fichiers
git add .

# Premier commit
git commit -m "Initial commit: WorldDataVision app"

# Ajouter un remote
git remote add origin https://github.com/votre-compte/worlddatavision.git

# Push
git push -u origin main
```

## 🎯 Développement

### Ajouter une nouvelle dépendance

```bash
# Backend
cd backend
npm install nom-du-package

# Frontend
cd frontend
npm install nom-du-package
```

### Lancer les tests

```bash
# Backend
cd backend
npm test

# Frontend
cd frontend
npm test
```

## 📊 Monitoring

```bash
# Voir les logs du backend en temps réel
cd backend
npm start | tee backend.log

# Surveiller l'utilisation de PostgreSQL
psql -U postgres -d worlddatavision -c "
  SELECT 
    datname, 
    pg_size_pretty(pg_database_size(datname)) as size
  FROM pg_database
  WHERE datname = 'worlddatavision';
"

# Voir les connexions actives
psql -U postgres -d worlddatavision -c "
  SELECT * FROM pg_stat_activity 
  WHERE datname = 'worlddatavision';
"
```

## 🔧 Maintenance

```bash
# Nettoyer les node_modules
cd backend && rm -rf node_modules && npm install
cd frontend && rm -rf node_modules && npm install

# Mettre à jour les dépendances
npm update

# Vérifier les vulnérabilités
npm audit
npm audit fix

# Optimiser PostgreSQL
psql -U postgres -d worlddatavision -c "VACUUM ANALYZE;"
```

## 📞 Aide

- Documentation complète : `README_WEB_APP.md`
- Guide rapide : `QUICKSTART.md`
- Structure du projet : `PROJECT_STRUCTURE.md`
- Personnalisation : `CUSTOMIZATION.md`
- Intégration des données : `DATA_INTEGRATION.md`
