# 📊 Guide du Tableau de Bord IRC

## Vue d'ensemble

Le nouveau **Tableau de Bord IRC** intègre maintenant **75 indicateurs** de développement issus de la Banque Mondiale, couvrant les domaines suivants :

## 🎯 Catégories d'indicateurs

### 👥 Démographie (15 indicateurs)
- Population totale, par tranche d'âge (0-14, 15-64, 65+)
- Âge médian, ratios de dépendance
- Taux de natalité, mortalité, fertilité
- Espérance de vie
- Croissance démographique, migration
- Urbanisation

### 🌾 Agriculture (8 indicateurs)
- Surfaces agricoles et arables
- Rendement céréalier
- Indices de production (alimentaire, cultures, élevage)
- Importations/exportations alimentaires

### 🌍 Environnement (6 indicateurs)
- Stress hydrique, eau renouvelable
- Surface forestière
- Émissions de CO2 (2 méthodes de calcul)
- Superficie terrestre

### ⚡ Énergie (12 indicateurs)
- Production et consommation électrique
- Énergies renouvelables vs fossiles
- Nucléaire, hydroélectrique
- Importations énergétiques
- Rentes pétrolières, gaz, charbon
- Accès à l'électricité

### 🏛️ Gouvernance (6 indicateurs)
- Contrôle de la corruption
- Efficacité gouvernementale
- Stabilité politique
- État de droit
- Qualité de la régulation
- Voix et responsabilité

### 💰 Finances publiques (5 indicateurs)
- Dette publique
- Dette extérieure, service de la dette
- Revenus fiscaux
- Réserves en mois d'importations

### 📊 Économie (7 indicateurs)
- PIB par habitant (PPA)
- Croissance du PIB
- Inflation
- Chômage
- Balance courante
- Investissements directs étrangers (IDE)
- Dépenses militaires

### 📚 Éducation (3 indicateurs)
- Dépenses en éducation
- Scolarisation tertiaire
- Taux d'alphabétisation adulte

### 🔬 Innovation (5 indicateurs)
- Dépenses en R&D
- Chercheurs par million d'habitants
- Demandes de brevets
- Publications scientifiques
- Exportations high-tech

### 💻 Technologies (4 indicateurs)
- Utilisateurs Internet
- Abonnements mobiles
- Haut débit fixe
- Serveurs Internet sécurisés

### 🏥 Santé (4 indicateurs)
- Dépenses de santé
- Médecins et lits d'hôpital pour 1000 habitants
- Mortalité infantile

## 🎨 Fonctionnalités du Tableau de Bord

### Navigation par catégories
- **11 boutons thématiques** avec icônes distinctives
- Compteur d'indicateurs par catégorie
- Design en grille responsive

### Recherche et filtrage
- **Barre de recherche** pour trouver rapidement un indicateur
- Recherche par nom ou code d'indicateur
- Bouton de réinitialisation rapide

### Modes de visualisation

#### 🏆 Mode Classement
- Top 20 des pays pour l'indicateur sélectionné
- Médailles pour le podium (🥇🥈🥉)
- Barres de progression normalisées
- Valeurs formatées avec unités

#### 📈 Mode Évolution
- Graphique temporel multi-pays
- Sélection de 5 pays maximum
- Légendes verticales avec couleurs distinctes
- Zoom et interaction sur le graphique

### Carte d'information
Pour chaque indicateur, affichage de :
- 📋 Description détaillée
- 💡 Conseils d'interprétation
- Métadonnées : unité, source, période, couverture

### Statistiques en temps réel
- Nombre d'indicateurs disponibles
- Nombre d'indicateurs affichés (après filtrage)
- Catégorie active

## 🚀 Comment utiliser le tableau de bord

### 1. Accéder au tableau de bord IRC
- Cliquez sur l'onglet **"📊 IRC"** dans le header
- Vous arrivez sur la catégorie "Démographie" par défaut

### 2. Explorer une catégorie
- Cliquez sur un bouton de catégorie (ex: 🌍 Environnement)
- Les indicateurs se filtrent automatiquement
- Le compteur indique le nombre d'indicateurs dans cette catégorie

### 3. Rechercher un indicateur spécifique
- Utilisez la barre de recherche
- Tapez le nom ou le code (ex: "CO2" ou "EN.ATM")
- Les résultats se filtrent en temps réel

### 4. Sélectionner un indicateur
- Utilisez le menu déroulant "Indicateur sélectionné"
- L'indicateur s'affiche immédiatement
- La carte d'information apparaît en haut

### 5. Choisir un mode de visualisation

#### Pour voir le classement :
1. Cliquez sur **"🏆 Classement"**
2. Consultez le Top 20 des pays
3. Les barres sont normalisées pour faciliter la comparaison

#### Pour voir l'évolution temporelle :
1. Cliquez sur **"📈 Évolution"**
2. Sélectionnez jusqu'à 5 pays
3. Le graphique affiche l'évolution sur toute la période disponible

## 📱 Design responsive
- Adapté aux écrans desktop, tablettes et mobiles
- Grilles auto-adaptatives
- Navigation intuitive sur tous les appareils

## 🎯 Exemples d'analyses possibles

### Analyse environnementale
1. Catégorie **🌍 Environnement**
2. Indicateur : **Émissions de CO2 par habitant**
3. Mode Classement → Identifier les plus gros émetteurs
4. Mode Évolution → Suivre la trajectoire de décarbonation

### Analyse démographique
1. Catégorie **👥 Démographie**
2. Indicateur : **Espérance de vie**
3. Comparer les pays développés vs en développement
4. Observer l'amélioration au fil du temps

### Analyse économique
1. Catégorie **📊 Économie**
2. Indicateur : **PIB par habitant (PPA)**
3. Classement des économies mondiales
4. Convergence ou divergence des pays

### Analyse technologique
1. Catégorie **💻 Technologies**
2. Indicateur : **Utilisateurs Internet**
3. Fracture numérique entre pays
4. Vitesse d'adoption des technologies

## 🔧 Architecture technique

### Frontend
- **React** avec hooks (useState, useEffect)
- **Axios** pour les appels API
- **Canvas API** pour les graphiques
- **CSS Grid & Flexbox** pour le layout

### Backend
- **Express.js** API REST
- **PostgreSQL** base de données
- **6 endpoints** pour les indicateurs :
  - `GET /api/indicators` - Liste tous les indicateurs
  - `GET /api/indicators/:code` - Détails d'un indicateur
  - `GET /api/indicators/:code/values` - Toutes les valeurs
  - `GET /api/indicators/:code/comparison` - Comparaison pays
  - `GET /api/indicators/:code/evolution` - Évolution temporelle
  - `GET /api/indicators/categories` - Liste des catégories

### Base de données
- **Table `indicator`** : 75 indicateurs IRC
- **Table `indicator_value`** : > 100 000 valeurs historiques
- **Table `indicator_category`** : 11 catégories thématiques
- **Période** : 1960-2025 (selon les indicateurs)
- **Couverture** : ~200 pays/territoires

## 📊 Données disponibles

### Couverture géographique
- **~200 pays** et territoires
- Agrégats régionaux exclus (AFE, WLD, etc.)
- Correspondance ISO3 pour la géolocalisation

### Couverture temporelle
- **1960-2025** (selon les indicateurs)
- Certains indicateurs démarrent plus tard (ex: Internet)
- Mise à jour annuelle

### Qualité des données
- **Source** : Banque Mondiale API v2
- **Dernière mise à jour** : 2026-02-19
- Données manquantes gérées (null values)
- Normalisation des valeurs pour comparaisons

## 🎨 Palette de couleurs par catégorie

Les catégories utilisent des couleurs cohérentes :
- **Démographie** : Bleu
- **Agriculture** : Vert
- **Environnement** : Vert foncé
- **Énergie** : Jaune/Orange
- **Gouvernance** : Violet
- **Finances** : Or
- **Économie** : Rouge
- **Éducation** : Bleu clair
- **Innovation** : Rose
- **Technologies** : Cyan
- **Santé** : Rouge clair

## 🚀 Améliorations futures possibles

1. **Export de données**
   - Export CSV/Excel des classements
   - Export PNG des graphiques
   - Rapport PDF personnalisable

2. **Comparaisons avancées**
   - Multi-indicateurs sur un même graphique
   - Corrélations entre indicateurs
   - Scatter plots (ex: PIB vs CO2)

3. **Alertes et tendances**
   - Détection de tendances (hausse/baisse)
   - Alertes sur changements significatifs
   - Prédictions basées sur les tendances

4. **Personnalisation**
   - Favoris d'indicateurs
   - Dashboards personnalisés
   - Partage de visualisations

5. **Analyses statistiques**
   - Moyenne mobile
   - Taux de croissance annuel
   - Écart-type et distribution

## 📖 Références

- **Banque Mondiale** : https://data.worldbank.org
- **API Documentation** : https://datahelpdesk.worldbank.org/knowledgebase/topics/125589
- **Méthodologie** : Voir fichier `Data/IRC/metadata.json`

---

**Créé par** : WorldDataVision Team  
**Date** : 2026-02-19  
**Version** : 1.0
