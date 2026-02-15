const express = require('express');
const router = express.Router();
const pool = require('../config/database');

/**
 * GET /api/indicators/categories
 * Récupère toutes les catégories d'indicateurs
 */
router.get('/categories', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        ic.id,
        ic.code,
        ic.name,
        ic.description,
        COUNT(i.id) as indicator_count
      FROM indicator_category ic
      LEFT JOIN indicator i ON i.category_id = ic.id
      GROUP BY ic.id, ic.code, ic.name, ic.description
      ORDER BY ic.name
    `);
    
    res.json(result.rows);
  } catch (error) {
    console.error('Erreur lors de la récupération des catégories:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

/**
 * GET /api/indicators
 * Récupère tous les indicateurs avec filtres optionnels
 * Query params:
 *   - category: code de la catégorie (economy, social, demographic, institutional, environment)
 */
router.get('/', async (req, res) => {
  try {
    const { category } = req.query;
    
    let query = `
      SELECT 
        i.id,
        i.code,
        i.name,
        i.description,
        i.unit,
        i.source,
        ic.code as category_code,
        ic.name as category_name,
        (SELECT COUNT(*) FROM indicator_value WHERE indicator_id = i.id) as value_count,
        (SELECT COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = i.id) as country_count,
        (SELECT MIN(year) FROM indicator_value WHERE indicator_id = i.id) as first_year,
        (SELECT MAX(year) FROM indicator_value WHERE indicator_id = i.id) as last_year
      FROM indicator i
      LEFT JOIN indicator_category ic ON ic.id = i.category_id
    `;
    
    const params = [];
    
    if (category) {
      query += ' WHERE ic.code = $1';
      params.push(category);
    }
    
    query += ' ORDER BY ic.name, i.name';
    
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Erreur lors de la récupération des indicateurs:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

/**
 * GET /api/indicators/:code
 * Récupère les détails d'un indicateur spécifique par son code
 */
router.get('/:code', async (req, res) => {
  try {
    const { code } = req.params;
    
    const result = await pool.query(`
      SELECT 
        i.id,
        i.code,
        i.name,
        i.description,
        i.unit,
        i.source,
        ic.code as category_code,
        ic.name as category_name,
        (SELECT COUNT(*) FROM indicator_value WHERE indicator_id = i.id) as value_count,
        (SELECT COUNT(DISTINCT country_id) FROM indicator_value WHERE indicator_id = i.id) as country_count,
        (SELECT MIN(year) FROM indicator_value WHERE indicator_id = i.id) as first_year,
        (SELECT MAX(year) FROM indicator_value WHERE indicator_id = i.id) as last_year
      FROM indicator i
      LEFT JOIN indicator_category ic ON ic.id = i.category_id
      WHERE i.code = $1
    `, [code]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'indicateur:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

/**
 * GET /api/indicators/:code/values
 * Récupère les valeurs d'un indicateur
 * Query params:
 *   - country: code ISO du pays (optionnel, plusieurs valeurs possibles séparées par des virgules)
 *   - year: année (optionnel, plusieurs valeurs possibles séparées par des virgules)
 *   - startYear: année de début (optionnel)
 *   - endYear: année de fin (optionnel)
 */
router.get('/:code/values', async (req, res) => {
  try {
    const { code } = req.params;
    const { country, year, startYear, endYear } = req.query;
    
    // Récupérer l'ID de l'indicateur
    const indicatorResult = await pool.query(
      'SELECT id FROM indicator WHERE code = $1',
      [code]
    );
    
    if (indicatorResult.rows.length === 0) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    const indicatorId = indicatorResult.rows[0].id;
    
    // Construire la requête dynamiquement
    let query = `
      SELECT 
        iv.year,
        iv.value,
        c.iso3 as country_code,
        c.name as country_name,
        c.region
      FROM indicator_value iv
      JOIN country c ON c.id = iv.country_id
      WHERE iv.indicator_id = $1
    `;
    
    const params = [indicatorId];
    let paramIndex = 2;
    
    // Filtrer par pays
    if (country) {
      const countries = country.split(',').map(c => c.trim());
      query += ` AND c.iso3 = ANY($${paramIndex})`;
      params.push(countries);
      paramIndex++;
    }
    
    // Filtrer par année(s) spécifique(s)
    if (year) {
      const years = year.split(',').map(y => parseInt(y.trim()));
      query += ` AND iv.year = ANY($${paramIndex})`;
      params.push(years);
      paramIndex++;
    }
    
    // Filtrer par plage d'années
    if (startYear) {
      query += ` AND iv.year >= $${paramIndex}`;
      params.push(parseInt(startYear));
      paramIndex++;
    }
    
    if (endYear) {
      query += ` AND iv.year <= $${paramIndex}`;
      params.push(parseInt(endYear));
      paramIndex++;
    }
    
    query += ' ORDER BY c.name, iv.year';
    
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Erreur lors de la récupération des valeurs:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

/**
 * GET /api/indicators/:code/comparison
 * Compare les valeurs d'un indicateur entre plusieurs pays pour une année donnée
 * Query params:
 *   - year: année (requis)
 *   - countries: codes ISO des pays séparés par des virgules (optionnel, tous par défaut)
 *   - limit: nombre maximum de pays à retourner (optionnel, par défaut 20)
 *   - sort: 'asc' ou 'desc' (optionnel, par défaut 'desc')
 */
router.get('/:code/comparison', async (req, res) => {
  try {
    const { code } = req.params;
    const { year, countries, limit = 20, sort = 'desc' } = req.query;
    
    if (!year) {
      return res.status(400).json({ error: 'Paramètre year requis' });
    }
    
    // Récupérer l'ID de l'indicateur
    const indicatorResult = await pool.query(
      'SELECT id, name, unit FROM indicator WHERE code = $1',
      [code]
    );
    
    if (indicatorResult.rows.length === 0) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    const { id: indicatorId, name, unit } = indicatorResult.rows[0];
    
    let query = `
      SELECT 
        c.iso3 as country_code,
        c.name as country_name,
        c.region,
        iv.value,
        iv.year
      FROM indicator_value iv
      JOIN country c ON c.id = iv.country_id
      WHERE iv.indicator_id = $1 AND iv.year = $2
    `;
    
    const params = [indicatorId, parseInt(year)];
    let paramIndex = 3;
    
    if (countries) {
      const countryList = countries.split(',').map(c => c.trim());
      query += ` AND c.iso3 = ANY($${paramIndex})`;
      params.push(countryList);
      paramIndex++;
    }
    
    const sortOrder = sort === 'asc' ? 'ASC' : 'DESC';
    query += ` ORDER BY iv.value ${sortOrder} LIMIT $${paramIndex}`;
    params.push(parseInt(limit));
    
    const result = await pool.query(query, params);
    
    res.json({
      indicator: {
        code,
        name,
        unit
      },
      year: parseInt(year),
      data: result.rows
    });
  } catch (error) {
    console.error('Erreur lors de la comparaison:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

/**
 * GET /api/indicators/:code/evolution
 * Récupère l'évolution d'un indicateur pour un ou plusieurs pays
 * Query params:
 *   - countries: codes ISO des pays séparés par des virgules (requis)
 *   - startYear: année de début (optionnel)
 *   - endYear: année de fin (optionnel)
 */
router.get('/:code/evolution', async (req, res) => {
  try {
    const { code } = req.params;
    const { countries, startYear, endYear } = req.query;
    
    if (!countries) {
      return res.status(400).json({ error: 'Paramètre countries requis' });
    }
    
    // Récupérer l'ID de l'indicateur
    const indicatorResult = await pool.query(
      'SELECT id, name, unit FROM indicator WHERE code = $1',
      [code]
    );
    
    if (indicatorResult.rows.length === 0) {
      return res.status(404).json({ error: 'Indicateur non trouvé' });
    }
    
    const { id: indicatorId, name, unit } = indicatorResult.rows[0];
    
    const countryList = countries.split(',').map(c => c.trim());
    
    let query = `
      SELECT 
        c.iso3 as country_code,
        c.name as country_name,
        iv.year,
        iv.value
      FROM indicator_value iv
      JOIN country c ON c.id = iv.country_id
      WHERE iv.indicator_id = $1 AND c.iso3 = ANY($2)
    `;
    
    const params = [indicatorId, countryList];
    let paramIndex = 3;
    
    if (startYear) {
      query += ` AND iv.year >= $${paramIndex}`;
      params.push(parseInt(startYear));
      paramIndex++;
    }
    
    if (endYear) {
      query += ` AND iv.year <= $${paramIndex}`;
      params.push(parseInt(endYear));
      paramIndex++;
    }
    
    query += ' ORDER BY c.name, iv.year';
    
    const result = await pool.query(query, params);
    
    // Organiser les données par pays
    const dataByCountry = {};
    result.rows.forEach(row => {
      if (!dataByCountry[row.country_code]) {
        dataByCountry[row.country_code] = {
          country_code: row.country_code,
          country_name: row.country_name,
          values: []
        };
      }
      dataByCountry[row.country_code].values.push({
        year: row.year,
        value: row.value
      });
    });
    
    res.json({
      indicator: {
        code,
        name,
        unit
      },
      data: Object.values(dataByCountry)
    });
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'évolution:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

module.exports = router;
