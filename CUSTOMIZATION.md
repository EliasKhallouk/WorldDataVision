# Guide de personnalisation

## 🎨 Personnaliser les couleurs de la carte

### Modifier l'échelle de couleurs

Éditez `frontend/src/utils/helpers.js` dans la fonction `getColorForValue()` :

```javascript
export const getColorForValue = (value, min, max) => {
  if (value === null || value === undefined || value === 0) {
    return '#e0e0e0'; // Gris pour pas de données
  }

  const normalized = (value - min) / (max - min);
  
  // 🎨 PERSONNALISEZ ICI : Modifiez les couleurs
  const colors = [
    { threshold: 0.0, color: '#fff7fb' },  // Rose très clair
    { threshold: 0.2, color: '#ece7f2' },  // Violet clair
    { threshold: 0.4, color: '#d0d1e6' },  // Bleu lavande
    { threshold: 0.6, color: '#a6bddb' },  // Bleu clair
    { threshold: 0.8, color: '#74a9cf' },  // Bleu moyen
    { threshold: 1.0, color: '#0570b0' }   // Bleu foncé
  ];

  // ... reste du code
};
```

### Exemples de palettes

#### Palette verte (environnement)
```javascript
const colors = [
  { threshold: 0.0, color: '#f7fcf5' },
  { threshold: 0.2, color: '#e5f5e0' },
  { threshold: 0.4, color: '#c7e9c0' },
  { threshold: 0.6, color: '#a1d99b' },
  { threshold: 0.8, color: '#74c476' },
  { threshold: 1.0, color: '#238b45' }
];
```

#### Palette orange/rouge (chaleur)
```javascript
const colors = [
  { threshold: 0.0, color: '#fff7ec' },
  { threshold: 0.2, color: '#fee8c8' },
  { threshold: 0.4, color: '#fdd49e' },
  { threshold: 0.6, color: '#fc8d59' },
  { threshold: 0.8, color: '#e34a33' },
  { threshold: 1.0, color: '#b30000' }
];
```

## 🗺️ Personnaliser la carte SVG

### Changer la projection

Si vous souhaitez utiliser une autre carte SVG :

1. Téléchargez une carte SVG (ex: projection de Mercator, projection polaire)
2. Placez-la dans `frontend/public/`
3. Modifiez `WorldMap.js` :

```javascript
useEffect(() => {
  fetch('/votre-carte.svg')  // 👈 Changez le nom ici
    .then(res => res.text())
    .then(svg => setSvgContent(svg))
    .catch(err => console.error('Erreur:', err));
}, []);
```

### Assurer la compatibilité

Votre fichier SVG doit :
- Avoir des éléments `<path>` ou `<g>` avec des attributs `id`
- Les `id` doivent correspondre aux codes ISO3 des pays (ex: `FRA`, `USA`, `CHN`)

## 📊 Ajouter de nouveaux graphiques

### Exemple : Ajouter un graphique en camembert

1. Installez un nouveau composant de graphique :
```bash
cd frontend
npm install recharts
```

2. Créez un nouveau composant `PieChartComponent.js` :

```javascript
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const PieChartComponent = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default PieChartComponent;
```

3. Utilisez-le dans `App.js` ou `CountryDetails.js`

## 🔍 Ajouter de nouveaux filtres

### Exemple : Ajouter un filtre par région

1. Modifiez `FilterPanel.js` :

```javascript
import React, { useState, useEffect } from 'react';
import { getRegions } from '../services/api';

const FilterPanel = ({ 
  years, 
  sexCategories,
  selectedYear, 
  selectedSex,
  selectedRegion, // 👈 Nouveau
  onYearChange,
  onSexChange,
  onRegionChange  // 👈 Nouveau
}) => {
  const [regions, setRegions] = useState([]);

  useEffect(() => {
    // Charger les régions
    getRegions().then(data => {
      setRegions(['Toutes', ...data.data]);
    });
  }, []);

  return (
    <div className="filter-panel">
      {/* Filtres existants */}
      
      {/* 👇 Nouveau filtre région */}
      <div className="filter-group">
        <label htmlFor="region-select">Région</label>
        <select 
          id="region-select"
          value={selectedRegion}
          onChange={(e) => onRegionChange(e.target.value)}
          className="filter-select"
        >
          {regions.map(region => (
            <option key={region} value={region}>{region}</option>
          ))}
        </select>
      </div>
    </div>
  );
};
```

2. Mettez à jour `App.js` :

```javascript
const [selectedRegion, setSelectedRegion] = useState('Toutes');

// Dans loadPopulationData()
const loadPopulationData = async () => {
  // ... code existant
  
  let data = await getPopulationSummary({
    year: selectedYear,
    sex: selectedSex
  });

  // Filtrer par région si nécessaire
  if (selectedRegion !== 'Toutes') {
    data.data = data.data.filter(d => d.region === selectedRegion);
  }

  setPopulationData(data.data);
};
```

## 🎭 Personnaliser l'interface

### Modifier le thème de couleurs

Éditez `frontend/src/App.css` :

```css
/* Changer la couleur du header */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Remplacez par votre gradient */
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* Changer la couleur primaire */
.filter-select:focus {
  border-color: #4a90e2; /* Bleu par défaut */
  border-color: #f5576c; /* Votre couleur */
}
```

### Modifier les polices

Dans `frontend/public/index.html`, ajoutez Google Fonts :

```html
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
</head>
```

Puis dans `App.css` :

```css
body {
  font-family: 'Poppins', sans-serif;
}
```

## 📱 Responsive design

### Ajuster les breakpoints

Dans les fichiers CSS, modifiez les media queries :

```css
/* Tablet */
@media (max-width: 1024px) {
  /* Vos styles pour tablettes */
}

/* Mobile */
@media (max-width: 768px) {
  /* Vos styles pour mobiles */
}
```

## 🌐 Internationalisation

### Ajouter le français

1. Installez react-i18next :
```bash
cd frontend
npm install react-i18next i18next
```

2. Créez `src/i18n.js` :

```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: {
          "title": "WorldDataVision",
          "population": "Population"
        }
      },
      fr: {
        translation: {
          "title": "Visualisation des Données Mondiales",
          "population": "Population"
        }
      }
    },
    lng: "fr",
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

3. Utilisez-le dans vos composants :

```javascript
import { useTranslation } from 'react-i18next';

function App() {
  const { t } = useTranslation();
  
  return <h1>{t('title')}</h1>;
}
```

## 📈 Ajouter des indicateurs personnalisés

### Exemple : Densité de population

1. Ajoutez un endpoint dans `backend/routes/population.js` :

```javascript
router.get('/density/:iso3', async (req, res) => {
  try {
    const { iso3 } = req.params;
    const { year } = req.query;

    // Supposons que vous avez une table avec les surfaces des pays
    const result = await pool.query(`
      SELECT 
        c.name,
        SUM(ps.population_count) as population,
        cs.area_km2,
        SUM(ps.population_count) / cs.area_km2 as density
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN country_surface cs ON cs.country_id = c.id
      WHERE c.iso3 = $1 AND ps.year = $2
      GROUP BY c.name, cs.area_km2
    `, [iso3.toUpperCase(), year]);

    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error) {
    res.status(500).json({ error: 'Erreur' });
  }
});
```

2. Affichez-le dans `CountryDetails.js`

## 🔌 Ajouter des sources de données externes

### Exemple : Intégrer l'API World Bank

```javascript
// Dans services/api.js
const WORLD_BANK_API = 'https://api.worldbank.org/v2';

export const getWorldBankIndicator = async (countryCode, indicator) => {
  const url = `${WORLD_BANK_API}/country/${countryCode}/indicator/${indicator}?format=json`;
  const response = await axios.get(url);
  return response.data;
};
```

## 💡 Conseils de performance

### Lazy loading des graphiques

```javascript
import React, { lazy, Suspense } from 'react';

const CountryDetails = lazy(() => import('./components/CountryDetails'));

function App() {
  return (
    <Suspense fallback={<div>Chargement...</div>}>
      {selectedCountry && <CountryDetails />}
    </Suspense>
  );
}
```

### Mémoïsation

```javascript
import React, { useMemo } from 'react';

const stats = useMemo(() => calculateStats(populationData), [populationData]);
```

## 🎯 Exemples de cas d'usage

### 1. Carte choroplèthe avec plusieurs indicateurs
- Ajoutez des endpoints pour PIB, IDH, espérance de vie
- Créez un sélecteur d'indicateur dans FilterPanel
- Adaptez getColorForValue() pour chaque indicateur

### 2. Animation temporelle
- Ajoutez un bouton "Play" qui change automatiquement l'année
- Utilisez setInterval() pour créer l'animation
- Affichez la transition sur la carte

### 3. Comparaison de pays
- Ajoutez la possibilité de sélectionner plusieurs pays
- Créez un graphique comparatif
- Affichez les tendances côte à côte
