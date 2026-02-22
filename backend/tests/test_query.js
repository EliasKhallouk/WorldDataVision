const pool = require('./config/database');

async function testQuery() {
  try {
    const result = await pool.query(`
      SELECT ps.id, c.name, c.iso3, ps.year, s.code as sex, ps.population_count, ps.age_group_id 
      FROM population_stat ps 
      JOIN country c ON ps.country_id = c.id 
      JOIN sex s ON ps.sex_id = s.id 
      WHERE ps.country_id=511 AND ps.year=1960 
      ORDER BY ps.id ASC
    `);

    console.log('\n========================================');
    console.log('RÉSULTATS DE LA REQUÊTE:');
    console.log('========================================');
    console.log(`Nombre de lignes: ${result.rows.length}`);
    console.log('');
    
    if (result.rows.length > 0) {
      console.log('Données trouvées:');
      result.rows.forEach(row => {
        console.log(`ID: ${row.id} | Pays: ${row.name} (${row.iso3}) | Année: ${row.year} | Sexe: ${row.sex} | Population: ${row.population_count} | Age Group ID: ${row.age_group_id}`);
      });
      
      console.log('\n========================================');
      console.log('ANALYSE DE COHÉRENCE:');
      console.log('========================================');
      
      // Grouper par sexe
      const bySex = result.rows.reduce((acc, row) => {
        acc[row.sex] = (acc[row.sex] || 0) + row.population_count;
        return acc;
      }, {});
      
      console.log('Total par sexe:');
      Object.keys(bySex).forEach(sex => {
        console.log(`  ${sex}: ${bySex[sex].toLocaleString('fr-FR')}`);
      });
      
      if (bySex.male && bySex.female && bySex.total) {
        const sum = bySex.male + bySex.female;
        const diff = Math.abs(bySex.total - sum);
        console.log(`\nVérification: male + female = ${sum.toLocaleString('fr-FR')}`);
        console.log(`Total dans la base: ${bySex.total.toLocaleString('fr-FR')}`);
        console.log(`Différence: ${diff.toLocaleString('fr-FR')}`);
        
        if (diff === 0) {
          console.log('✅ COHÉRENT: total = male + female');
        } else {
          console.log('⚠️  INCOHÉRENT: total ≠ male + female');
        }
      }
    } else {
      console.log('❌ Aucune donnée trouvée pour country_id=511 en 1960');
    }
    
    // Vérifier quel pays est le country_id 511
    const countryResult = await pool.query('SELECT * FROM country WHERE id = 511');
    console.log('\n========================================');
    console.log('INFORMATIONS SUR LE PAYS (ID 511):');
    console.log('========================================');
    if (countryResult.rows.length > 0) {
      const country = countryResult.rows[0];
      console.log(`Nom: ${country.name}`);
      console.log(`ISO2: ${country.iso2}`);
      console.log(`ISO3: ${country.iso3}`);
      console.log(`Région: ${country.region}`);
    }
    
    process.exit(0);
  } catch (error) {
    console.error('Erreur:', error);
    process.exit(1);
  }
}

testQuery();
