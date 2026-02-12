const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const pool = require('../config/database');

/**
 * Script d'importation des données de population depuis les fichiers CSV
 * Version 2 - Amélioration de la gestion asynchrone
 * Usage: node scripts/import_population_data_v2.js
 */

const DATA_DIR = path.join(__dirname, '../../Data');

// Mapping des fichiers CSV avec leur catégorie de sexe
const CSV_FILES = [
  {
    file: 'API_SP.POP.TOTL_DS2_en_csv_v2_40826.csv',
    sex: 'total',
    description: 'Population totale'
  },
  {
    file: 'API_SP.POP.TOTL.FE.IN_DS2_en_csv_v2_1037.csv',
    sex: 'female',
    description: 'Population féminine'
  },
  {
    file: 'API_SP.POP.TOTL.MA.IN_DS2_en_csv_v2_4601.csv',
    sex: 'male',
    description: 'Population masculine'
  }
];

// Cache pour éviter les requêtes répétées
const countryCache = {};

async function getSexId(sexCode) {
  const result = await pool.query('SELECT id FROM sex WHERE code = $1', [sexCode]);
  return result.rows[0]?.id;
}

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

async function getAllAgeGroupId() {
  // Utiliser le groupe d'âge "ALL" (0-120 ans) car les CSV n'ont pas de détail par âge
  const result = await pool.query("SELECT id FROM age_group WHERE label = 'ALL'");
  return result.rows[0]?.id;
}

async function readCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv({ skipLines: 4 }))
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

async function importCSVFile(csvFile) {
  const filePath = path.join(DATA_DIR, csvFile.file);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Fichier non trouvé: ${csvFile.file}`);
    return;
  }

  console.log(`\n📄 Importation de: ${csvFile.description}`);
  console.log(`   Fichier: ${csvFile.file}`);

  const sexId = await getSexId(csvFile.sex);
  const ageGroupId = await getAllAgeGroupId();

  if (!sexId || !ageGroupId) {
    console.error('❌ Impossible de récupérer sex_id ou age_group_id');
    return;
  }
  
  console.log(`   ℹ️  Utilisation du groupe d'âge ALL (id=${ageGroupId})`);

  // Lire toutes les lignes du CSV
  console.log('   📖 Lecture du fichier CSV...');
  const rows = await readCSV(filePath);
  console.log(`   📊 ${rows.length} lignes lues`);

  let importCount = 0;
  let skipCount = 0;
  const batchSize = 100;
  let batch = [];

  for (const row of rows) {
    const countryCode = row['Country Code'];
    if (!countryCode || countryCode === 'Country Code') continue;

    // Extraire les données de population par année
    const years = Object.keys(row).filter(key => /^\d{4}$/.test(key));
    
    for (const year of years) {
      const population = row[year];
      
      // Ignorer les valeurs vides ou non numériques
      if (!population || population === '' || isNaN(parseFloat(population))) {
        continue;
      }

      const countryId = await getCountryIdByCode(countryCode);
      if (!countryId) {
        skipCount++;
        continue;
      }

      batch.push({
        countryId,
        ageGroupId,
        sexId,
        year: parseInt(year),
        population: Math.round(parseFloat(population)),
        source: 'World Bank'
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
}

async function main() {
  console.log('🚀 Démarrage de l\'importation des données de population\n');
  console.log('📁 Répertoire des données:', DATA_DIR);

  try {
    // Vérifier la connexion à la base de données
    await pool.query('SELECT 1');
    console.log('✅ Connexion à la base de données établie\n');

    // Importer chaque fichier CSV
    for (const csvFile of CSV_FILES) {
      await importCSVFile(csvFile);
    }

    console.log('\n🎉 Importation terminée avec succès!');
    
    // Afficher quelques statistiques
    const stats = await pool.query('SELECT COUNT(*) as count FROM population_stat');
    console.log(`\n📊 Total d'enregistrements dans la base: ${stats.rows[0].count}`);

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

module.exports = { importCSVFile };
