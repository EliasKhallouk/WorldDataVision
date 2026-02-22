#!/bin/bash

# Script de setup complet pour WorldDataVision
# Ce script configure automatiquement le backend et le frontend

echo "🌍 WorldDataVision - Installation"
echo "===================================="
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "BDD/creation_bdd.sql" ]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté depuis le répertoire WorldDataVision${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Vérification des prérequis...${NC}"

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    echo "Installez Node.js depuis https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm $(npm --version)${NC}"

# Vérifier PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${RED}⚠️  PostgreSQL n'est pas installé ou n'est pas dans le PATH${NC}"
    echo "Assurez-vous que PostgreSQL est installé et en cours d'exécution"
else
    echo -e "${GREEN}✅ PostgreSQL installé${NC}"
fi

echo ""
echo -e "${BLUE}📥 Téléchargement de la carte SVG du monde...${NC}"

# Créer le dossier public du frontend s'il n'existe pas
mkdir -p frontend/public

# Télécharger la carte SVG depuis GitHub
curl -L -o frontend/public/world-map.svg \
    "https://raw.githubusercontent.com/raphaellepuschitz/SVG-World-Map/master/world.svg" \
    2>/dev/null

if [ $? -eq 0 ] && [ -f "frontend/public/world-map.svg" ]; then
    echo -e "${GREEN}✅ Carte SVG téléchargée${NC}"
else
    echo -e "${RED}⚠️  Impossible de télécharger la carte SVG${NC}"
    echo "Téléchargez-la manuellement depuis:"
    echo "https://github.com/raphaellepuschitz/SVG-World-Map"
fi

echo ""
echo -e "${BLUE}🔧 Installation du backend...${NC}"
cd backend

# Créer .env s'il n'existe pas
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé (à configurer)${NC}"
fi

# Installer les dépendances
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dépendances backend installées${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation des dépendances backend${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${BLUE}🎨 Installation du frontend...${NC}"
cd frontend

# Créer .env s'il n'existe pas
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

# Installer les dépendances
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dépendances frontend installées${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation des dépendances frontend${NC}"
    exit 1
fi

cd ..

echo ""
echo "===================================="
echo -e "${GREEN}🎉 Installation terminée avec succès!${NC}"
echo "===================================="
echo ""
echo -e "${BLUE}📝 Prochaines étapes:${NC}"
echo ""
echo "1️⃣  Configurer PostgreSQL:"
echo "   • Créez la base de données: CREATE DATABASE worlddatavision;"
echo "   • Exécutez les scripts SQL dans BDD/"
echo ""
echo "2️⃣  Configurer le backend:"
echo "   • Éditez backend/.env avec vos identifiants PostgreSQL"
echo ""
echo "3️⃣  Importer les données:"
echo "   cd backend && npm run import-data"
echo ""
echo "4️⃣  Démarrer l'application:"
echo "   • Terminal 1: cd backend && npm start"
echo "   • Terminal 2: cd frontend && npm start"
echo ""
echo "5️⃣  Accéder à l'application:"
echo "   • Frontend: http://localhost:3000"
echo "   • API: http://localhost:5000"
echo ""
echo -e "${BLUE}📖 Documentation complète: README_WEB_APP.md${NC}"
