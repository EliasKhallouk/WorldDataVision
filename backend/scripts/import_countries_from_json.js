const fs = require('fs');
const path = require('path');
const pool = require('../config/database');

async function importCountriesFromJson() {
  console.log('=== Import des données depuis countries.json ===\n');
  
  try {
    // Lire le fichier JSON
    const jsonPath = path.join(__dirname, '../../Data/countries.json');
    console.log('📖 Lecture du fichier:', jsonPath);
    const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    console.log(`✅ ${jsonData.length} pays trouvés dans le fichier JSON\n`);

    // Étape 1: Supprimer toutes les langues existantes
    console.log('🗑️  Étape 1/4: Suppression des données de langues existantes...');
    await pool.query('DELETE FROM country_language');
    console.log('   ✅ Relations pays-langues supprimées');
    await pool.query('DELETE FROM language');
    console.log('   ✅ Langues supprimées\n');

    // Étape 2: Mettre à jour les informations des pays
    console.log('🔍 Étape 2/5: Mise à jour des informations des pays...');
    const countryResult = await pool.query('SELECT id, iso2, iso3, name FROM country ORDER BY name');
    const countryMap = new Map();
    countryResult.rows.forEach(row => {
      countryMap.set(row.iso2, { id: row.id, iso3: row.iso3, name: row.name });
    });
    console.log(`   ✅ ${countryMap.size} pays trouvés dans la base`);
    
    let countriesUpdated = 0;
    for (const country of jsonData) {
      const countryInfo = countryMap.get(country.code);
      if (!countryInfo) {
        console.log(`   ⚠️  Pays non trouvé dans la base: ${country.name} (${country.code})`);
        continue;
      }

      // Convertir les codes ISO2 des frontières en IDs
      let borderIds = null;
      if (country.borders && country.borders.length > 0) {
        borderIds = country.borders
          .map(borderCode => {
            const borderCountry = countryMap.get(borderCode);
            return borderCountry ? borderCountry.id : null;
          })
          .filter(id => id !== null);
      }

      await pool.query(`
        UPDATE country SET
          name_local = $1,
          area_sq_km = $2,
          continent = $3,
          capital = $4,
          capital_latitude = $5,
          capital_longitude = $6,
          currency_name = $7,
          currency_local = $8,
          currency_code = $9,
          currency_symbol = $10,
          currency_numeric = $11,
          currency_subunit_value = $12,
          currency_subunit_name = $13,
          flag = $14,
          timezones = $15,
          borders = $16
        WHERE id = $17
      `, [
        country.name_local || null,
        country.area_sq_km || null,
        country.continent || null,
        country.capital_name || null,
        country.capital_latitude || null,
        country.capital_longitude || null,
        country.currency || null,
        country.currency_local || null,
        country.currency_code || null,
        country.currency_symbol || null,
        country.currency_numeric || null,
        country.currency_subunit_value || null,
        country.currency_subunit_name || null,
        country.flag || null,
        country.timezones || null,
        borderIds,
        countryInfo.id
      ]);
      countriesUpdated++;
    }
    console.log(`   ✅ ${countriesUpdated} pays mis à jour\n`);

    // Étape 3: Importer les langues
    console.log('📝 Étape 3/5: Import des langues...');
    const languageMap = new Map(); // Map: iso_code -> language_id
    let languagesImported = 0;

    for (const country of jsonData) {
      if (!country.languages || country.languages.length === 0) {
        continue;
      }

      // Vérifier si le pays existe dans notre base
      const countryInfo = countryMap.get(country.code);
      if (!countryInfo) {
        console.log(`   ⚠️  Pays non trouvé: ${country.name} (${country.code})`);
        continue;
      }

      // Traiter chaque langue du pays
      for (const lang of country.languages) {
        const isoCode = lang.iso_639_1 || lang.iso_639_2 || lang.iso_639_3;
        
        if (!isoCode) {
          console.log(`   ⚠️  Langue sans code ISO pour ${country.name}: ${lang.name}`);
          continue;
        }

        // Vérifier si la langue existe déjà dans notre map
        if (!languageMap.has(isoCode)) {
          // Insérer la nouvelle langue
          const insertLang = await pool.query(
            `INSERT INTO language (iso_code, name, group_name) 
             VALUES ($1, $2, $3) 
             RETURNING id`,
            [isoCode, lang.name, null]
          );
          languageMap.set(isoCode, insertLang.rows[0].id);
          languagesImported++;
        }
      }
    }
    console.log(`   ✅ ${languagesImported} langues uniques importées\n`);

    // Étape 4: Créer les relations pays-langues
    console.log('🔗 Étape 4/5: Création des relations pays-langues...');
    let relationsCreated = 0;
    const relations = new Set(); // Pour éviter les doublons

    for (const country of jsonData) {
      if (!country.languages || country.languages.length === 0) {
        continue;
      }

      const countryInfo = countryMap.get(country.code);
      if (!countryInfo) {
        continue;
      }

      for (const lang of country.languages) {
        const isoCode = lang.iso_639_1 || lang.iso_639_2 || lang.iso_639_3;
        
        if (!isoCode || !languageMap.has(isoCode)) {
          continue;
        }

        const languageId = languageMap.get(isoCode);
        const relationKey = `${countryInfo.id}-${languageId}`;

        // Éviter les doublons
        if (!relations.has(relationKey)) {
          await pool.query(
            `INSERT INTO country_language (country_id, language_id) 
             VALUES ($1, $2)`,
            [countryInfo.id, languageId]
          );
          relations.add(relationKey);
          relationsCreated++;
        }
      }
    }
    console.log(`   ✅ ${relationsCreated} relations créées\n`);

    // Étape 5: Statistiques finales
    console.log('📊 Étape 5/5: Statistiques finales:');
    const stats = await pool.query(`
      SELECT 
        (SELECT COUNT(*) FROM country WHERE name_local IS NOT NULL) as countries_updated,
        (SELECT COUNT(*) FROM language) as total_languages,
        (SELECT COUNT(*) FROM country_language) as total_relations,
        (SELECT COUNT(DISTINCT country_id) FROM country_language) as countries_with_languages
    `);
    
    console.log(`   - Pays mis à jour avec nouvelles infos: ${stats.rows[0].countries_updated}`);
    console.log(`   - Langues dans la base: ${stats.rows[0].total_languages}`);
    console.log(`   - Relations pays-langues: ${stats.rows[0].total_relations}`);
    console.log(`   - Pays avec au moins une langue: ${stats.rows[0].countries_with_languages}`);

    // Afficher quelques exemples
    console.log('\n📋 Exemples de pays avec leurs informations:');
    const examples = await pool.query(`
      SELECT 
        c.name,
        c.iso3,
        c.flag,
        c.continent,
        c.area_sq_km,
        c.capital,
        c.currency_code,
        c.currency_symbol,
        STRING_AGG(l.name, ', ' ORDER BY l.name) as languages
      FROM country c
      LEFT JOIN country_language cl ON c.id = cl.country_id
      LEFT JOIN language l ON cl.language_id = l.id
      WHERE c.iso3 IN ('FRA', 'USA', 'MAR', 'CAN', 'CHE')
      GROUP BY c.id, c.name, c.iso3, c.flag, c.continent, c.area_sq_km, c.capital, c.currency_code, c.currency_symbol
      ORDER BY c.name
    `);

    examples.rows.forEach(row => {
      console.log(`   ${row.flag} ${row.name} (${row.iso3})`);
      console.log(`      Continent: ${row.continent || 'N/A'}`);
      console.log(`      Superficie: ${row.area_sq_km ? parseInt(row.area_sq_km).toLocaleString() + ' km²' : 'N/A'}`);
      console.log(`      Capitale: ${row.capital || 'N/A'}`);
      console.log(`      Devise: ${row.currency_code || 'N/A'} ${row.currency_symbol || ''}`);
      console.log(`      Langues: ${row.languages || 'N/A'}`);
      console.log('');
    });

    console.log('\n✅ Import terminé avec succès!');

  } catch (error) {
    console.error('❌ Erreur lors de l\'import:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

// Exécuter l'import
importCountriesFromJson();
