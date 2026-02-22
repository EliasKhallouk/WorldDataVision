#!/usr/bin/env node

/**
 * Import des données d'électricité depuis Our World in Data
 * Source: Ember (2026); Energy Institute - Statistical Review of World Energy (2025)
 * Conversion: TWh → kWh (×10^9)
 */

const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const pool = require('../config/database');

const ELECTRICITY_FILE = path.join(__dirname, '../..', 'Data', 'electricity-generation.csv');

/**
 * Importe les données d'électricité dans la base de données
 */
async function importElectricityData() {
  console.log('='.repeat(80));
  console.log('⚡ IMPORTATION DES DONNÉES D\'ÉLECTRICITÉ (Our World in Data)');
  console.log('='.repeat(80));
  console.log();

  try {
    // Vérifier que l'indicateur existe
    const indResult = await pool.query(
      'SELECT id FROM indicator WHERE code = $1',
      ['EG.ELC.PROD.KH']
    );

    if (indResult.rows.length === 0) {
      console.error('❌ Indicateur EG.ELC.PROD.KH non trouvé dans la base');
      process.exit(1);
    }

    const indicatorId = indResult.rows[0].id;
    console.log(`✅ Indicateur EG.ELC.PROD.KH trouvé (ID: ${indicatorId})`);
    console.log();

    // Lire et traiter le CSV
    let rowCount = 0;
    let insertCount = 0;
    let skipCount = 0;
    const batch = [];
    const BATCH_SIZE = 500;

    const stream = fs.createReadStream(ELECTRICITY_FILE)
      .pipe(csv({
        mapHeaders: ({ header }) => header.trim(),
        mapValues: ({ value }) => {
          const num = parseFloat(value);
          return isNaN(num) ? value : num;
        }
      }))
      .on('data', (row) => {
        rowCount++;

        // Filtrer les agrégats régionaux (garder seulement les pays ISO3 valides)
        const code = row.Code ? row.Code.trim() : null;
        if (!code || code.length !== 3 || !/^[A-Z]+$/.test(code)) {
          skipCount++;
          return;
        }

        const year = row.Year ? parseInt(row.Year, 10) : null;
        const valueTWh = row['Total electricity'] ? parseFloat(row['Total electricity']) : null;

        if (!year || valueTWh === null || isNaN(valueTWh)) {
          skipCount++;
          return;
        }

        // Convertir TWh en kWh (×10^9)
        const valueKWh = valueTWh * 1e9;

        batch.push({
          countryCode: code,
          year: year,
          value: valueKWh
        });

        // Traiter le batch quand il atteint la taille limite
        if (batch.length >= BATCH_SIZE) {
          stream.pause();
          processBatch(batch, indicatorId).then(count => {
            insertCount += count;
            batch.length = 0;
            stream.resume();
          }).catch(err => {
            console.error(`❌ Erreur batch:`, err.message);
            batch.length = 0;
            stream.resume();
          });
        }
      })
      .on('error', (err) => {
        console.error(`❌ Erreur lecture CSV:`, err.message);
        process.exit(1);
      })
      .on('end', async () => {
        // Traiter le dernier batch
        if (batch.length > 0) {
          insertCount += await processBatch(batch, indicatorId);
        }

        console.log();
        console.log('='.repeat(80));
        console.log('📊 RÉSUMÉ DE L\'IMPORTATION');
        console.log('='.repeat(80));
        console.log(`✅ Valeurs insérées: ${insertCount}`);
        console.log(`⏭️  Lignes filtrées: ${skipCount}`);
        console.log(`📝 Lignes traitées: ${rowCount}`);
        console.log();

        await pool.end();
        process.exit(insertCount > 0 ? 0 : 1);
      });
  } catch (err) {
    console.error('❌ Erreur fatale:', err.message);
    await pool.end();
    process.exit(1);
  }
}

/**
 * Traite un batch de lignes
 */
async function processBatch(batchData, indicatorId) {
  let successCount = 0;

  for (const { countryCode, year, value } of batchData) {
    try {
      // Chercher le pays par son code ISO3
      const countryResult = await pool.query(
        'SELECT id FROM country WHERE iso3 = $1',
        [countryCode]
      );

      if (countryResult.rows.length === 0) {
        continue; // Pays non trouvé, ignorer
      }

      const countryId = countryResult.rows[0].id;

      // Insérer ou ignorer si conflit
      const result = await pool.query(
        `INSERT INTO indicator_value (country_id, indicator_id, year, value)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT (country_id, indicator_id, year) DO NOTHING
         RETURNING id`,
        [countryId, indicatorId, year, value]
      );

      if (result.rows.length > 0) {
        successCount++;
      }
    } catch (err) {
      console.error(`⚠️  Erreur insertion (${countryCode}, ${year}):`, err.message);
    }
  }

  return successCount;
}

// Lancer l'import
importElectricityData().catch(err => {
  console.error('❌ Erreur non gérée:', err);
  process.exit(1);
});
