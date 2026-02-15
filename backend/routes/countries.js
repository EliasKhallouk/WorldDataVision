const express = require('express');
const router = express.Router();
const pool = require('../config/database');

// GET /api/countries/mapping/iso2-to-iso3 - Récupérer le mapping ISO2 -> ISO3
router.get('/mapping/iso2-to-iso3', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT iso2, iso3
      FROM country
      ORDER BY iso2
    `);

    // Créer un objet de mapping { "FR": "FRA", "US": "USA", ... }
    const mapping = result.rows.reduce((acc, row) => {
      acc[row.iso2] = row.iso3;
      return acc;
    }, {});

    res.json({
      success: true,
      data: mapping
    });
  } catch (error) {
    console.error('Erreur lors de la récupération du mapping ISO:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération du mapping ISO' 
    });
  }
});

// GET /api/countries - Récupérer tous les pays
router.get('/', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        id,
        iso2,
        iso3,
        name,
        region,
        capital,
        currency_name,
        is_independent
      FROM country
      ORDER BY name
    `);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des pays:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des pays' 
    });
  }
});

// GET /api/countries/:iso3 - Récupérer un pays spécifique
router.get('/:iso3', async (req, res) => {
  try {
    const { iso3 } = req.params;
    
    const result = await pool.query(`
      WITH border_countries AS (
        SELECT 
          c.id,
          ARRAY(
            SELECT bc.name
            FROM unnest(c.borders) AS border_id
            JOIN country bc ON bc.id = border_id
            ORDER BY bc.name
          ) as border_names
        FROM country c
        WHERE c.iso3 = $1
      )
      SELECT 
        c.*,
        COALESCE(bc.border_names, ARRAY[]::text[]) as borders,
        COALESCE(
          json_agg(
            json_build_object('id', l.id, 'name', l.name, 'iso_code', l.iso_code)
          ) FILTER (WHERE l.id IS NOT NULL),
          '[]'
        ) as languages
      FROM country c
      LEFT JOIN border_countries bc ON c.id = bc.id
      LEFT JOIN country_language cl ON c.id = cl.country_id
      LEFT JOIN language l ON cl.language_id = l.id
      WHERE c.iso3 = $1
      GROUP BY c.id, bc.border_names
    `, [iso3.toUpperCase()]);

    if (result.rows.length === 0) {
      return res.status(404).json({ 
        success: false,
        error: 'Pays non trouvé' 
      });
    }

    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Erreur lors de la récupération du pays:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération du pays' 
    });
  }
});

// GET /api/countries/region/:region - Récupérer les pays d'une région
router.get('/region/:region', async (req, res) => {
  try {
    const { region } = req.params;
    
    const result = await pool.query(`
      SELECT 
        id,
        iso2,
        iso3,
        name,
        region,
        capital
      FROM country
      WHERE LOWER(region) = LOWER($1)
      ORDER BY name
    `, [region]);

    res.json({
      success: true,
      count: result.rows.length,
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la récupération des pays par région:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération des pays' 
    });
  }
});

module.exports = router;
