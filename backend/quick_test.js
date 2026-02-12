const pool = require('./config/database');

async function quickTest() {
  try {
    // 1. Trouver quel pays est le country_id 511
    const countryQ = await pool.query('SELECT id, iso2, iso3, name FROM country WHERE id = 511');
    console.log('\n=== PAYS ID 511 ===');
    if (countryQ.rows.length > 0) {
      const c = countryQ.rows[0];
      console.log(`${c.name} (${c.iso3} / ${c.iso2})`);
      
      // 2. Chercher ses données en 1960
      const dataQ = await pool.query(`
        SELECT s.code, ps.population_count 
        FROM population_stat ps 
        JOIN sex s ON ps.sex_id = s.id 
        WHERE ps.country_id = 511 AND ps.year = 1960
      `);
      
      console.log('\n=== DONNÉES 1960 ===');
      if (dataQ.rows.length > 0) {
        dataQ.rows.forEach(r => {
          console.log(`${r.code}: ${Number(r.population_count).toLocaleString('fr-FR')}`);
        });
        
        const totals = {};
        dataQ.rows.forEach(r => {
          totals[r.code] = Number(r.population_count);
        });
        
        if (totals.male && totals.female && totals.total) {
          const sum = totals.male + totals.female;
          console.log('\n=== VÉRIFICATION ===');
          console.log(`Male + Female = ${sum.toLocaleString('fr-FR')}`);
          console.log(`Total enregistré = ${totals.total.toLocaleString('fr-FR')}`);
          console.log(`Différence = ${Math.abs(totals.total - sum).toLocaleString('fr-FR')}`);
          
          if (Math.abs(totals.total - sum) === 0) {
            console.log('✅ COHÉRENT');
          } else {
            console.log('⚠️  INCOHÉRENT');
          }
        }
      } else {
        console.log('Aucune donnée trouvée');
      }
    } else {
      console.log('Pays non trouvé');
    }
    
    await pool.end();
  } catch (error) {
    console.error('Erreur:', error.message);
    process.exit(1);
  }
}

quickTest();
