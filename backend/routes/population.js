const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/population/summary - Résumé de la population de tous les pays
router.get('/summary', async (req, res) => {
  try {
    const { year, sex, ageGroup } = req.query;
    
    // Année par défaut : la plus récente avec des données
    const yearValue = year || await getLatestYear();
    const sexCode = sex || 'total';
    const ageGroupId = ageGroup || null;

    let query;
    let params;

    // Si on filtre par une tranche d'âge spécifique (pas ALL)
    if (ageGroupId && ageGroupId !== 'ALL') {
      // Requête pour calculer la population par tranche d'âge
      // Il faut récupérer les données male ET female, puis calculer selon le type de source
      query = `
        WITH age_data AS (
          SELECT 
            c.id as country_id,
            c.iso3,
            c.name,
            c.region,
            s.code as sex_code,
            ps.population_count,
            ps.source,
            -- Récupérer la population totale pour le calcul des pourcentages
            (SELECT population_count 
             FROM population_stat ps2 
             JOIN age_group ag2 ON ps2.age_group_id = ag2.id 
             WHERE ps2.country_id = c.id 
               AND ps2.year = $1 
               AND ps2.sex_id = s.id 
               AND ag2.label = 'ALL'
             LIMIT 1) as total_pop
          FROM country c
          INNER JOIN population_stat ps ON c.id = ps.country_id
          INNER JOIN sex s ON ps.sex_id = s.id
          INNER JOIN age_group ag ON ps.age_group_id = ag.id
          WHERE ps.year = $1
            AND ag.id = $2
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
      `;
      params = [yearValue, ageGroupId];
      
    } else {
      // Requête standard pour ALL ou sans filtre d'âge
      query = `
        SELECT 
          c.iso3,
          c.name,
          c.region,
          COALESCE(SUM(ps.population_count), 0)::bigint as total_population
        FROM country c
        LEFT JOIN population_stat ps ON c.id = ps.country_id
        LEFT JOIN sex s ON ps.sex_id = s.id
        LEFT JOIN age_group ag ON ps.age_group_id = ag.id
        WHERE (ps.year = $1 OR ps.year IS NULL)
          AND (s.code = $2 OR s.code IS NULL)
          AND (ag.label = 'ALL' OR ag.label IS NULL)
        GROUP BY c.id, c.iso3, c.name, c.region
        ORDER BY total_population DESC
      `;
      params = [yearValue, sexCode];
    }

    const result = await pool.query(query, params);

    // Convertir les chaînes en nombres pour éviter les problèmes dans le frontend
    const data = result.rows.map(row => ({
      ...row,
      total_population: parseInt(row.total_population, 10)
    }));

    res.json({
      success: true,
      year: yearValue,
      sex: sexCode,
      ageGroup: ageGroupId || 'ALL',
      count: data.length,
      data: data
    });
  } catch (error) {
    console.error('Erreur lors de la récupération du résumé:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des données' 
    });
  }
});

// GET /api/population/country/:iso3 - Population détaillée d'un pays
router.get('/country/:iso3', async (req, res) => {
  try {
    const { iso3 } = req.params;
    const { year, sex, ageGroup } = req.query;

    let query = `
      SELECT 
        ps.year,
        s.code as sex,
        s.label as sex_label,
        ag.label as age_group,
        ag.age_min,
        ag.age_max,
        ps.population_count,
        ps.source
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1
    `;

    const params = [iso3.toUpperCase()];
    let paramCount = 1;

    if (year) {
      paramCount++;
      query += ` AND ps.year = $${paramCount}`;
      params.push(year);
    }

    if (sex) {
      paramCount++;
      query += ` AND s.code = $${paramCount}`;
      params.push(sex);
    }

    if (ageGroup) {
      paramCount++;
      query += ` AND ag.id = $${paramCount}`;
      params.push(ageGroup);
    }

    query += ` ORDER BY ps.year DESC, ag.age_min, s.code`;

    const result = await pool.query(query, params);

    res.json({
      success: true,
      iso3: iso3.toUpperCase(),
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des données de population:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des données' 
    });
  }
});

// GET /api/population/trend/:iso3 - Évolution de la population d'un pays
router.get('/trend/:iso3', async (req, res) => {
  try {
    const { iso3 } = req.params;
    const { sex } = req.query;
    const sexCode = sex || 'total';

    const result = await pool.query(`
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
    `, [iso3.toUpperCase(), sexCode]);

    res.json({
      success: true,
      iso3: iso3.toUpperCase(),
      sex: sexCode,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération de la tendance:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des données' 
    });
  }
});

// GET /api/population/pyramid/:iso3 - Pyramide des âges
router.get('/pyramid/:iso3', async (req, res) => {
  try {
    const { iso3 } = req.params;
    const { year } = req.query;
    const yearValue = year || await getLatestYear();

    // Récupérer d'abord la population totale du pays pour cette année
    const totalPopResult = await pool.query(`
      SELECT 
        s.code as sex,
        ps.population_count as total
      FROM population_stat ps
      JOIN country c ON ps.country_id = c.id
      JOIN sex s ON ps.sex_id = s.id
      JOIN age_group ag ON ps.age_group_id = ag.id
      WHERE c.iso3 = $1 
        AND ps.year = $2
        AND ag.label = 'ALL'
        AND s.code IN ('male', 'female')
    `, [iso3.toUpperCase(), yearValue]);

    const totalPopulation = {};
    totalPopResult.rows.forEach(row => {
      totalPopulation[row.sex] = parseInt(row.total);
    });

    // Récupérer les données par tranche d'âge
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
    `, [iso3.toUpperCase(), yearValue]);

    // Formater les données pour une pyramide
    const pyramid = result.rows.reduce((acc, row) => {
      const existing = acc.find(item => item.age_group === row.age_group);
      
      // Calculer la population en fonction du type de source
      let population;
      if (row.source?.includes('Absolute')) {
        // Valeur absolue - utiliser directement
        population = parseInt(row.population_count);
      } else if (row.source?.includes('Percentage')) {
        // Pourcentage * 10000 - calculer la population absolue
        const percentage = parseInt(row.population_count) / 10000 / 100; // Convertir en décimal
        const sexTotal = totalPopulation[row.sex] || 0;
        population = Math.round(sexTotal * percentage);
      } else {
        // Fallback - utiliser la valeur telle quelle
        population = parseInt(row.population_count);
      }
      
      if (existing) {
        existing[row.sex] = population;
      } else {
        acc.push({
          age_group: row.age_group,
          age_min: row.age_min,
          age_max: row.age_max,
          [row.sex]: population
        });
      }
      return acc;
    }, []);

    res.json({
      success: true,
      iso3: iso3.toUpperCase(),
      year: yearValue,
      data: pyramid
    });
  } catch (error) {
    console.error('Erreur lors de la récupération de la pyramide:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des données' 
    });
  }
});

// Fonction helper pour obtenir l'année la plus récente
async function getLatestYear() {
  const result = await pool.query('SELECT MAX(value) as max_year FROM year_table');
  return result.rows[0].max_year || new Date().getFullYear();
}

module.exports = router;
