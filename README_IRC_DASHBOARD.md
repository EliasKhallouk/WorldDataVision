# 📊 Tableau de Bord IRC - README

## 🌍 Qu'est-ce que c'est ?

Le **Tableau de Bord IRC** est une interface de visualisation interactive pour explorer **75 indicateurs de développement mondial** issus de la Banque Mondiale.

## ✨ Fonctionnalités principales

### 🎯 8 catégories thématiques
- 👥 **Démographie** (14 indicateurs) : Population, âges, fertilité, espérance de vie...
- 🌾 **Agriculture** (11 indicateurs) : Terres agricoles, rendements, production...
- 🌍 **Environnement** (3 indicateurs) : Forêts, eau, stress hydrique...
- ⚡ **Énergie** (12 indicateurs) : Production, consommation, renouvelables...
- 🏛️ **Institutionnel** (8 indicateurs) : Gouvernance, corruption, stabilité...
- 📊 **Économie** (10 indicateurs) : PIB, croissance, inflation, chômage...
- 📚 **Social** (8 indicateurs) : Éducation, santé, alphabétisation...
- 💻 **Technologie** (9 indicateurs) : Internet, mobile, innovation...

### 🔍 Recherche intelligente
- Recherche en temps réel par nom ou code d'indicateur
- Filtrage automatique selon la catégorie
- Réinitialisation rapide

### 📈 2 modes de visualisation

#### 🏆 Mode Classement
- Top 20 des pays pour chaque indicateur
- Médailles pour le podium (🥇🥈🥉)
- Barres de progression normalisées
- Valeurs formatées avec unités

#### 📊 Mode Évolution
- Graphique temporel sur 65 ans (1960-2025)
- Comparaison multi-pays (jusqu'à 5)
- Légendes interactives
- Zoom et exploration

### 💡 Informations contextuelles
Pour chaque indicateur :
- 📋 Description détaillée
- 💡 Conseils d'interprétation
- 📊 Métadonnées (unité, source, période, couverture)

## 🚀 Démarrage rapide

### Prérequis
- Node.js installé
- PostgreSQL avec les données IRC importées
- Backend et Frontend du projet WorldDataVision

### Lancer l'application

```bash
# 1. Démarrer le backend (si pas déjà lancé)
cd backend
npm start
# → http://localhost:5000

# 2. Démarrer le frontend
cd frontend
npm start
# → http://localhost:3000

# 3. Dans le navigateur
# - Ouvrir http://localhost:3000
# - Cliquer sur l'onglet "📊 IRC"
```

## 📖 Utilisation

### Navigation de base

1. **Choisir une catégorie**
   - Cliquer sur l'un des 8 boutons de catégorie
   - Les indicateurs se filtrent automatiquement

2. **Sélectionner un indicateur**
   - Utiliser la barre de recherche OU
   - Utiliser le menu déroulant
   - La carte d'information s'affiche

3. **Visualiser les données**
   - Mode 🏆 Classement : Voir le Top 20
   - Mode 📈 Évolution : Comparer des pays dans le temps

### Exemples d'analyses

#### Analyser les émissions de CO2
```
1. Catégorie : 🌍 Environnement
2. Chercher "CO2" dans la barre de recherche
3. Mode Classement → Identifier les plus gros émetteurs
4. Mode Évolution → Suivre USA, Chine, UE depuis 1960
```

#### Comparer le développement économique
```
1. Catégorie : 📊 Économie
2. Indicateur : PIB par habitant (PPA)
3. Mode Classement → Voir les pays les plus riches
4. Mode Évolution → Comparer Chine, Inde, USA, Afrique du Sud
```

#### Étudier la transition énergétique
```
1. Catégorie : ⚡ Énergie
2. Indicateur : Consommation énergies renouvelables
3. Mode Évolution → Comparer Allemagne, France, Norvège
4. Observer les différentes stratégies
```

## 📊 Données disponibles

- **75 indicateurs** de la Banque Mondiale
- **~200 pays** couverts
- **1960-2025** période (variable selon l'indicateur)
- **> 100 000 points de données** historiques

## 🎨 Design

- Dégradé violet/rose moderne
- Animations fluides au survol
- Design responsive (mobile, tablette, desktop)
- Cartes avec ombres portées
- Icônes thématiques pour chaque catégorie

## 📚 Documentation complète

Pour en savoir plus, consultez :

- **GUIDE_IRC_DASHBOARD.md** - Guide d'utilisation détaillé
- **LISTE_INDICATEURS_IRC.md** - Liste complète des 75 indicateurs
- **CAS_USAGE_IRC.md** - Exemples d'analyses et méthodologie
- **STATUT_FINAL_IRC.md** - Statut technique et tests

## 🔧 Architecture

### Frontend
```
IRCDashboard (composant principal)
├── IndicatorInfo (carte d'information)
├── IndicatorRanking (Top 20 pays)
└── IndicatorChart (graphique temporel)
```

### Backend API
```
GET /api/indicators              - Liste complète
GET /api/indicators/:code        - Détails indicateur
GET /api/indicators/:code/values - Toutes les valeurs
GET /api/indicators/:code/comparison - Classement
GET /api/indicators/:code/evolution - Évolution temporelle
```

### Base de données
```
indicator (table)
├── 75 indicateurs IRC
├── Codes, noms, descriptions
└── Métadonnées (unité, source, période)

indicator_value (table)
├── > 100 000 valeurs historiques
├── Par pays et par année
└── 1960-2025
```

## 🤝 Contribution

Le code est modulaire et bien documenté. Pour ajouter des fonctionnalités :

### Ajouter une description d'indicateur
Modifier `frontend/src/components/IndicatorInfo.js` :
```javascript
const indicatorDescriptions = {
  'CODE_INDICATEUR': {
    description: 'Description...',
    interpretation: 'Interprétation...'
  }
};
```

### Personnaliser les couleurs
Modifier `frontend/src/components/IRCDashboard.css` :
```css
/* Dégradé principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 🐛 Dépannage

### Le tableau de bord ne s'affiche pas
```bash
# Vérifier que le backend fonctionne
curl http://localhost:5000/api/indicators

# Vérifier la console du navigateur (F12)
# Rechercher les erreurs
```

### Les indicateurs sont vides
```bash
# Vérifier que les données sont importées
psql -U elias -d worlddata -c "SELECT COUNT(*) FROM indicator;"
# → Devrait retourner 75

# Si 0, importer les données IRC
cd backend/scripts
node import_irc_data.js
```

### Erreur CORS
Le backend doit avoir configuré CORS pour autoriser http://localhost:3000

## 📈 Améliorations futures

- [ ] Export CSV des données
- [ ] Export PNG des graphiques
- [ ] Favoris d'indicateurs
- [ ] Dashboards personnalisés
- [ ] Comparaison multi-indicateurs
- [ ] Corrélations et scatter plots
- [ ] Prédictions basées sur les tendances

## 📧 Support

Consultez la documentation complète dans les fichiers :
- GUIDE_IRC_DASHBOARD.md
- LISTE_INDICATEURS_IRC.md
- CAS_USAGE_IRC.md

## 📄 Licence

Projet WorldDataVision - 2026

---

**Bon à savoir** :
- Les données proviennent de l'API de la Banque Mondiale
- Mise à jour : 2026-02-19
- Source : https://data.worldbank.org

**Bonne exploration ! 🌍📊**
