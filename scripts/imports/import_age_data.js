const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const pool = require('../config/database');

/**
 * Script d'importation des données de population par tranches d'âge depuis les fichiers CSV
 * Usage: node scripts/import_age_data.js
 */

const DATA_DIR = path.join(__dirname, '../../Data/Age');

// Mapping des fichiers CSV avec leur tranche d'âge et sexe
// Format: POP.XXXX.YY.csv où XXXX = tranche d'âge, YY = sexe (FE=female, MA=male)
const AGE_MAPPINGS = {
  '0004': { label: '0-4', ageMin: 0, ageMax: 4 },
  '0509': { label: '5-9', ageMin: 5, ageMax: 9 },
  '1014': { label: '10-14', ageMin: 10, ageMax: 14 },
  '1519': { label: '15-19', ageMin: 15, ageMax: 19 },
  '2024': { label: '20-24', ageMin: 20, ageMax: 24 },
  '2529': { label: '25-29', ageMin: 25, ageMax: 29 },
  '3034': { label: '30-34', ageMin: 30, ageMax: 34 },
  '3539': { label: '35-39', ageMin: 35, ageMax: 39 },
  '4044': { label: '40-44', ageMin: 40, ageMax: 44 },
  '4549': { label: '45-49', ageMin: 45, ageMax: 49 },
  '5054': { label: '50-54', ageMin: 50, ageMax: 54 },
  '5559': { label: '55-59', ageMin: 55, ageMax: 59 },
  '6064': { label: '60-64', ageMin: 60, ageMax: 64 },
  '65UP': { label: '65+', ageMin: 65, ageMax: 120 }
};

const SEX_MAPPINGS = {
  'FE': 'female',
  'MA': 'male'
};

// Cache pour éviter les requêtes répétées
const countryCache = {};
const ageGroupCache = {};
const sexCache = {};

/**
 * Récupérer l'ID du sexe depuis la base de données
 */
async function getSexId(sexCode) {
  if (sexCache[sexCode]) {
    return sexCache[sexCode];
  }

  const result = await pool.query('SELECT id FROM sex WHERE code = $1', [sexCode]);
  if (result.rows.length > 0) {
    sexCache[sexCode] = result.rows[0].id;
  }
  return sexCache[sexCode];
}

/**
 * Récupérer l'ID du pays par son code ISO
 */
async function getCountryIdByCode(countryCode) {
  if (countryCache[countryCode]) {
    return countryCache[countryCode];
  }

  // Essayer d'abord avec iso3
  let result = await pool.query('SELECT id FROM country WHERE iso3 = $1', [countryCode]);
  if (result.rows.length > 0) {
    countryCache[countryCode] = result.rows[0].id;
    return countryCache[countryCode];
  }
  
  // Essayer avec iso2
  result = await pool.query('SELECT id FROM country WHERE iso2 = $1', [countryCode]);
  if (result.rows.length > 0) {
    countryCache[countryCode] = result.rows[0].id;
  }
  return result.rows[0]?.id;
}

/**
 * Récupérer ou créer un groupe d'âge
 */
async function getAgeGroupId(ageInfo) {
  const cacheKey = `${ageInfo.ageMin}-${ageInfo.ageMax}`;
  
  if (ageGroupCache[cacheKey]) {
    return ageGroupCache[cacheKey];
  }

  // Chercher le groupe d'âge existant
  let result = await pool.query(
    'SELECT id FROM age_group WHERE age_min = $1 AND age_max = $2',
    [ageInfo.ageMin, ageInfo.ageMax]
  );

  if (result.rows.length > 0) {
    ageGroupCache[cacheKey] = result.rows[0].id;
    return ageGroupCache[cacheKey];
  }

  // Si le groupe n'existe pas, le créer
  result = await pool.query(
    'INSERT INTO age_group (label, age_min, age_max) VALUES ($1, $2, $3) RETURNING id',
    [ageInfo.label, ageInfo.ageMin, ageInfo.ageMax]
  );

  ageGroupCache[cacheKey] = result.rows[0].id;
  console.log(`   ✅ Groupe d'âge créé: ${ageInfo.label} (${ageInfo.ageMin}-${ageInfo.ageMax})`);
  
  return ageGroupCache[cacheKey];
}

/**
 * Lire un fichier CSV
 */
async function readCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv({ skipLines: 4 })) // Sauter les 4 premières lignes (metadata)
      .on('data', (row) => {
        rows.push(row);
      })
      .on('end', () => {
        resolve(rows);
      })
      .on('error', (error) => {
        reject(error);
      });
  });
}

/**
 * Insérer un lot d'enregistrements
 */
async function insertBatch(batch) {
  if (batch.length === 0) return;

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const query = `
      INSERT INTO population_stat 
        (country_id, age_group_id, sex_id, language_id, year, population_count, source)
      VALUES 
        ($1, $2, $3, NULL, $4, $5, $6)
      ON CONFLICT (country_id, age_group_id, sex_id, language_id, year)
      DO UPDATE SET 
        population_count = EXCLUDED.population_count,
        source = EXCLUDED.source
    `;

    for (const record of batch) {
      await client.query(query, [
        record.countryId,
        record.ageGroupId,
        record.sexId,
        record.year,
        record.population,
        record.source
      ]);
    }

    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Erreur lors de l\'insertion:', error.message);
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Analyser le nom de fichier pour extraire l'âge et le sexe
 * Format: POP.XXXX.YY.csv
 */
function parseFileName(filename) {
  const match = filename.match(/POP\.([0-9A-Z]+)\.(FE|MA)\.csv/);
  if (!match) return null;

  const ageCode = match[1];
  const sexCode = match[2];

  if (!AGE_MAPPINGS[ageCode] || !SEX_MAPPINGS[sexCode]) {
    return null;
  }

  return {
    ageInfo: AGE_MAPPINGS[ageCode],
    sexCode: SEX_MAPPINGS[sexCode]
  };
}

/**
 * Importer un fichier CSV
 */
async function importCSVFile(filename) {
  const filePath = path.join(DATA_DIR, filename);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Fichier non trouvé: ${filename}`);
    return { imported: 0, skipped: 0 };
  }

  // Analyser le nom de fichier
  const fileInfo = parseFileName(filename);
  if (!fileInfo) {
    console.log(`⚠️  Format de fichier non reconnu: ${filename}`);
    return { imported: 0, skipped: 0 };
  }

  console.log(`\n📄 Importation de: ${filename}`);
  console.log(`   Tranche d'âge: ${fileInfo.ageInfo.label} (${fileInfo.ageInfo.ageMin}-${fileInfo.ageInfo.ageMax} ans)`);
  console.log(`   Sexe: ${fileInfo.sexCode}`);

  // Récupérer les IDs
  const sexId = await getSexId(fileInfo.sexCode);
  const ageGroupId = await getAgeGroupId(fileInfo.ageInfo);

  if (!sexId || !ageGroupId) {
    console.error('❌ Impossible de récupérer sex_id ou age_group_id');
    return { imported: 0, skipped: 0 };
  }

  // Lire toutes les lignes du CSV
  console.log('   📖 Lecture du fichier CSV...');
  const rows = await readCSV(filePath);
  console.log(`   📊 ${rows.length} lignes lues`);

  let importCount = 0;
  let skipCount = 0;
  const batchSize = 100;
  let batch = [];

  // Détecter le type de données (pourcentage ou valeur absolue)
  const isAbsoluteValue = rows.length > 0 && rows[0]['Indicator Code']?.includes('.IN');
  
  console.log(`   📊 Type de données: ${isAbsoluteValue ? 'Valeur absolue (nombre de personnes)' : 'Pourcentage'}`);

  for (const row of rows) {
    const countryCode = row['Country Code'];
    if (!countryCode || countryCode === 'Country Code') continue;

    // Extraire les données de population par année (colonnes qui sont des années)
    const years = Object.keys(row).filter(key => /^\d{4}$/.test(key));
    
    for (const year of years) {
      const value = row[year];
      
      // Ignorer les valeurs vides ou non numériques
      if (!value || value === '' || isNaN(parseFloat(value))) {
        continue;
      }

      const countryId = await getCountryIdByCode(countryCode);
      if (!countryId) {
        skipCount++;
        continue;
      }

      let populationValue;
      let source;
      
      if (isAbsoluteValue) {
        // Données en nombre absolu de personnes
        populationValue = Math.round(parseFloat(value));
        source = 'World Bank - Age Distribution (Absolute)';
      } else {
        // Données en pourcentage - multiplier par 10000 pour conserver la précision
        // Ex: 12.7706% devient 127706
        populationValue = Math.round(parseFloat(value) * 10000);
        source = 'World Bank - Age Distribution (Percentage * 10000)';
      }

      batch.push({
        countryId,
        ageGroupId,
        sexId,
        year: parseInt(year),
        population: populationValue,
        source: source
      });

      if (batch.length >= batchSize) {
        await insertBatch(batch);
        importCount += batch.length;
        batch = [];
        process.stdout.write(`\r   💾 Importé: ${importCount} enregistrements`);
      }
    }
  }

  // Insérer le dernier lot
  if (batch.length > 0) {
    await insertBatch(batch);
    importCount += batch.length;
  }
  
  console.log(`\n   ✅ Terminé: ${importCount} enregistrements importés`);
  if (skipCount > 0) {
    console.log(`   ⚠️  ${skipCount} enregistrements ignorés (pays non trouvé)`);
  }

  return { imported: importCount, skipped: skipCount };
}

/**
 * Fonction principale
 */
async function main() {
  console.log('🚀 Démarrage de l\'importation des données de population par âge\n');
  console.log('📁 Répertoire des données:', DATA_DIR);

  try {
    // Vérifier la connexion à la base de données
    await pool.query('SELECT 1');
    console.log('✅ Connexion à la base de données établie\n');

    // Lire tous les fichiers CSV du répertoire Age
    const files = fs.readdirSync(DATA_DIR)
      .filter(file => file.startsWith('POP.') && file.endsWith('.csv'))
      .sort();

    console.log(`📋 ${files.length} fichiers CSV trouvés\n`);

    let totalImported = 0;
    let totalSkipped = 0;

    // Importer chaque fichier CSV
    for (const file of files) {
      const result = await importCSVFile(file);
      totalImported += result.imported;
      totalSkipped += result.skipped;
    }

    console.log('\n' + '='.repeat(60));
    console.log('🎉 Importation terminée avec succès!');
    console.log('='.repeat(60));
    console.log(`📊 Total importé: ${totalImported} enregistrements`);
    if (totalSkipped > 0) {
      console.log(`⚠️  Total ignoré: ${totalSkipped} enregistrements`);
    }

    // Afficher quelques statistiques
    const stats = await pool.query(`
      SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT country_id) as unique_countries,
        COUNT(DISTINCT age_group_id) as unique_age_groups,
        MIN(year) as min_year,
        MAX(year) as max_year
      FROM population_stat
    `);
    
    console.log('\n📈 Statistiques de la base de données:');
    console.log(`   • Enregistrements totaux: ${stats.rows[0].total_records}`);
    console.log(`   • Pays uniques: ${stats.rows[0].unique_countries}`);
    console.log(`   • Tranches d'âge uniques: ${stats.rows[0].unique_age_groups}`);
    console.log(`   • Années: ${stats.rows[0].min_year} - ${stats.rows[0].max_year}`);

  } catch (error) {
    console.error('\n❌ Erreur lors de l\'importation:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Exécuter le script
if (require.main === module) {
  main();
}

module.exports = { importCSVFile, parseFileName };
