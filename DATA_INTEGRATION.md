# Guide d'intégration des données

## Structure de la base de données

Votre base PostgreSQL contient les tables suivantes :

### Tables principales

1. **country** - Informations sur les pays
   - `id`, `iso2`, `iso3`, `name`, `region`, `capital`

2. **population_stat** - Données de population
   - `country_id`, `age_group_id`, `sex_id`, `year`, `population_count`

3. **age_group** - Groupes d'âge
4. **sex** - Catégories de sexe (male, female, total)
5. **year_table** - Années disponibles

## Importation des données CSV

### Option 1 : Script automatique

Le script `backend/scripts/import_population_data.js` importe automatiquement vos fichiers CSV :

```bash
cd backend
npm run import-data
```

### Option 2 : Import manuel

```javascript
const pool = require('./config/database');

async function importCustomData() {
  // Exemple : insérer une donnée de population
  await pool.query(`
    INSERT INTO population_stat 
      (country_id, age_group_id, sex_id, year, population_count, source)
    VALUES 
      ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (country_id, age_group_id, sex_id, language_id, year)
    DO UPDATE SET population_count = EXCLUDED.population_count
  `, [countryId, ageGroupId, sexId, year, population, 'Source']);
}
```

## Adaptation des données

### Vos fichiers CSV actuels

Vous avez 3 fichiers CSV de la Banque Mondiale :
- `API_SP.POP.TOTL_DS2_en_csv_v2_40826.csv` - Population totale
- `API_SP.POP.TOTL.FE.IN_DS2_en_csv_v2_1037.csv` - Population féminine
- `API_SP.POP.TOTL.MA.IN_DS2_en_csv_v2_4601.csv` - Population masculine

### Format attendu

Le script d'import attend des CSV avec :
- Colonne `Country Code` (code ISO du pays)
- Colonnes nommées avec l'année (ex: `1960`, `1961`, etc.)
- Valeurs de population dans chaque cellule

### Personnalisation du script

Pour adapter l'import à d'autres sources de données :

1. Modifiez `backend/scripts/import_population_data.js`
2. Ajustez la logique de parsing selon votre format CSV
3. Mappez les colonnes vers les champs de la base

```javascript
// Exemple de personnalisation
const customMapping = {
  countryColumn: 'Country Code',
  yearColumns: ['1960', '1970', '1980'],
  // ... votre logique
};
```

## Ajouter de nouvelles sources de données

### 1. Créer une nouvelle table (optionnel)

```sql
CREATE TABLE custom_data (
  id SERIAL PRIMARY KEY,
  country_id INT REFERENCES country(id),
  year SMALLINT,
  custom_value NUMERIC,
  -- vos colonnes
);
```

### 2. Créer un nouvel endpoint API

Dans `backend/routes/` :

```javascript
router.get('/custom-data', async (req, res) => {
  const result = await pool.query(`
    SELECT c.iso3, cd.custom_value
    FROM custom_data cd
    JOIN country c ON cd.country_id = c.id
    WHERE cd.year = $1
  `, [year]);
  
  res.json({ data: result.rows });
});
```

### 3. Mettre à jour le frontend

Dans `frontend/src/services/api.js` :

```javascript
export const getCustomData = async (params) => {
  const response = await api.get('/custom-data', { params });
  return response.data;
};
```

## Vérification des données

### Tester la connexion

```bash
cd backend
node -e "require('./config/database').query('SELECT COUNT(*) FROM population_stat').then(r => console.log(r.rows))"
```

### Vérifier les données importées

```sql
-- Nombre total d'enregistrements
SELECT COUNT(*) FROM population_stat;

-- Pays avec le plus de données
SELECT c.name, COUNT(*) as data_points
FROM population_stat ps
JOIN country c ON ps.country_id = c.id
GROUP BY c.name
ORDER BY data_points DESC
LIMIT 10;

-- Années disponibles
SELECT DISTINCT year FROM population_stat ORDER BY year;
```

## Mise à jour des données

Pour actualiser les données régulièrement :

1. Téléchargez les nouveaux fichiers CSV
2. Placez-les dans le dossier `Data/`
3. Exécutez le script d'import
4. Les données existantes seront mises à jour (ON CONFLICT DO UPDATE)

## Performance

### Index recommandés

Les index sont déjà créés dans `creation_bdd.sql` :

```sql
CREATE INDEX idx_population_country ON population_stat(country_id);
CREATE INDEX idx_population_filters ON population_stat(age_group_id, sex_id, language_id, year);
```

### Optimisation des requêtes

Pour de gros volumes de données, utilisez :
- `EXPLAIN ANALYZE` pour analyser les requêtes
- Pagination pour limiter les résultats
- Cache côté serveur (Redis) pour les données fréquemment consultées
