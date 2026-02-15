const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/metadata/years - Liste des années disponibles
router.get('/years', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT value as year
      FROM year_table
      ORDER BY value
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows.map(row => row.year)
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des années:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des années' 
    });
  }
});

// GET /api/metadata/age-groups - Liste des groupes d'âge
router.get('/age-groups', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, label, age_min, age_max
      FROM age_group
      ORDER BY age_min
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des groupes d\'âge:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des groupes d\'âge' 
    });
  }
});

// GET /api/metadata/sex-categories - Liste des catégories de sexe
router.get('/sex-categories', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, code, label
      FROM sex
      ORDER BY id
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des catégories de sexe:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des catégories' 
    });
  }
});

// GET /api/metadata/regions - Liste des régions
router.get('/regions', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT DISTINCT region
      FROM country
      WHERE region IS NOT NULL
      ORDER BY region
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows.map(row => row.region)
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des régions:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des régions' 
    });
  }
});

// GET /api/metadata/languages - Liste des langues disponibles
router.get('/languages', async (req, res) => {
  try {
    // Grouper par code de base (les 2 premières lettres) pour inclure toutes les variantes
    const result = await pool.query(`
      WITH language_base AS (
        SELECT 
          l.id,
          l.iso_code,
          CASE 
            WHEN l.iso_code LIKE '%-%' THEN SUBSTRING(l.iso_code FROM 1 FOR POSITION('-' IN l.iso_code) - 1)
            ELSE l.iso_code
          END as base_code,
          cl.country_id
        FROM language l
        LEFT JOIN country_language cl ON l.id = cl.language_id
      )
      SELECT 
        base_code as iso_code,
        base_code as name,
        COUNT(DISTINCT country_id) as country_count,
        ARRAY_AGG(DISTINCT id) as language_ids
      FROM language_base
      WHERE country_id IS NOT NULL
      GROUP BY base_code
      HAVING COUNT(DISTINCT country_id) > 0
      ORDER BY country_count DESC, base_code
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des langues:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des langues' 
    });
  }
});

// GET /api/metadata/stats - Statistiques générales
router.get('/stats', async (req, res) => {
  try {
    const [countries, years, dataPoints] = await Promise.all([
      pool.query('SELECT COUNT(*) as count FROM country'),
      pool.query('SELECT COUNT(*) as count FROM year_table'),
      pool.query('SELECT COUNT(*) as count FROM population_stat')
    ]);

    res.json({
      success: true,
      data: {
        total_countries: parseInt(countries.rows[0].count),
        total_years: parseInt(years.rows[0].count),
        total_data_points: parseInt(dataPoints.rows[0].count)
      }
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des statistiques:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des statistiques' 
    });
  }
});

module.exports = router;
