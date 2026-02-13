const pool = require('./config/database');

async function testTrend() {
  try {
    console.log('🧪 Test de la tendance de la population\n');
    
    const iso3 = 'FRA';
    const sexCode = 'total';
    
    console.log(`📊 Test pour ${iso3} (sexe: ${sexCode})\n`);
    
    // 1. Ancienne requête (avec SUM - BUG)
    console.log('❌ Ancienne requête (avec SUM - additionne tout):');
    const oldResult = await pool.query(`
      SELECT 
        ps.year,
        SUM(ps.population_count) as total_population
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      WHERE c.iso3 = $1 AND s.code = $2
      GROUP BY ps.year
      ORDER BY ps.year
      LIMIT 5
    `, [iso3, sexCode]);
    
    console.table(oldResult.rows);
    
    // 2. Nouvelle requête (avec filtre ALL)
    console.log('\n✅ Nouvelle requête (avec filtre ALL):');
    const newResult = await pool.query(`
      SELECT 
        ps.year,
        ps.population_count as total_population
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1 
        AND s.code = $2
        AND ag.label = 'ALL'
      ORDER BY ps.year
      LIMIT 5
    `, [iso3, sexCode]);
    
    console.table(newResult.rows);
    
    // 3. Vérifier les dernières années
    console.log('\n📈 Dernières années (2015-2020):');
    const recentResult = await pool.query(`
      SELECT 
        ps.year,
        ps.population_count as total_population
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1 
        AND s.code = $2
        AND ag.label = 'ALL'
        AND ps.year BETWEEN 2015 AND 2020
      ORDER BY ps.year
    `, [iso3, sexCode]);
    
    console.table(recentResult.rows);
    
    console.log('\n✅ Test terminé');
    
  } catch (error) {
    console.error('❌ Erreur:', error);
  } finally {
    await pool.end();
  }
}

testTrend();
