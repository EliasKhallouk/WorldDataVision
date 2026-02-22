const pool = require('./config/database');

async function testPyramid() {
  try {
    console.log('🧪 Test de la pyramide des âges pour Aruba (ABW) en 2020\n');
    
    const iso3 = 'ABW';
    const year = 2020;
    
    // Récupérer la population totale
    console.log('1️⃣ Population totale:');
    const totalPopResult = await pool.query(`
      SELECT 
        s.code as sex,
        ps.population_count as total,
        ag.label as age_group
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1 
        AND ps.year = $2
        AND ag.label = 'ALL'
        AND s.code IN ('male', 'female')
    `, [iso3, year]);
    
    console.table(totalPopResult.rows);
    
    const totalPopulation = {};
    totalPopResult.rows.forEach(row => {
      totalPopulation[row.sex] = parseInt(row.total);
    });
    
    // Récupérer les données par tranche d'âge
    console.log('\n2️⃣ Données par tranche d\'âge:');
    const result = await pool.query(`
      SELECT 
        ag.label as age_group,
        ag.age_min,
        ag.age_max,
        s.code as sex,
        ps.population_count,
        ps.source
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1 
        AND ps.year = $2
        AND s.code IN ('male', 'female')
        AND ag.label != 'ALL'
      ORDER BY ag.age_min, s.code
      LIMIT 10
    `, [iso3, year]);
    
    console.table(result.rows);
    
    // Calculer les populations
    console.log('\n3️⃣ Calculs des populations:');
    result.rows.forEach(row => {
      let population;
      if (row.source?.includes('Absolute')) {
        population = parseInt(row.population_count);
        console.log(`  ${row.age_group} (${row.sex}): ${population} personnes (valeur absolue)`);
      } else if (row.source?.includes('Percentage')) {
        const percentage = parseInt(row.population_count) / 10000 / 100;
        const sexTotal = totalPopulation[row.sex] || 0;
        population = Math.round(sexTotal * percentage);
        console.log(`  ${row.age_group} (${row.sex}): ${percentage.toFixed(4)}% de ${sexTotal} = ${population} personnes`);
      }
    });
    
    console.log('\n✅ Test terminé');
    
  } catch (error) {
    console.error('❌ Erreur:', error);
  } finally {
    await pool.end();
  }
}

testPyramid();
