const pool = require('./config/database');

async function testLanguageFilter() {
  console.log('=== Test du filtre par langue ===\n');
  
  try {
    // Test 1: Liste des langues les plus parlées
    console.log('1. Top 10 des langues par nombre de pays:');
    const topLanguages = await pool.query(`
      SELECT l.id, l.name, COUNT(DISTINCT cl.country_id) as country_count
      FROM language l
      LEFT JOIN country_language cl ON l.id = cl.language_id
      GROUP BY l.id, l.name
      HAVING COUNT(DISTINCT cl.country_id) > 0
      ORDER BY country_count DESC
      LIMIT 10
    `);
    topLanguages.rows.forEach(lang => {
      console.log(`   ${lang.name}: ${lang.country_count} pays`);
    });
    
    // Test 2: Pays francophones (fr = id 311 selon notre requête précédente)
    console.log('\n2. Pays francophones (langue fr):');
    const frenchCountries = await pool.query(`
      SELECT c.iso3, c.name
      FROM country c
      INNER JOIN country_language cl ON c.id = cl.country_id
      WHERE cl.language_id = 311
      ORDER BY c.name
    `);
    console.log(`   Nombre: ${frenchCountries.rows.length}`);
    console.log('   Exemples:', frenchCountries.rows.slice(0, 5).map(c => c.name).join(', '));
    
    // Test 3: Pays anglophones (en = id 453)
    console.log('\n3. Pays anglophones (langue en):');
    const englishCountries = await pool.query(`
      SELECT c.iso3, c.name
      FROM country c
      INNER JOIN country_language cl ON c.id = cl.country_id
      WHERE cl.language_id = 453
      ORDER BY c.name
    `);
    console.log(`   Nombre: ${englishCountries.rows.length}`);
    console.log('   Exemples:', englishCountries.rows.slice(0, 5).map(c => c.name).join(', '));
    
    // Test 4: Population totale des pays francophones en 2024
    console.log('\n4. Population des pays francophones (2024):');
    const frenchPopulation = await pool.query(`
      SELECT 
        c.iso3,
        c.name,
        COALESCE(SUM(ps.population_count), 0)::bigint as total_population
      FROM country c
      INNER JOIN country_language cl ON c.id = cl.country_id
      LEFT JOIN population_stat ps ON c.id = ps.country_id
      LEFT JOIN sex s ON ps.sex_id = s.id
      LEFT JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE cl.language_id = 311
        AND (ps.year = 2024 OR ps.year IS NULL)
        AND (s.code = 'total' OR s.code IS NULL)
        AND (ag.label = 'ALL' OR ag.label IS NULL)
      GROUP BY c.id, c.iso3, c.name
      ORDER BY total_population DESC
      LIMIT 10
    `);
    frenchPopulation.rows.forEach((row, i) => {
      const pop = parseInt(row.total_population);
      console.log(`   ${i + 1}. ${row.name} (${row.iso3}): ${pop.toLocaleString()} hab.`);
    });
    
    // Test 5: Combinaison de filtres (français + tranche d'âge)
    console.log('\n5. Population 20-24 ans des pays francophones (2024):');
    const frenchYoung = await pool.query(`
      WITH age_data AS (
        SELECT 
          c.id as country_id,
          c.iso3,
          c.name,
          ps.population_count,
          ps.source,
          (SELECT population_count 
           FROM population_stat ps2 
           JOIN age_group ag2 ON ps2.age_group_id = ag2.id 
           WHERE ps2.country_id = c.id 
             AND ps2.year = 2024
             AND ps2.sex_id IN (SELECT id FROM sex WHERE code IN ('male', 'female'))
             AND ag2.label = 'ALL'
           LIMIT 1) as total_pop
        FROM country c
        INNER JOIN country_language cl ON c.id = cl.country_id
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        WHERE ps.year = 2024
          AND ag.label = '20-24'
          AND s.code IN ('male', 'female')
          AND cl.language_id = 311
      )
      SELECT 
        iso3,
        name,
        SUM(
          CASE 
            WHEN source LIKE '%Absolute%' THEN population_count::bigint
            WHEN source LIKE '%Percentage%' THEN 
              ROUND((population_count::numeric / 10000 / 100) * total_pop::numeric)::bigint
            ELSE population_count::bigint
          END
        ) as total_population
      FROM age_data
      GROUP BY iso3, name
      ORDER BY total_population DESC
      LIMIT 5
    `);
    frenchYoung.rows.forEach((row, i) => {
      const pop = parseInt(row.total_population);
      console.log(`   ${i + 1}. ${row.name}: ${pop.toLocaleString()} personnes (20-24 ans)`);
    });
    
    console.log('\n✅ Tests terminés avec succès');
  } catch (error) {
    console.error('❌ Erreur:', error.message);
  } finally {
    await pool.end();
  }
}

testLanguageFilter();
