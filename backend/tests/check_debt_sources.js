const pool = require('./config/database');

async function checkDebtSources() {
  try {
    // Get current debt indicators info
    const result = await pool.query(`
      SELECT 
        i.code,
        i.name,
        i.source,
        COUNT(DISTINCT iv.country_id) as country_count,
        MAX(iv.year) as latest_year,
        MIN(iv.year) as earliest_year
      FROM indicator i
      LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
      WHERE i.code IN ('DT.DOD.DECT.GN.ZS', 'DT.TDS.DECT.EX.ZS')
      GROUP BY i.id, i.code, i.name, i.source
      ORDER BY i.code
    `);

    console.log('========================================');
    console.log('INDICATEURS DETTE EXTERNE - ÉTAT ACTUEL');
    console.log('========================================\n');
    
    result.rows.forEach(row => {
      console.log(`Code: ${row.code}`);
      console.log(`Nom: ${row.name}`);
      console.log(`Source actuelle: ${row.source || 'Non définie'}`);
      console.log(`Couverture: ${row.country_count} pays`);
      console.log(`Période: ${row.earliest_year} - ${row.latest_year}`);
      console.log('');
    });

    // Check sample values
    const sampleResult = await pool.query(`
      SELECT 
        i.code,
        c.name,
        c.iso3_code,
        iv.year,
        iv.value,
        iv.source as value_source
      FROM indicator_value iv
      JOIN indicator i ON iv.indicator_id = i.id
      JOIN country c ON iv.country_id = c.id
      WHERE i.code = 'DT.DOD.DECT.GN.ZS'
        AND c.iso3_code IN ('USA', 'FRA', 'CHN', 'BRA')
        AND iv.year >= 2020
      ORDER BY c.name, iv.year DESC
    `);

    console.log('========================================');
    console.log('ÉCHANTILLON DE VALEURS (2020+)');
    console.log('========================================\n');
    
    sampleResult.rows.forEach(row => {
      console.log(`${row.iso3_code} ${row.year}: ${row.value.toFixed(2)}% - Source: ${row.value_source || 'N/A'}`);
    });

    await pool.end();
    
  } catch (error) {
    console.error('Erreur:', error);
    process.exit(1);
  }
}

checkDebtSources();
