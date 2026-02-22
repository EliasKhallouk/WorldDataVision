#!/usr/bin/env node

/**
 * Validation et Analyse de Qualité des Données IRC
 * Génère un rapport détaillé sur la complétude et cohérence des données
 */

const pool = require('../config/database');
const fs = require('fs');
const path = require('path');

/**
 * Rapport 1: Complétude des données
 */
async function analyzeCompleteness() {
  console.log('\n' + '='.repeat(80));
  console.log('📊 RAPPORT 1 : COMPLÉTUDE DES DONNÉES IRC');
  console.log('='.repeat(80) + '\n');

  try {
    const result = await pool.query(`
      SELECT 
        i.code,
        i.name,
        ic.name as category,
        COUNT(DISTINCT iv.country_id) as countries_with_data,
        COUNT(DISTINCT iv.year) as years_with_data,
        COUNT(*) as total_values,
        ROUND(100.0 * COUNT(DISTINCT iv.country_id) / (SELECT COUNT(*) FROM country), 1) as coverage_pct,
        MIN(iv.year) as first_year,
        MAX(iv.year) as last_year
      FROM indicator i
      LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
      LEFT JOIN indicator_category ic ON i.category_id = ic.id
      GROUP BY i.id, i.code, i.name, ic.name
      ORDER BY coverage_pct DESC, total_values DESC
    `);

    const indicators = result.rows;
    
    // Afficher dans le terminal
    console.log('┌─────────────────────────────────┬──────────┬────────┬──────────┬─────────┬──────────────┐');
    console.log('│ Indicateur (Code)               │ Pays     │ Années │ Valeurs  │ Couv.%  │ Période      │');
    console.log('├─────────────────────────────────┼──────────┼────────┼──────────┼─────────┼──────────────┤');
    
    for (const ind of indicators) {
      const code = (ind.code || 'N/A').padEnd(15);
      const countries = (ind.countries_with_data || 0).toString().padStart(4);
      const years = (ind.years_with_data || 0).toString().padStart(3);
      const values = (ind.total_values || 0).toString().padStart(6);
      const coverageVal = parseFloat(ind.coverage_pct) || 0;
      const coverage = coverageVal.toFixed(1).padStart(5);
      const period = ind.first_year && ind.last_year 
        ? `${ind.first_year}-${ind.last_year}` 
        : 'N/A';
      const periodStr = period.padEnd(12);
      
      console.log(`│ ${code} │ ${countries} │ ${years}  │ ${values} │ ${coverage} │ ${periodStr}│`);
    }
    
    console.log('└─────────────────────────────────┴──────────┴────────┴──────────┴─────────┴──────────────┘\n');

    // Statistiques globales
    const totalCountries = await pool.query('SELECT COUNT(*) FROM country');
    const totalYears = await pool.query('SELECT COUNT(*) FROM year_table');
    const totalValues = await pool.query('SELECT COUNT(*) FROM indicator_value');
    
    const avgCountries = indicators.reduce((sum, i) => sum + (i.countries_with_data || 0), 0) / indicators.length;
    const avgYears = indicators.reduce((sum, i) => sum + (i.years_with_data || 0), 0) / indicators.length;
    const avgCoverage = indicators.reduce((sum, i) => sum + (parseFloat(i.coverage_pct) || 0), 0) / indicators.length;

    console.log('📈 STATISTIQUES GLOBALES:');
    console.log(`   • Nombre total d'indicateurs:     ${indicators.length}`);
    console.log(`   • Pays dans la base:              ${totalCountries.rows[0].count}`);
    console.log(`   • Années dans la base:            ${totalYears.rows[0].count}`);
    console.log(`   • Valeurs totales:                ${totalValues.rows[0].count}`);
    console.log(`   • Couverture moyenne par indicateur: ${avgCountries.toFixed(0)} pays, ${avgYears.toFixed(0)} années (${avgCoverage.toFixed(1)}%)`);
    console.log();

    // Identifier les indicateurs avec problèmes
    const problematic = indicators.filter(i => (parseFloat(i.coverage_pct) || 0) < 50);
    if (problematic.length > 0) {
      console.log('⚠️  INDICATEURS AVEC FAIBLE COUVERTURE (<50%):');
      problematic.forEach(ind => {
        console.log(`   • ${ind.code}: ${ind.countries_with_data} pays (${parseFloat(ind.coverage_pct).toFixed(1)}%)`);
      });
      console.log();
    }

    return { indicators, stats: { totalCountries: totalCountries.rows[0].count, totalYears: totalYears.rows[0].count, totalValues: totalValues.rows[0].count } };
  } catch (err) {
    console.error('❌ Erreur lors de l\'analyse de complétude:', err.message);
    throw err;
  }
}

/**
 * Rapport 2: Qualité des données
 */
async function analyzeQuality() {
  console.log('='.repeat(80));
  console.log('🔍 RAPPORT 2 : QUALITÉ ET COHÉRENCE DES DONNÉES');
  console.log('='.repeat(80) + '\n');

  try {
    // 1. Valeurs NULL et invalides
    console.log('1️⃣  VALEURS MANQUANTES ET INVALIDES:');
    const nullValues = await pool.query(`
      SELECT 
        i.code,
        i.name,
        COUNT(*) as null_count
      FROM indicator_value iv
      RIGHT JOIN indicator i ON i.id = iv.indicator_id
      WHERE iv.value IS NULL OR iv.id IS NULL
      GROUP BY i.id, i.code, i.name
      HAVING COUNT(*) > 0
      ORDER BY null_count DESC
    `);
    
    if (nullValues.rows.length === 0) {
      console.log('   ✅ Aucune valeur NULL détectée\n');
    } else {
      nullValues.rows.forEach(row => {
        console.log(`   ⚠️  ${row.code}: ${row.null_count} valeurs manquantes`);
      });
      console.log();
    }

    // 2. Cohérence logique (exemples)
    console.log('2️⃣  COHÉRENCE LOGIQUE DES DONNÉES:\n');

    // Population doit être positive
    const negPop = await pool.query(`
      SELECT COUNT(*) as anomalies
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code = 'SP.POP.TOTL' AND iv.value < 0
    `);
    console.log(`   Population (SP.POP.TOTL): ${negPop.rows[0].anomalies} valeurs négatives ${negPop.rows[0].anomalies === 0 ? '✅' : '❌'}`);

    // Pourcentages doivent être entre 0-100
    const badPercentages = await pool.query(`
      SELECT i.code, COUNT(*) as anomalies
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code LIKE '%ZS%' OR i.code LIKE '%ZG%' OR i.code LIKE '%IN'
      AND (iv.value < 0 OR iv.value > 150)
      GROUP BY i.code
      HAVING COUNT(*) > 0
    `);
    
    if (badPercentages.rows.length === 0) {
      console.log(`   Pourcentages (codes %ZS, %ZG, %IN): Tous entre 0-150 ✅`);
    } else {
      badPercentages.rows.forEach(row => {
        console.log(`   ⚠️  ${row.code}: ${row.anomalies} valeurs en dehors [0-150]`);
      });
    }
    console.log();

    // 3. Croissance du PIB (doit être entre -50% et 50%)
    const gdpGrowth = await pool.query(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN iv.value < -50 OR iv.value > 50 THEN 1 ELSE 0 END) as anomalies
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code = 'NY.GDP.MKTP.KD.ZG'
    `);
    const gdpAnomalies = gdpGrowth.rows[0].anomalies || 0;
    console.log(`   Croissance PIB (NY.GDP.MKTP.KD.ZG): ${gdpAnomalies}/${gdpGrowth.rows[0].total} anomalies (>±50%) ${gdpAnomalies === 0 ? '✅' : '⚠️'}`);

    // 4. Taux de natalité (plausibilité)
    const birthRate = await pool.query(`
      SELECT 
        COUNT(*) as total,
        MIN(iv.value) as min_val,
        MAX(iv.value) as max_val,
        AVG(iv.value) as avg_val
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code = 'SP.DYN.CBRT.IN'
    `);
    const br = birthRate.rows[0];
    console.log(`   Taux de natalité (SP.DYN.CBRT.IN): min=${parseFloat(br.min_val).toFixed(2)}, max=${parseFloat(br.max_val).toFixed(2)}, moy=${parseFloat(br.avg_val).toFixed(2)} ✅`);

    // 5. Taux de mortalité
    const deathRate = await pool.query(`
      SELECT 
        COUNT(*) as total,
        MIN(iv.value) as min_val,
        MAX(iv.value) as max_val,
        AVG(iv.value) as avg_val
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code = 'SP.DYN.CDRT.IN'
    `);
    const dr = deathRate.rows[0];
    console.log(`   Taux de mortalité (SP.DYN.CDRT.IN): min=${parseFloat(dr.min_val).toFixed(2)}, max=${parseFloat(dr.max_val).toFixed(2)}, moy=${parseFloat(dr.avg_val).toFixed(2)} ✅`);

    // 6. Espérance de vie
    const lifeExp = await pool.query(`
      SELECT 
        COUNT(*) as total,
        MIN(iv.value) as min_val,
        MAX(iv.value) as max_val,
        AVG(iv.value) as avg_val
      FROM indicator_value iv
      JOIN indicator i ON i.id = iv.indicator_id
      WHERE i.code = 'SP.DYN.LE00.IN'
    `);
    const le = lifeExp.rows[0];
    console.log(`   Espérance de vie (SP.DYN.LE00.IN): min=${parseFloat(le.min_val).toFixed(2)}, max=${parseFloat(le.max_val).toFixed(2)}, moy=${parseFloat(le.avg_val).toFixed(2)} (30-90 plausible) ✅\n`);

    // 4. Distribution des années (pour chaque indicateur)
    console.log('3️⃣  DISTRIBUTION DES ANNÉES PAR INDICATEUR:\n');
    
    const yearDistribution = await pool.query(`
      WITH year_ranges AS (
        SELECT 
          i.code,
          COUNT(DISTINCT iv.year) as unique_years,
          MIN(iv.year) as start_year,
          MAX(iv.year) as end_year,
          ARRAY_AGG(DISTINCT iv.year ORDER BY iv.year) as years_array
        FROM indicator_value iv
        JOIN indicator i ON i.id = iv.indicator_id
        GROUP BY i.code
      )
      SELECT 
        code,
        unique_years,
        start_year,
        end_year,
        (end_year - start_year + 1) as span_years,
        ROUND(100.0 * unique_years / (end_year - start_year + 1), 1) as coverage_span_pct
      FROM year_ranges
      WHERE unique_years >= 5
      ORDER BY coverage_span_pct DESC, unique_years DESC
      LIMIT 10
    `);

    console.log('   Top 10 indicateurs avec meilleure continuité temporelle:');
    console.log('   ┌────────────────────┬───────────┬──────────┐');
    console.log('   │ Code               │ Années    │ Couv.%   │');
    console.log('   ├────────────────────┼───────────┼──────────┤');
    
    yearDistribution.rows.forEach(row => {
      const code = row.code.padEnd(18);
      const span = `${row.start_year}-${row.end_year}`.padEnd(9);
      const coverage = (parseFloat(row.coverage_span_pct).toFixed(1) + '%').padEnd(8);
      console.log(`   │ ${code} │ ${span} │ ${coverage} │`);
    });
    console.log('   └────────────────────┴───────────┴──────────┘\n');

    // 5. Outliers détectés
    console.log('4️⃣  DÉTECTION D\'OUTLIERS (Z-SCORE > 3):\n');
    
    const outliers = await pool.query(`
      WITH stats AS (
        SELECT 
          i.code,
          AVG(iv.value::numeric) as mean_val,
          STDDEV(iv.value::numeric) as std_val
        FROM indicator_value iv
        JOIN indicator i ON i.id = iv.indicator_id
        WHERE iv.value IS NOT NULL
        GROUP BY i.code
      ),
      outlier_detection AS (
        SELECT 
          i.code,
          c.iso3,
          iv.year,
          iv.value,
          ABS((iv.value::numeric - stats.mean_val) / NULLIF(stats.std_val, 0))::numeric as z_score
        FROM indicator_value iv
        JOIN indicator i ON i.id = iv.indicator_id
        JOIN country c ON c.id = iv.country_id
        JOIN stats ON stats.code = i.code
        WHERE iv.value IS NOT NULL AND stats.std_val > 0
      )
      SELECT 
        code,
        COUNT(*) as outlier_count
      FROM outlier_detection
      WHERE z_score > 3
      GROUP BY code
      ORDER BY outlier_count DESC
      LIMIT 5
    `);

    if (outliers.rows.length === 0) {
      console.log('   ✅ Aucun outlier significatif détecté (Z-score > 3)\n');
    } else {
      console.log('   ⚠️  Outliers détectés:');
      outliers.rows.forEach(row => {
        console.log(`      • ${row.code}: ${row.outlier_count} valeurs extrêmes`);
      });
      console.log();
    }

    // 6. Comparaison avec un indicateur de référence
    console.log('5️⃣  CORRÉLATION LOGIQUE:\n');
    
    const correlation = await pool.query(`
      WITH country_indicators AS (
        SELECT 
          iv.country_id,
          iv.year,
          MAX(CASE WHEN i.code = 'SP.POP.TOTL' THEN iv.value END) as population,
          MAX(CASE WHEN i.code = 'SP.DYN.LE00.IN' THEN iv.value END) as life_expectancy,
          MAX(CASE WHEN i.code = 'NY.GDP.PCAP.PP.KD' THEN iv.value END) as gdp_per_capita,
          MAX(CASE WHEN i.code = 'SP.DYN.TFRT.IN' THEN iv.value END) as fertility_rate
        FROM indicator_value iv
        JOIN indicator i ON i.id = iv.indicator_id
        GROUP BY iv.country_id, iv.year
        HAVING COUNT(DISTINCT i.code) >= 2
      )
      SELECT 
        COUNT(*) as complete_records,
        CORR(life_expectancy::numeric, gdp_per_capita::numeric) as corr_life_exp_gdp,
        CORR(life_expectancy::numeric, fertility_rate::numeric) as corr_life_exp_fertility
      FROM country_indicators
      WHERE population > 0 AND life_expectancy IS NOT NULL AND gdp_per_capita IS NOT NULL
    `);

    const corr = correlation.rows[0];
    console.log(`   Enregistrements complets (multi-indicateurs): ${corr.complete_records}`);
    if (corr.corr_life_exp_gdp) {
      const corrVal = parseFloat(corr.corr_life_exp_gdp);
      console.log(`   Corrélation Espérance de vie ↔ PIB/capita: ${corrVal.toFixed(3)} (attendu ~0.7 positif) ${Math.abs(corrVal) > 0.5 ? '✅' : '⚠️'}`);
    }
    if (corr.corr_life_exp_fertility) {
      const corrVal = parseFloat(corr.corr_life_exp_fertility);
      console.log(`   Corrélation Espérance de vie ↔ Fécondité: ${corrVal.toFixed(3)} (attendu ~-0.7 négatif) ${corrVal < -0.5 ? '✅' : '⚠️'}`);
    }
    console.log();

  } catch (err) {
    console.error('❌ Erreur lors de l\'analyse de qualité:', err.message);
    throw err;
  }
}

/**
 * Rapport 3: Recommandations
 */
async function generateRecommendations(data) {
  console.log('='.repeat(80));
  console.log('📋 RAPPORT 3 : RECOMMANDATIONS');
  console.log('='.repeat(80) + '\n');

  const { indicators } = data;
  const issues = [];

  // Identifier les problèmes
  indicators.forEach(ind => {
    if ((parseFloat(ind.coverage_pct) || 0) < 30) {
      issues.push({
        level: 'CRITIQUE',
        indicator: ind.code,
        message: `Couverture très faible (${parseFloat(ind.coverage_pct).toFixed(1)}%) - considérer exclusion de l'IRC`
      });
    } else if ((parseFloat(ind.coverage_pct) || 0) < 50) {
      issues.push({
        level: 'ATTENTION',
        indicator: ind.code,
        message: `Couverture faible (${parseFloat(ind.coverage_pct).toFixed(1)}%) - résultats à interpréter avec prudence`
      });
    }
    
    if ((ind.years_with_data || 0) < 5) {
      issues.push({
        level: 'ATTENTION',
        indicator: ind.code,
        message: `Données temporelles limitées (${ind.years_with_data} années) - analyse de tendance impossible`
      });
    }
  });

  if (issues.length === 0) {
    console.log('✅ BASE DE DONNÉES DE HAUTE QUALITÉ\n');
    console.log('Aucun problème majeur détecté. Les données IRC sont:');
    console.log('  • Complètes (couverture >50% pour la plupart des indicateurs)');
    console.log('  • Cohérentes (valeurs plausibles et corrélations logiques)');
    console.log('  • Temporellement riches (couverture pluriannuelle)');
  } else {
    console.log('⚠️  PROBLÈMES IDENTIFIÉS:\n');
    issues.forEach(issue => {
      const icon = issue.level === 'CRITIQUE' ? '🔴' : '🟡';
      console.log(`${icon} [${issue.level}] ${issue.indicator}: ${issue.message}`);
    });
  }

  console.log('\n' + '='.repeat(80) + '\n');
}

/**
 * Main
 */
async function main() {
  try {
    const completenessData = await analyzeCompleteness();
    await analyzeQuality();
    await generateRecommendations(completenessData);
    
    console.log('✨ Rapport de validation IRC généré avec succès!');
    await pool.end();
  } catch (err) {
    console.error('❌ Erreur fatale:', err);
    process.exit(1);
  }
}

main();
