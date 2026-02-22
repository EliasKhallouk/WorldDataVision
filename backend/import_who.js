const pool = require('../backend/config/database');
const axios = require('axios');

const WHO_BASE = "https://ghoapi.azureedge.net/api";

// Mapping IRC → OMS
const whoMappings = {
  'SP.DYN.IMRT.IN': {
    whoCode: 'MDG_0000000001',
    name: 'Mortalité infantile'
  },
  'SP.DYN.LE00.IN': {
    whoCode: 'WHOSIS_000001',
    name: 'Espérance de vie'
  },
  'SH.MED.PHYS.ZS': {
    whoCode: 'HRH_26',
    name: 'Médecins par 1000'
  }
};

async function importWHOData() {
  console.log('='.repeat(80));
  console.log('IMPORT OMS - INDICATEURS SANTÉ');
  console.log('='.repeat(80));
  console.log();

  // Récupérer les pays
  const countriesResult = await pool.query(
    "SELECT id, iso3, name FROM country WHERE iso3 IS NOT NULL AND iso3 != ''"
  );
  const countries = {};
  countriesResult.rows.forEach(row => {
    countries[row.iso3] = { id: row.id, name: row.name };
  });

  console.log(`✓ ${countriesResult.rows.length} pays dans la BDD\n`);

  const stats = {
    total: 0,
    new: 0,
    averaged: 0
  };

  for (const [ircCode, mapping] of Object.entries(whoMappings)) {
    console.log('='.repeat(60));
    console.log(`📊 ${ircCode}: ${mapping.name}`);
    console.log(`   Code OMS: ${mapping.whoCode}`);
    console.log('='.repeat(60));

    // Couverture actuelle
    const currentCov = await pool.query(`
      SELECT COUNT(DISTINCT country_id) as count
      FROM indicator_value
      WHERE indicator_id = (SELECT id FROM indicator WHERE code = $1)
    `, [ircCode]);

    console.log(`  Couverture actuelle: ${currentCov.rows[0].count} pays`);

    // Télécharger données OMS
    try {
      console.log(`  Téléchargement depuis OMS...`);
      const response = await axios.get(`${WHO_BASE}/${mapping.whoCode}`, {
        timeout: 60000
      });

      const values = response.data.value || [];
      console.log(`  ✓ ${values.length} observations OMS`);

      if (values.length === 0) {
        console.log(`  ⚠️  Aucune donnée\n`);
        continue;
      }

      // Obtenir ID indicateur
      const indResult = await pool.query(
        "SELECT id FROM indicator WHERE code = $1",
        [ircCode]
      );

      if (indResult.rows.length === 0) {
        console.log(`  ✗ Indicateur non trouvé\n`);
        continue;
      }

      const indicatorId = indResult.rows[0].id;

      // Regrouper par pays-année
      const dataByCountryYear = {};
      
      for (const value of values) {
        const iso3 = value.SpatialDim;
        const year = value.TimeDim;
        const numericValue = value.NumericValue;

        if (iso3 && year && numericValue !== null && countries[iso3]) {
          try {
            const y = parseInt(year);
            const key = `${iso3}_${y}`;
            if (!dataByCountryYear[key]) {
              dataByCountryYear[key] = [];
            }
            dataByCountryYear[key].push(parseFloat(numericValue));
          } catch (err) {
            // Skip invalid data
          }
        }
      }

      console.log(`  ✓ ${Object.keys(dataByCountryYear).length} paires pays-année`);

      // Moyenner et importer
      let newValues = 0;
      let averagedValues = 0;

      for (const [key, vals] of Object.entries(dataByCountryYear)) {
        const [iso3, yearStr] = key.split('_');
        const year = parseInt(yearStr);
        const value = vals.reduce((a, b) => a + b, 0) / vals.length;
        const countryId = countries[iso3].id;

        // Vérifier si existe
        const existing = await pool.query(`
          SELECT id, value, source
          FROM indicator_value
          WHERE indicator_id = $1 AND country_id = $2 AND year = $3
        `, [indicatorId, countryId, year]);

        if (existing.rows.length > 0) {
          // Moyenner
          const ex = existing.rows[0];
          const exSource = ex.source || '';

          if (!exSource.includes('OMS') && !exSource.includes('WHO')) {
            const newValue = (ex.value + value) / 2;
            const newSource = exSource ? `${exSource} + OMS (WHO GHO)` : 'OMS (WHO GHO)';

            await pool.query(`
              UPDATE indicator_value
              SET value = $1, source = $2
              WHERE id = $3
            `, [newValue, newSource, ex.id]);

            averagedValues++;
          }
        } else {
          // Nouvelle valeur
          await pool.query(`
            INSERT INTO indicator_value (indicator_id, country_id, year, value, source)
            VALUES ($1, $2, $3, $4, $5)
          `, [indicatorId, countryId, year, value, 'OMS (WHO Global Health Observatory)']);

          newValues++;
        }
      }

      // Nouvelle couverture
      const newCov = await pool.query(`
        SELECT COUNT(DISTINCT country_id) as count
        FROM indicator_value
        WHERE indicator_id = $1
      `, [indicatorId]);

      const gain = newCov.rows[0].count - currentCov.rows[0].count;

      console.log(`\n  ✅ Nouvelles: ${newValues} | Moyennées: ${averagedValues}`);
      console.log(`  📈 Couverture: ${currentCov.rows[0].count} → ${newCov.rows[0].count} (+${gain})\n`);

      stats.total += newValues + averagedValues;
      stats.new += newValues;
      stats.averaged += averagedValues;

    } catch (error) {
      console.log(`  ✗ Erreur: ${error.message}\n`);
    }

    // Pause pour rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Mettre à jour les sources
  console.log('='.repeat(80));
  console.log('MISE À JOUR DES SOURCES');
  console.log('='.repeat(80));
  console.log();

  for (const ircCode of Object.keys(whoMappings)) {
    const result = await pool.query(
      "SELECT source FROM indicator WHERE code = $1",
      [ircCode]
    );

    if (result.rows.length > 0) {
      const currentSource = result.rows[0].source || '';

      if (!currentSource.includes('OMS') && !currentSource.includes('WHO')) {
        const newSource = currentSource ? `${currentSource} + OMS (WHO GHO)` : 'OMS (WHO Global Health Observatory)';

        await pool.query(
          "UPDATE indicator SET source = $1 WHERE code = $2",
          [newSource, ircCode]
        );

        console.log(`✓ ${ircCode}: Source mise à jour`);
      }
    }
  }

  console.log(`\n${'='.repeat(80)}`);
  console.log(`📊 TOTAL: ${stats.total} valeurs (${stats.new} nouvelles + ${stats.averaged} moyennées)`);
  console.log('='.repeat(80));

  await pool.end();
  console.log('\n✅ Import OMS terminé');
}

importWHOData().catch(error => {
  console.error('Erreur:', error);
  process.exit(1);
});
