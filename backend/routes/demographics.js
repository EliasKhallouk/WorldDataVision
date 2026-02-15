const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/demographics/global-stats - Statistiques démographiques globales
router.get('/global-stats', async (req, res) => {
  try {
    const { year, sex, language } = req.query;
    
    const yearValue = year || 2024;
    const sexCode = sex || 'total';

    // Requête pour obtenir toutes les données démographiques agrégées
    const query = `
      WITH country_totals AS (
        -- Population totale par pays
        SELECT 
          c.id,
          c.name,
          ps.population_count as total_pop
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        ${language && language !== 'ALL' ? `
        INNER JOIN country_language cl ON c.id = cl.country_id
        INNER JOIN language l ON cl.language_id = l.id` : ''}
        WHERE ps.year = $1
          AND s.code = $2
          AND ag.label = 'ALL'
          ${language && language !== 'ALL' ? `
          AND (l.iso_code = $3 OR l.iso_code LIKE $3 || '-%')` : ''}
      ),
      sex_totals AS (
        -- Population par sexe (nécessaire pour les conversions de pourcentages)
        SELECT 
          c.id,
          s.code as sex_code,
          ps.population_count as sex_pop
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        ${language && language !== 'ALL' ? `
        INNER JOIN country_language cl ON c.id = cl.country_id
        INNER JOIN language l ON cl.language_id = l.id` : ''}
        WHERE ps.year = $1
          AND s.code IN ('male', 'female')
          AND ag.label = 'ALL'
          ${language && language !== 'ALL' ? `
          AND (l.iso_code = $3 OR l.iso_code LIKE $3 || '-%')` : ''}
      ),
      age_data AS (
        -- Données par tranches d'âge avec conversion correcte
        -- Les pourcentages sont relatifs à la population du SEXE, pas au total
        SELECT 
          c.id,
          ag.age_min,
          ag.age_max,
          SUM(
            CASE 
              -- Si la source contient 'Percentage', c'est un pourcentage * 10000
              -- On divise par 10000 pour avoir le %, puis on multiplie par la population DU SEXE
              WHEN ps.source LIKE '%Percentage%' AND st.sex_pop IS NOT NULL 
              THEN (ps.population_count / 10000.0) * st.sex_pop / 100.0
              -- Si absolu, prendre la valeur directement
              ELSE ps.population_count
            END
          ) as age_population
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        INNER JOIN sex_totals st ON c.id = st.id AND s.code = st.sex_code
        ${language && language !== 'ALL' ? `
        INNER JOIN country_language cl ON c.id = cl.country_id
        INNER JOIN language l ON cl.language_id = l.id` : ''}
        WHERE ps.year = $1
          AND (
            -- Si on veut 'total', additionner male + female
            ($2 = 'total' AND s.code IN ('male', 'female'))
            -- Sinon prendre le sexe spécifié
            OR s.code = $2
          )
          AND ag.label != 'ALL'
          ${language && language !== 'ALL' ? `
          AND (l.iso_code = $3 OR l.iso_code LIKE $3 || '-%')` : ''}
        GROUP BY c.id, ag.age_min, ag.age_max
      ),
      age_aggregates AS (
        SELECT 
          SUM(CASE WHEN age_min < 15 THEN age_population ELSE 0 END) as under_15,
          SUM(CASE WHEN age_min >= 65 THEN age_population ELSE 0 END) as over_65,
          SUM(CASE WHEN age_min >= 15 AND age_min < 65 THEN age_population ELSE 0 END) as working_age,
          SUM(age_population) as total_from_ages
        FROM age_data
      )
      SELECT 
        (SELECT SUM(total_pop) FROM country_totals) as total_population,
        (SELECT COUNT(*) FROM country_totals) as countries_count,
        (SELECT AVG(total_pop) FROM country_totals) as avg_population,
        aa.under_15,
        aa.over_65,
        aa.working_age,
        aa.total_from_ages,
        -- Calculs des pourcentages
        CASE WHEN aa.total_from_ages > 0 
          THEN (aa.under_15 * 100.0 / aa.total_from_ages) 
          ELSE 0 
        END as pct_under_15,
        CASE WHEN aa.total_from_ages > 0 
          THEN (aa.over_65 * 100.0 / aa.total_from_ages) 
          ELSE 0 
        END as pct_over_65,
        -- Ratio actifs/dépendants
        CASE WHEN aa.working_age > 0 
          THEN ((aa.under_15 + aa.over_65) * 100.0 / aa.working_age) 
          ELSE 0 
        END as dependency_ratio
      FROM age_aggregates aa
    `;

    const params = language && language !== 'ALL' 
      ? [yearValue, sexCode, language] 
      : [yearValue, sexCode];

    const result = await pool.query(query, params);

    if (result.rows.length === 0) {
      return res.json({
        success: true,
        data: null
      });
    }

    const stats = result.rows[0];

    // Calcul de l'âge médian estimé
    // Estimation simplifiée basée sur la distribution par tranche
    // Assume une distribution uniforme dans chaque tranche
    const pctUnder15 = parseFloat(stats.pct_under_15);
    const pctOver65 = parseFloat(stats.pct_over_65);
    const pctWorking = 100 - pctUnder15 - pctOver65;
    
    let medianAge = 30; // Valeur par défaut
    
    if (pctUnder15 >= 50) {
      // La médiane est dans la tranche 0-15
      medianAge = (50 / pctUnder15) * 15;
    } else if (pctUnder15 + pctWorking >= 50) {
      // La médiane est dans la tranche 15-65
      const remainingToMedian = 50 - pctUnder15;
      medianAge = 15 + (remainingToMedian / pctWorking) * 50;
    } else {
      // La médiane est dans la tranche 65+
      const remainingToMedian = 50 - pctUnder15 - pctWorking;
      medianAge = 65 + (remainingToMedian / pctOver65) * 15; // Assume max 80 ans
    }

    // Calcul du taux de vieillissement (index de vieillissement)
    const agingIndex = pctUnder15 > 0 
      ? (pctOver65 * 100 / pctUnder15)
      : 0;

    // Calcul de l'indice de jeunesse (inverse de l'indice de vieillissement)
    const youthIndex = pctOver65 > 0 
      ? (pctUnder15 * 100 / pctOver65)
      : (pctUnder15 > 0 ? 999 : 0); // 999 si pas de personnes âgées mais des jeunes

    res.json({
      success: true,
      data: {
        total_population: parseFloat(stats.total_population) || 0,
        countries_count: parseInt(stats.countries_count) || 0,
        avg_population: parseFloat(stats.avg_population) || 0,
        
        // Populations par groupe
        population_under_15: parseFloat(stats.under_15) || 0,
        population_over_65: parseFloat(stats.over_65) || 0,
        population_working_age: parseFloat(stats.working_age) || 0,
        
        // Pourcentages
        pct_under_15: parseFloat(stats.pct_under_15).toFixed(2),
        pct_over_65: parseFloat(stats.pct_over_65).toFixed(2),
        pct_working_age: (100 - parseFloat(stats.pct_under_15) - parseFloat(stats.pct_over_65)).toFixed(2),
        
        // Indicateurs
        dependency_ratio: parseFloat(stats.dependency_ratio).toFixed(2),
        median_age_estimated: parseFloat(medianAge).toFixed(1),
        aging_index: parseFloat(agingIndex).toFixed(1),
        youth_index: parseFloat(youthIndex).toFixed(1),
        
        // Ratio actifs/inactifs
        active_inactive_ratio: stats.working_age > 0 
          ? (parseFloat(stats.working_age) / (parseFloat(stats.under_15) + parseFloat(stats.over_65))).toFixed(2)
          : 0
      }
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des stats démographiques:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des statistiques démographiques' 
    });
  }
});

// GET /api/demographics/gender-balance - Équilibre H/F global
router.get('/gender-balance', async (req, res) => {
  try {
    const { year, language } = req.query;
    
    const yearValue = year || 2024;

    const query = `
      SELECT 
        SUM(CASE WHEN s.code = 'male' THEN ps.population_count ELSE 0 END) as male_population,
        SUM(CASE WHEN s.code = 'female' THEN ps.population_count ELSE 0 END) as female_population,
        COUNT(DISTINCT c.id) as countries_count
      FROM country c
      INNER JOIN population_stat ps ON c.id = ps.country_id
      INNER JOIN sex s ON ps.sex_id = s.id
      INNER JOIN age_group ag ON ps.age_group_id = ag.id
      ${language && language !== 'ALL' ? `
      INNER JOIN country_language cl ON c.id = cl.country_id
      INNER JOIN language l ON cl.language_id = l.id` : ''}
      WHERE ps.year = $1
        AND s.code IN ('male', 'female')
        AND ag.label = 'ALL'
        ${language && language !== 'ALL' ? `
        AND (l.iso_code = $2 OR l.iso_code LIKE $2 || '-%')` : ''}
    `;

    const params = language && language !== 'ALL' 
      ? [yearValue, language] 
      : [yearValue];

    const result = await pool.query(query, params);

    if (result.rows.length === 0) {
      return res.json({
        success: true,
        data: null
      });
    }

    const stats = result.rows[0];
    const malePopulation = parseFloat(stats.male_population) || 0;
    const femalePopulation = parseFloat(stats.female_population) || 0;
    const totalPopulation = malePopulation + femalePopulation;

    // Ratio hommes/femmes (nombre d'hommes pour 100 femmes)
    const genderRatio = femalePopulation > 0 
      ? (malePopulation * 100 / femalePopulation)
      : 0;

    res.json({
      success: true,
      data: {
        male_population: malePopulation,
        female_population: femalePopulation,
        total_population: totalPopulation,
        pct_male: totalPopulation > 0 ? ((malePopulation * 100 / totalPopulation).toFixed(2)) : 0,
        pct_female: totalPopulation > 0 ? ((femalePopulation * 100 / totalPopulation).toFixed(2)) : 0,
        gender_ratio: genderRatio.toFixed(2), // Hommes pour 100 femmes
        gender_balance_index: (100 - Math.abs(genderRatio - 100)).toFixed(2), // 100 = parfait équilibre
        countries_count: parseInt(stats.countries_count) || 0
      }
    });
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'équilibre H/F:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération de l\'équilibre H/F' 
    });
  }
});

// GET /api/demographics/scatter-data - Données pour scatter plot (croissance vs âge médian)
router.get('/scatter-data', async (req, res) => {
  try {
    const { year, language } = req.query;
    
    const yearValue = parseInt(year) || 2024;
    const previousYear = yearValue - 10; // Comparer sur 10 ans

    const query = `
      WITH current_year AS (
        SELECT 
          c.id,
          c.name,
          c.iso3,
          ps.population_count as current_population
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        ${language && language !== 'ALL' ? `
        INNER JOIN country_language cl ON c.id = cl.country_id
        INNER JOIN language l ON cl.language_id = l.id` : ''}
        WHERE ps.year = $1
          AND s.code = 'total'
          AND ag.label = 'ALL'
          ${language && language !== 'ALL' ? `
          AND (l.iso_code = $3 OR l.iso_code LIKE $3 || '-%')` : ''}
      ),
      previous_year AS (
        SELECT 
          c.id,
          ps.population_count as previous_population
        FROM country c
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        WHERE ps.year = $2
          AND s.code = 'total'
          AND ag.label = 'ALL'
      ),
      age_distribution AS (
        SELECT 
          c.id,
          SUM(CASE WHEN ag.age_min < 15 THEN 
            CASE 
              WHEN ps.source LIKE '%Percentage%' THEN (ps.population_count / 10000.0)
              ELSE (ps.population_count * 100.0 / cy.current_population)
            END
          ELSE 0 END) as pct_under_15,
          SUM(CASE WHEN ag.age_min >= 65 THEN 
            CASE 
              WHEN ps.source LIKE '%Percentage%' THEN (ps.population_count / 10000.0)
              ELSE (ps.population_count * 100.0 / cy.current_population)
            END
          ELSE 0 END) as pct_over_65
        FROM country c
        INNER JOIN current_year cy ON c.id = cy.id
        INNER JOIN population_stat ps ON c.id = ps.country_id
        INNER JOIN sex s ON ps.sex_id = s.id
        INNER JOIN age_group ag ON ps.age_group_id = ag.id
        WHERE ps.year = $1
          AND s.code IN ('male', 'female')
          AND ag.label != 'ALL'
        GROUP BY c.id
      )
      SELECT 
        cy.id,
        cy.name,
        cy.iso3,
        cy.current_population,
        py.previous_population,
        ad.pct_under_15,
        ad.pct_over_65,
        CASE 
          WHEN py.previous_population > 0 
          THEN ((cy.current_population - py.previous_population) * 100.0 / py.previous_population)
          ELSE 0
        END as growth_rate
      FROM current_year cy
      LEFT JOIN previous_year py ON cy.id = py.id
      LEFT JOIN age_distribution ad ON cy.id = ad.id
      WHERE cy.current_population > 100000
      ORDER BY cy.current_population DESC
    `;

    const params = language && language !== 'ALL' 
      ? [yearValue, previousYear, language] 
      : [yearValue, previousYear];

    const result = await pool.query(query, params);

    // Calculer l'âge médian pour chaque pays
    const data = result.rows.map(row => {
      const pctUnder15 = parseFloat(row.pct_under_15) || 0;
      const pctOver65 = parseFloat(row.pct_over_65) || 0;
      const pctWorking = 100 - pctUnder15 - pctOver65;
      
      let medianAge = 30;
      if (pctUnder15 >= 50) {
        medianAge = (50 / pctUnder15) * 15;
      } else if (pctUnder15 + pctWorking >= 50) {
        const remainingToMedian = 50 - pctUnder15;
        medianAge = 15 + (remainingToMedian / pctWorking) * 50;
      } else {
        const remainingToMedian = 50 - pctUnder15 - pctWorking;
        medianAge = 65 + (remainingToMedian / pctOver65) * 15;
      }

      return {
        id: row.id,
        name: row.name,
        iso3: row.iso3,
        population: parseFloat(row.current_population),
        growth_rate: parseFloat(row.growth_rate).toFixed(2),
        median_age: parseFloat(medianAge).toFixed(1)
      };
    });

    res.json({
      success: true,
      data: data,
      year: yearValue,
      comparison_year: previousYear
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des données scatter:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des données scatter' 
    });
  }
});

module.exports = router;
