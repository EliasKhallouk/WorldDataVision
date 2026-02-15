const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const pool = require('../config/database');

/**
 * Script d'importation des indicateurs économiques, sociaux et institutionnels
 * Usage: node scripts/import_indicators.js
 */

// Configuration des fichiers CSV à importer
const INDICATOR_FILES = [
  {
    file: 'Data/Economie/PIB_habitant_PPA_internationaux_constants_2011.csv',
    indicatorCode: 'NY.GDP.PCAP.PP.KD',
    description: 'PIB par habitant (PPA)'
  },
  {
    file: 'Data/Social/Esperance_vie_naissance_total_annees.csv',
    indicatorCode: 'SP.DYN.LE00.IN',
    description: 'Espérance de vie à la naissance'
  },
  {
    file: 'Data/Social/Depenses_publiques_education_pourcent_PIB.csv',
    indicatorCode: 'SE.XPD.TOTL.GD.ZS',
    description: 'Dépenses publiques en éducation'
  },
  {
    file: 'Data/Demographie/Taux_fertilite_total_naissances_femme.csv',
    indicatorCode: 'SP.DYN.TFRT.IN',
    description: 'Taux de fertilité'
  },
  {
    file: 'Data/Institutionnel/Dette_gouvernement_central_total_pourcent_PIB.csv',
    indicatorCode: 'GC.DOD.TOTL.GD.ZS',
    description: 'Dette du gouvernement central'
  },
  {
    file: 'Data/Institutionnel/Revenus_fiscaux_pourcent_PIB.csv',
    indicatorCode: 'GC.TAX.TOTL.GD.ZS',
    description: 'Revenus fiscaux'
  }
];

// Cache pour les IDs
const countryCache = {};
const indicatorCache = {};

/**
 * Récupère l'ID d'un pays par son code ISO3
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
    return countryCache[countryCode];
  }
  
  return null;
}

/**
 * Récupère l'ID d'un indicateur par son code
 */
async function getIndicatorId(indicatorCode) {
  if (indicatorCache[indicatorCode]) {
    return indicatorCache[indicatorCode];
  }

  const result = await pool.query('SELECT id FROM indicator WHERE code = $1', [indicatorCode]);
  if (result.rows.length > 0) {
    indicatorCache[indicatorCode] = result.rows[0].id;
    return indicatorCache[indicatorCode];
  }
  
  return null;
}

/**
 * Lit un fichier CSV et retourne les données
 */
async function readCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    
    fs.createReadStream(filePath)
      .pipe(csv({ skipLines: 4 })) // Sauter les 4 premières lignes de métadonnées
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
 * Importe les données d'un fichier CSV dans la table indicator_value
 */
async function importIndicatorFile(fileConfig) {
  const filePath = path.join(__dirname, '../../', fileConfig.file);
  
  console.log(`\n📊 Importation de ${fileConfig.description}...`);
  console.log(`   Fichier: ${fileConfig.file}`);
  
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Fichier non trouvé: ${filePath}`);
    return;
  }

  try {
    // Récupérer l'ID de l'indicateur
    const indicatorId = await getIndicatorId(fileConfig.indicatorCode);
    if (!indicatorId) {
      console.error(`❌ Indicateur non trouvé: ${fileConfig.indicatorCode}`);
      return;
    }

    // Lire le CSV
    const rows = await readCSV(filePath);
    console.log(`   Lignes lues: ${rows.length}`);

    let insertedCount = 0;
    let skippedCount = 0;
    let errorCount = 0;

    // Traiter chaque ligne
    for (const row of rows) {
      const countryCode = row['Country Code'];
      if (!countryCode) continue;

      // Récupérer l'ID du pays
      const countryId = await getCountryIdByCode(countryCode);
      if (!countryId) {
        skippedCount++;
        continue;
      }

      // Parcourir toutes les colonnes qui sont des années
      for (const [key, value] of Object.entries(row)) {
        const year = parseInt(key);
        
        // Si la clé est une année valide et la valeur n'est pas vide
        if (!isNaN(year) && year >= 1960 && year <= 2030 && value && value.trim() !== '') {
          try {
            const numericValue = parseFloat(value);
            
            if (!isNaN(numericValue)) {
              // Insérer la valeur (ou la mettre à jour si elle existe déjà)
              await pool.query(
                `INSERT INTO indicator_value (country_id, indicator_id, year, value)
                 VALUES ($1, $2, $3, $4)
                 ON CONFLICT (country_id, indicator_id, year) 
                 DO UPDATE SET value = EXCLUDED.value`,
                [countryId, indicatorId, year, numericValue]
              );
              insertedCount++;
            }
          } catch (error) {
            errorCount++;
            if (errorCount < 5) {
              console.error(`   Erreur lors de l'insertion: ${error.message}`);
            }
          }
        }
      }
    }

    console.log(`   ✅ Importé: ${insertedCount} valeurs`);
    if (skippedCount > 0) {
      console.log(`   ⚠️  Ignoré: ${skippedCount} pays non trouvés`);
    }
    if (errorCount > 0) {
      console.log(`   ❌ Erreurs: ${errorCount}`);
    }

  } catch (error) {
    console.error(`❌ Erreur lors de l'importation: ${error.message}`);
  }
}

/**
 * Fonction principale
 */
async function main() {
  console.log('🚀 Début de l\'importation des indicateurs\n');
  console.log('=' .repeat(60));

  try {
    // Importer chaque fichier séquentiellement
    for (const fileConfig of INDICATOR_FILES) {
      await importIndicatorFile(fileConfig);
    }

    console.log('\n' + '='.repeat(60));
    console.log('✅ Importation terminée avec succès!');
    
    // Afficher quelques statistiques
    const stats = await pool.query(`
      SELECT 
        i.name,
        COUNT(DISTINCT iv.country_id) as nb_countries,
        MIN(iv.year) as first_year,
        MAX(iv.year) as last_year,
        COUNT(*) as nb_values
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      GROUP BY i.id, i.name
      ORDER BY i.name
    `);
    
    console.log('\n📈 Statistiques par indicateur:');
    console.log('─'.repeat(60));
    for (const stat of stats.rows) {
      console.log(`\n${stat.name}`);
      console.log(`   Pays: ${stat.nb_countries}`);
      console.log(`   Période: ${stat.first_year} - ${stat.last_year}`);
      console.log(`   Valeurs: ${stat.nb_values}`);
    }

  } catch (error) {
    console.error('\n❌ Erreur fatale:', error);
  } finally {
    await pool.end();
  }
}

// Exécution
main();
