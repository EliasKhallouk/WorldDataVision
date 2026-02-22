const pool = require('./config/database');

async function checkWHO() {
  try {
    const res = await pool.query(`
      SELECT 
        i.code,
        i.name,
        i.source,
        COUNT(DISTINCT iv.country_id) as pays
      FROM indicator i
      LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
      WHERE i.code IN ('SP.DYN.IMRT.IN', 'SP.DYN.LE00.IN')
      GROUP BY i.code, i.name, i.source
      ORDER BY i.code
    `);
    
    console.log('\n=== INDICATEURS SANTÉ ===\n');
    res.rows.forEach(r => {
      console.log(`${r.code}`);
      console.log(`  ${r.name}`);
      console.log(`  Source: ${r.source || 'N/A'}`);
      console.log(`  Pays: ${r.pays}\n`);
    });
    
    process.exit(0);
  } catch (err) {
    console.error('Erreur:', err.message);
    process.exit(1);
  }
}

checkWHO();
