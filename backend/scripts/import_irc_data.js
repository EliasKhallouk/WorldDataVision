#!/usr/bin/env node

/**
 * Étape 3 : Importation des données IRC dans indicator_value
 * Lit tous les CSV de Data/IRC/ et les insère dans la base de données
 */

const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const pool = require('../config/database');

const IRC_DATA_DIR = path.join(__dirname, '../..', 'Data', 'IRC');

// Cache pour les IDs
const countryCache = {};
const indicatorCache = {};
let validYears = new Set(); // Sera chargé au démarrage

// Liste des codes régionaux/agrégats à ignorer (ne correspondent pas à des pays réels)
const SKIP_COUNTRY_CODES = new Set([
  'AFE', 'AFW', 'EAS', 'ECS', 'LCN', 'MEA', 'MNA', 'NAC', 'SAS', 'SSF', 'SSA',
  'WLD', 'HIC', 'MIC', 'LIC', 'EUU', 'FCS', 'IBD', 'IBT', 'IDA', 'IBRD', 'IDB'
]);

/**
 * Récupère l'ID d'un pays par son code ISO3
 */
async function getCountryId(countryCode) {
  if (!countryCode) return null;
  
  if (countryCode in countryCache) {
    return countryCache[countryCode];
  }
  
  try {
    const result = await pool.query(
      'SELECT id FROM country WHERE iso3 = $1',
      [countryCode]
    );
    
    if (result.rows.length > 0) {
      countryCache[countryCode] = result.rows[0].id;
      return result.rows[0].id;
    }
  } catch (err) {
    console.error(`❌ Erreur lors de la recherche du pays ${countryCode}:`, err.message);
  }
  
  return null;
}

/**
 * Récupère l'ID d'un indicateur par son code
 */
async function getIndicatorId(indicatorCode) {
  if (!indicatorCode) return null;
  
  if (indicatorCode in indicatorCache) {
    return indicatorCache[indicatorCode];
  }
  
  try {
    const result = await pool.query(
      'SELECT id FROM indicator WHERE code = $1',
      [indicatorCode]
    );
    
    if (result.rows.length > 0) {
      indicatorCache[indicatorCode] = result.rows[0].id;
      return result.rows[0].id;
    }
  } catch (err) {
    console.error(`❌ Erreur lors de la recherche de l'indicateur ${indicatorCode}:`, err.message);
  }
  
  return null;
}

/**
 * Charge toutes les années depuis year_table (une seule fois au démarrage)
 */
async function loadValidYears() {
  try {
    const result = await pool.query('SELECT value FROM year_table ORDER BY value');
    validYears = new Set(result.rows.map(r => r.value));
    console.log(`✅ ${validYears.size} années chargées en cache`);
  } catch (err) {
    console.error('❌ Erreur lors du chargement des années:', err.message);
    throw err;
  }
}

/**
 * Vérifie qu'une année est dans le cache (appel O(1), pas de requête DB)
 */
function isValidYear(year) {
  if (!year || isNaN(year)) return false;
  const yearNum = parseInt(year, 10);
  return validYears.has(yearNum);
}

/**
 * Insère une valeur d'indicateur
 */
async function insertIndicatorValue(countryId, indicatorId, year, value) {
  if (!countryId || !indicatorId || !year || value === null) {
    return null;
  }
  
  try {
    const result = await pool.query(
      `INSERT INTO indicator_value (country_id, indicator_id, year, value)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (country_id, indicator_id, year) DO NOTHING
       RETURNING id`,
      [countryId, indicatorId, year, value]
    );
    
    return result.rows.length > 0 ? result.rows[0].id : null;
  } catch (err) {
    console.error(`❌ Erreur insertion (country=${countryId}, indicator=${indicatorId}, year=${year}):`, err.message);
    return null;
  }
}

/**
 * Traite un fichier CSV IRC (avec batch processing)
 */
async function processIRCFile(filePath, indicatorCode, indicatorName) {
  return new Promise((resolve) => {
    let rowCount = 0;
    let insertCount = 0;
    let skipCount = 0;
    const batch = [];
    const BATCH_SIZE = 100;
    
    console.log(`📥 Traitement de ${indicatorName} (${indicatorCode})...`);
    
    const stream = fs.createReadStream(filePath)
      .pipe(csv({
        mapHeaders: ({ header }) => header.trim(),
        mapValues: ({ value }) => {
          const num = parseFloat(value);
          return isNaN(num) ? value : num;
        }
      }))
      .on('data', (row) => {
        rowCount++;
        
        // Extraire les informations clés
        const countryCode = row.country_code ? row.country_code.trim() : null;
        const year = row.year ? parseInt(row.year, 10) : null;
        const value = row.value !== undefined && row.value !== '' ? parseFloat(row.value) : null;
        
        // Ignorer les agrégats régionaux/non-pays
        if (!countryCode || SKIP_COUNTRY_CODES.has(countryCode)) {
          skipCount++;
          return;
        }
        
        if (!year || value === null || isNaN(value)) {
          skipCount++;
          return;
        }
        
        batch.push({ countryCode, year, value });
        
        // Traiter le batch quand il atteint la taille limite
        if (batch.length >= BATCH_SIZE) {
          stream.pause();
          processBatch(batch, indicatorCode).then(count => {
            insertCount += count;
            batch.length = 0;
            stream.resume();
          }).catch(err => {
            console.error(`❌ Erreur lors du traitement du batch:`, err.message);
            batch.length = 0;
            stream.resume();
          });
        }
      })
      .on('error', (err) => {
        console.error(`❌ Erreur de lecture du fichier ${filePath}:`, err.message);
        resolve({ rowCount: 0, insertCount: 0, skipCount: 0 });
      })
      .on('end', async () => {
        // Traiter le dernier batch
        if (batch.length > 0) {
          insertCount += await processBatch(batch, indicatorCode);
        }
        console.log(`   ✅ ${insertCount} insertions, ⏭️ ${skipCount} ignorées (sur ${rowCount} lignes)`);
        resolve({ rowCount, insertCount, skipCount });
      });
  });
}

/**
 * Traite un batch de lignes
 */
async function processBatch(batchData, indicatorCode) {
  let successCount = 0;
  let failCount = 0;
  
  // Pré-charger l'ID indicateur une fois par batch
  const indicId = await getIndicatorId(indicatorCode);
  
  if (!indicId) {
    console.warn(`   ⚠️ Indicateur non trouvé: ${indicatorCode}`);
    return 0;
  }
  
  for (const { countryCode, year, value } of batchData) {
    // Vérifier l'année d'abord (rapide, en cache)
    if (!isValidYear(year)) {
      failCount++;
      continue;
    }
    
    // Puis chercher le pays
    const countryId = await getCountryId(countryCode);
    
    if (!countryId) {
      failCount++;
      continue;
    }
    
    const result = await insertIndicatorValue(countryId, indicId, year, value);
    if (result) {
      successCount++;
    } else {
      failCount++;
    }
  }
  
  return successCount;
}

/**
 * Fonction principale
 */
async function main() {
  console.log('='.repeat(80));
  console.log('📝 ÉTAPE 3 : IMPORTATION DES DONNÉES IRC');
  console.log('='.repeat(80));
  console.log();
  
  // Charger les années valides d'abord
  console.log('📚 Chargement des années...');
  await loadValidYears();
  console.log();
  
  // Lister les fichiers CSV
  let csvFiles = [];
  try {
    const files = fs.readdirSync(IRC_DATA_DIR);
    csvFiles = files
      .filter(f => f.endsWith('.csv') && f !== 'metadata.csv')
      .sort();
  } catch (err) {
    console.error(`❌ Erreur lors de la lecture du dossier ${IRC_DATA_DIR}:`, err.message);
    process.exit(1);
  }
  
  console.log(`📊 Fichiers CSV trouvés: ${csvFiles.length}`);
  console.log();
  
  // Charger les métadonnées pour mapper code → name
  const metadataFile = path.join(IRC_DATA_DIR, 'metadata.json');
  let metadata = {};
  let fileToCodeMap = {}; // nom_fichier → code_indicateur
  let codeToName = {};
  try {
    if (fs.existsSync(metadataFile)) {
      metadata = JSON.parse(fs.readFileSync(metadataFile, 'utf8'));
      
      // Créer le mapping nom_fichier → code
      if (metadata.indicators) {
        metadata.indicators.forEach(ind => {
          const fileName = ind.file.replace('.csv', '');
          fileToCodeMap[fileName] = ind.code;
          codeToName[ind.code] = ind.name;
        });
      }
    }
  } catch (err) {
    console.error(`❌ Impossible de charger metadata.json:`, err.message);
    process.exit(1);
  }
  
  if (Object.keys(fileToCodeMap).length === 0) {
    console.error('❌ Aucun mapping indicateur trouvé dans metadata.json');
    process.exit(1);
  }
  
  // Traiter chaque fichier
  let totalInserted = 0;
  let totalSkipped = 0;
  const failedFiles = [];
  
  for (const csvFile of csvFiles) {
    const filePath = path.join(IRC_DATA_DIR, csvFile);
    const fileName = csvFile.replace('.csv', '');
    
    // Chercher le code indicateur via le mapping
    const indicatorCode = fileToCodeMap[fileName];
    if (!indicatorCode) {
      console.error(`❌ Aucun code trouvé pour ${csvFile}`);
      failedFiles.push(csvFile);
      continue;
    }
    
    const indicatorName = codeToName[indicatorCode] || indicatorCode;
    
    try {
      const result = await processIRCFile(filePath, indicatorCode, indicatorName);
      totalInserted += result.insertCount;
      totalSkipped += result.skipCount;
    } catch (err) {
      console.error(`❌ Erreur lors du traitement de ${csvFile}:`, err.message);
      failedFiles.push(csvFile);
    }
  }
  
  // Résumé
  console.log();
  console.log('='.repeat(80));
  console.log('📊 RÉSUMÉ DE L\'IMPORTATION');
  console.log('='.repeat(80));
  console.log(`✅ Valeurs insérées: ${totalInserted}`);
  console.log(`⏭️ Valeurs ignorées: ${totalSkipped}`);
  console.log(`📁 Fichiers traités: ${csvFiles.length - failedFiles.length}/${csvFiles.length}`);
  
  if (failedFiles.length > 0) {
    console.log(`\n❌ Fichiers échoués:`);
    failedFiles.forEach(f => console.log(`   - ${f}`));
  }
  
  console.log('='.repeat(80));
  
  // Fermer la connexion
  await pool.end();
  
  process.exit(failedFiles.length > 0 ? 1 : 0);
}

// Lancer
main().catch(err => {
  console.error('❌ Erreur fatale:', err);
  process.exit(1);
});
