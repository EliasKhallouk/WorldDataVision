# API des Indicateurs - Documentation

## Vue d'ensemble

L'API des indicateurs permet d'accéder à des données économiques, sociales, démographiques et institutionnelles pour tous les pays du monde. Les données proviennent de la Banque mondiale (Indicateurs du développement dans le monde).

**Base URL:** `http://localhost:5000/api/indicators`

---

## Indicateurs disponibles

### 📊 Économie
- **PIB par habitant (PPA)** - `NY.GDP.PCAP.PP.KD`
  - Unité: $ internationaux constants 2011
  - Période: 1990-2024
  - Pays: 199

### 👥 Social
- **Espérance de vie à la naissance** - `SP.DYN.LE00.IN`
  - Unité: années
  - Période: 1960-2023
  - Pays: 216

- **Dépenses publiques en éducation** - `SE.XPD.TOTL.GD.ZS`
  - Unité: % du PIB
  - Période: 1970-2024
  - Pays: 203

### 📈 Démographie
- **Taux de fertilité** - `SP.DYN.TFRT.IN`
  - Unité: naissances par femme
  - Période: 1960-2023
  - Pays: 216

### 🏛️ Institutionnel
- **Dette du gouvernement central** - `GC.DOD.TOTL.GD.ZS`
  - Unité: % du PIB
  - Période: 1989-2024
  - Pays: 109

- **Revenus fiscaux** - `GC.TAX.TOTL.GD.ZS`
  - Unité: % du PIB
  - Période: 1972-2024
  - Pays: 161

---

## Endpoints

### 1. Récupérer les catégories d'indicateurs

```http
GET /api/indicators/categories
```

**Réponse:**
```json
[
  {
    "id": 1,
    "code": "economy",
    "name": "Économie",
    "description": "Indicateurs économiques et financiers",
    "indicator_count": "1"
  },
  {
    "id": 2,
    "code": "social",
    "name": "Social",
    "description": "Indicateurs sociaux et de développement humain",
    "indicator_count": "2"
  }
]
```

---

### 2. Récupérer tous les indicateurs

```http
GET /api/indicators
```

**Paramètres optionnels:**
- `category` (string): Filtrer par code de catégorie (economy, social, demographic, institutional, environment)

**Exemples:**
```bash
# Tous les indicateurs
curl "http://localhost:5000/api/indicators"

# Indicateurs économiques uniquement
curl "http://localhost:5000/api/indicators?category=economy"

# Indicateurs sociaux
curl "http://localhost:5000/api/indicators?category=social"
```

**Réponse:**
```json
[
  {
    "id": 1,
    "code": "NY.GDP.PCAP.PP.KD",
    "name": "PIB par habitant (PPA, $ internationaux constants de 2011)",
    "unit": "$ internationaux constants 2011",
    "source": "Indicateurs du développement dans le monde",
    "category_code": "economy",
    "category_name": "Économie",
    "value_count": "6785",
    "country_count": "199",
    "first_year": 1990,
    "last_year": 2024
  }
]
```

---

### 3. Détails d'un indicateur

```http
GET /api/indicators/:code
```

**Exemple:**
```bash
curl "http://localhost:5000/api/indicators/SP.DYN.LE00.IN"
```

**Réponse:**
```json
{
  "id": 2,
  "code": "SP.DYN.LE00.IN",
  "name": "Espérance de vie à la naissance (années)",
  "unit": "années",
  "source": "Indicateurs du développement dans le monde",
  "category_code": "social",
  "category_name": "Social",
  "value_count": "13790",
  "country_count": "216",
  "first_year": 1960,
  "last_year": 2023
}
```

---

### 4. Valeurs d'un indicateur

```http
GET /api/indicators/:code/values
```

**Paramètres optionnels:**
- `country` (string): Code ISO du pays ou plusieurs codes séparés par des virgules
- `year` (number): Année spécifique ou plusieurs années séparées par des virgules
- `startYear` (number): Année de début
- `endYear` (number): Année de fin

**Exemples:**
```bash
# Taux de fertilité en France de 2010 à 2023
curl "http://localhost:5000/api/indicators/SP.DYN.TFRT.IN/values?country=FRA&startYear=2010&endYear=2023"

# PIB par habitant pour France, Allemagne et Espagne en 2024
curl "http://localhost:5000/api/indicators/NY.GDP.PCAP.PP.KD/values?country=FRA,DEU,ESP&year=2024"

# Espérance de vie en France pour les années 2020, 2021, 2022
curl "http://localhost:5000/api/indicators/SP.DYN.LE00.IN/values?country=FRA&year=2020,2021,2022"
```

**Réponse:**
```json
[
  {
    "year": 2010,
    "value": 2.03,
    "country_code": "FRA",
    "country_name": "France",
    "region": "Europe"
  },
  {
    "year": 2011,
    "value": 2.01,
    "country_code": "FRA",
    "country_name": "France",
    "region": "Europe"
  }
]
```

---

### 5. Comparaison entre pays

```http
GET /api/indicators/:code/comparison
```

**Paramètres:**
- `year` (number, **requis**): Année de comparaison
- `countries` (string, optionnel): Codes ISO séparés par des virgules (tous les pays par défaut)
- `limit` (number, optionnel): Nombre maximum de pays (défaut: 20)
- `sort` (string, optionnel): 'asc' ou 'desc' (défaut: 'desc')

**Exemples:**
```bash
# Top 10 des pays avec le PIB par habitant le plus élevé en 2024
curl "http://localhost:5000/api/indicators/NY.GDP.PCAP.PP.KD/comparison?year=2024&limit=10"

# Top 10 des pays avec le taux de fertilité le plus bas en 2023
curl "http://localhost:5000/api/indicators/SP.DYN.TFRT.IN/comparison?year=2023&limit=10&sort=asc"

# Comparaison entre pays européens en 2024
curl "http://localhost:5000/api/indicators/NY.GDP.PCAP.PP.KD/comparison?year=2024&countries=FRA,DEU,ESP,ITA,GBR"
```

**Réponse:**
```json
{
  "indicator": {
    "code": "NY.GDP.PCAP.PP.KD",
    "name": "PIB par habitant (PPA, $ internationaux constants de 2011)",
    "unit": "$ internationaux constants 2011"
  },
  "year": 2024,
  "data": [
    {
      "country_code": "SGP",
      "country_name": "Singapour",
      "region": "Asie",
      "value": 132569.53,
      "year": 2024
    },
    {
      "country_code": "LUX",
      "country_name": "Luxembourg",
      "region": "Europe",
      "value": 128475.28,
      "year": 2024
    }
  ]
}
```

---

### 6. Évolution temporelle

```http
GET /api/indicators/:code/evolution
```

**Paramètres:**
- `countries` (string, **requis**): Codes ISO séparés par des virgules
- `startYear` (number, optionnel): Année de début
- `endYear` (number, optionnel): Année de fin

**Exemples:**
```bash
# Évolution de l'espérance de vie en France de 1960 à 2023
curl "http://localhost:5000/api/indicators/SP.DYN.LE00.IN/evolution?countries=FRA&startYear=1960&endYear=2023"

# Comparaison de l'évolution du PIB entre France, Allemagne et Espagne depuis 2000
curl "http://localhost:5000/api/indicators/NY.GDP.PCAP.PP.KD/evolution?countries=FRA,DEU,ESP&startYear=2000"

# Évolution du taux de fertilité dans les pays scandinaves
curl "http://localhost:5000/api/indicators/SP.DYN.TFRT.IN/evolution?countries=SWE,NOR,DNK,FIN"
```

**Réponse:**
```json
{
  "indicator": {
    "code": "SP.DYN.LE00.IN",
    "name": "Espérance de vie à la naissance (années)",
    "unit": "années"
  },
  "data": [
    {
      "country_code": "FRA",
      "country_name": "France",
      "values": [
        { "year": 1960, "value": 70.29 },
        { "year": 1961, "value": 70.87 },
        { "year": 1962, "value": 71.05 }
      ]
    }
  ]
}
```

---

## Cas d'utilisation

### 1. Créer un graphique d'évolution

```javascript
// Récupérer l'évolution de l'espérance de vie pour plusieurs pays
fetch('/api/indicators/SP.DYN.LE00.IN/evolution?countries=FRA,USA,JPN&startYear=1960&endYear=2023')
  .then(res => res.json())
  .then(data => {
    // data.data contient un tableau de pays avec leurs valeurs annuelles
    // Parfait pour un graphique en ligne avec une série par pays
  });
```

### 2. Créer un classement

```javascript
// Top 20 des pays par PIB par habitant en 2024
fetch('/api/indicators/NY.GDP.PCAP.PP.KD/comparison?year=2024&limit=20')
  .then(res => res.json())
  .then(data => {
    // data.data contient le classement des pays
    // Parfait pour un tableau ou un bar chart
  });
```

### 3. Tableau de bord multi-indicateurs

```javascript
// Récupérer plusieurs indicateurs pour un pays
const country = 'FRA';
const year = 2023;

Promise.all([
  fetch(`/api/indicators/NY.GDP.PCAP.PP.KD/values?country=${country}&year=${year}`),
  fetch(`/api/indicators/SP.DYN.LE00.IN/values?country=${country}&year=${year}`),
  fetch(`/api/indicators/SP.DYN.TFRT.IN/values?country=${country}&year=${year}`)
])
.then(responses => Promise.all(responses.map(r => r.json())))
.then(([gdp, lifeExpectancy, fertility]) => {
  // Afficher tous les indicateurs pour le pays
});
```

---

## Codes des pays

Utilisez les codes ISO3 standard (3 lettres) pour identifier les pays :
- France: `FRA`
- États-Unis: `USA`
- Allemagne: `DEU`
- Royaume-Uni: `GBR`
- Espagne: `ESP`
- Italie: `ITA`
- Japon: `JPN`
- Chine: `CHN`
- etc.

Pour obtenir la liste complète des pays disponibles:
```bash
curl "http://localhost:5000/api/countries"
```

---

## Notes

- Les valeurs manquantes ne sont pas retournées dans les résultats
- Les années disponibles varient selon les indicateurs
- Toutes les dates sont en années calendaires (YYYY)
- Les valeurs numériques sont retournées en format double precision
- L'API supporte CORS pour les requêtes depuis le frontend

---

## Statistiques d'import

Données importées avec succès :
- **45 732 valeurs** au total
- **6 indicateurs** disponibles
- **216 pays maximum** par indicateur
- **Période**: 1960-2024 selon les indicateurs
