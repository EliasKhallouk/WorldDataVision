const pool = require('./config/database');

async function checkWHOImport() {
  console.log('Vérification de l\'import OMS...\n');

  const indicators = ['SP.DYN.IMRT.IN', 'SP.DYN.LE00.IN', 'SH.MED.PHYS.ZS'];

  for (const code of indicators) {
    const result = await pool.query(`
      SELECT 
        i.code,
        i.name,
        i.source,
        COUNT(DISTINCT iv.country_id) as country_count
      FROM indicator i
      LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
      WHERE i.code = $1
      GROUP BY i.id, i.code, i.name, i.source
    `, [code]);

    if (result.rows.length > 0) {
      const row = result.rows[0];
      console.log(`${row.code}: ${row.country_count} pays`);
      console.log(`  Source: ${row.source || 'Non définie'}\n`);
    }
  }

  await pool.end();
}

checkWHOImport();
