const pool = require('./config/database');

async function testAgeGroupFilter() {
  try {
    console.log('🧪 Test du filtre par groupe d\'âge\n');
    
    // 1. Récupérer les groupes d'âge disponibles
    console.log('1️⃣ Groupes d\'âge disponibles:');
    const ageGroupsResult = await pool.query(`
      SELECT id, label, age_min, age_max
      FROM age_group
      WHERE label != 'ALL'
      ORDER BY age_min
      LIMIT 5
    `);
    console.table(ageGroupsResult.rows);
    
    if (ageGroupsResult.rows.length === 0) {
      console.log('❌ Aucun groupe d\'âge trouvé');
      return;
    }
    
    const testAgeGroup = ageGroupsResult.rows[0];
    console.log(`\n✅ Test avec le groupe d'âge: ${testAgeGroup.label} (ID: ${testAgeGroup.id})\n`);
    
    // 2. Tester la requête avec le filtre d'âge
    console.log('2️⃣ Population par pays pour la tranche d\'âge', testAgeGroup.label, ':');
    const summaryResult = await pool.query(`
      WITH age_data AS (
        SELECT 
          c.id as country_id,
          c.iso3,
          c.name,
          c.region,
          s.code as sex_code,
          ps.population_count,
          ps.source,
          (SELECT population_count 
           FROM population_stat ps2 
           JOIN age_group ag2 ON ps2.age_group_id = ag2.id 
           WHERE ps2.country_id = c.id 
             AND ps2.year = 2020
             AND ps2.sex_id = s.id 
             AND ag2.label = 'ALL'
           LIMIT 1) as total_pop
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        WHERE ps.year = 2020
          AND ag.id = $1
          AND s.code IN ('male', 'female')
      )
      SELECT 
        iso3,
        name,
        region,
        SUM(
          CASE 
            WHEN source LIKE '%Absolute%' THEN population_count::bigint
            WHEN source LIKE '%Percentage%' THEN 
              ROUND((population_count::numeric / 10000 / 100) * total_pop::numeric)::bigint
            ELSE population_count::bigint
          END
        ) as total_population
      FROM age_data
      GROUP BY iso3, name, region
      ORDER BY total_population DESC
      LIMIT 10
    `, [testAgeGroup.id]);
    
    console.table(summaryResult.rows);
    
    // 3. Comparer avec ALL
    console.log('\n3️⃣ Comparaison avec ALL (population totale):');
    const allResult = await pool.query(`
      SELECT 
        c.iso3,
        c.name,
        COALESCE(SUM(ps.population_count), 0)::bigint as total_population
      FROM country c
      LEFT JOIN population_stat ps ON c.id = ps.country_id
      LEFT JOIN sex s ON ps.sex_id = s.id
      LEFT JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE ps.year = 2020
        AND s.code = 'total'
        AND ag.label = 'ALL'
      GROUP BY c.id, c.iso3, c.name
      ORDER BY total_population DESC
      LIMIT 5
    `);
    
    console.table(allResult.rows);
    
    console.log('\n✅ Test terminé avec succès!');
    
  } catch (error) {
    console.error('❌ Erreur:', error);
  } finally {
    await pool.end();
  }
}

testAgeGroupFilter();
