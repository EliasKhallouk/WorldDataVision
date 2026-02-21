const pool = require('../config/database');

const WGI_CODES = ['VA.EST', 'PV.EST', 'GE.EST', 'RQ.EST', 'RL.EST', 'CC.EST'];

const GAUSSIAN_INDICATORS = {
  'SP.DYN.TFRT.IN': { optimal: 2.1, sigma: 0.8 },
  'SP.POP.GROW': { optimal: 0.9, sigma: 0.7 },
  'SP.POP.AG.MA.NO': { optimal: 35, sigma: 8 },
  'NY.GDP.MKTP.KD.ZG': { optimal: 3.5, sigma: 2.5 },
  'MS.MIL.XPND.GD.ZS': { optimal: 2.0, sigma: 1.5 },
  'BN.CAB.XOKA.GD.ZS': { optimal: 0.0, sigma: 5.0 }
};

const NEGATIVE_INDICATORS = new Set([
  'SP.DYN.IMRT.IN',
  'FP.CPI.TOTL.ZG',
  'GC.DOD.TOTL.GD.ZS',
  'DT.DOD.DECT.GN.ZS',
  'DT.TDS.DECT.EX.ZS',
  'EN.GHG.CO2.PC.CE.AR5',
  'ER.H2O.FWST.ZS',
  'EG.IMP.CONS.ZS',
  'TM.VAL.FOOD.ZS.UN',
  'NY.GDP.PETR.RT.ZS',
  'NY.GDP.NGAS.RT.ZS'
]);

const PILLARS = [
  {
    code: 'demography',
    weight: 0.25,
    subPillars: [
      {
        code: 'generation_balance',
        weight: 0.40,
        indicators: [
          { code: 'SP.POP.1564.TO.ZS', weight: 0.30 },
          { code: 'SP.POP.DPND', weight: 0.25 },
          { code: 'SP.POP.AG.MA.NO', weight: 0.20 },
          { code: 'SP.POP.0014.TO.ZS', weight: 0.15 },
          { code: 'SP.POP.65UP.TO.ZS', weight: 0.10 }
        ]
      },
      {
        code: 'demographic_dynamics',
        weight: 0.30,
        indicators: [
          { code: 'SP.DYN.TFRT.IN', weight: 0.35 },
          { code: 'SP.POP.GROW', weight: 0.25 },
          { code: 'SM.POP.NETM', weight: 0.20 },
          { code: 'SP.DYN.CBRT.IN', weight: 0.10 },
          { code: 'SP.DYN.CDRT.IN', weight: 0.10 }
        ]
      },
      {
        code: 'life_quality',
        weight: 0.20,
        indicators: [
          { code: 'SP.DYN.LE00.IN', weight: 0.70 },
          { code: 'SP.DYN.IMRT.IN', weight: 0.30 }
        ]
      },
      {
        code: 'urbanization',
        weight: 0.10,
        indicators: [
          { code: 'SP.URB.TOTL.IN.ZS', weight: 1.0 }
        ]
      }
    ]
  },
  {
    code: 'economy',
    weight: 0.20,
    subPillars: [
      {
        code: 'economic_development',
        weight: 0.35,
        indicators: [
          { code: 'NY.GDP.PCAP.PP.KD', weight: 0.60 },
          { code: 'NY.GDP.MKTP.KD.ZG', weight: 0.40 }
        ]
      },
      {
        code: 'macro_stability',
        weight: 0.30,
        indicators: [
          { code: 'FP.CPI.TOTL.ZG', weight: 0.40 },
          { code: 'BN.CAB.XOKA.GD.ZS', weight: 0.30 },
          { code: 'FI.RES.TOTL.MO', weight: 0.30 }
        ]
      },
      {
        code: 'fiscal_sustainability',
        weight: 0.20,
        indicators: [
          { code: 'GC.TAX.TOTL.GD.ZS', weight: 0.50 },
          { code: 'GC.DOD.TOTL.GD.ZS', weight: 0.30 },
          { code: 'DT.DOD.DECT.GN.ZS', weight: 0.20 }
        ]
      },
      {
        code: 'investment_openness',
        weight: 0.15,
        indicators: [
          { code: 'BX.KLT.DINV.WD.GD.ZS', weight: 0.60 },
          { code: 'DT.TDS.DECT.EX.ZS', weight: 0.40 }
        ]
      }
    ]
  },
  {
    code: 'governance',
    weight: 0.20,
    subPillars: [
      {
        code: 'institution_quality',
        weight: 0.60,
        indicators: [
          { code: 'RL.EST', weight: 0.20 },
          { code: 'CC.EST', weight: 0.20 },
          { code: 'GE.EST', weight: 0.20 },
          { code: 'RQ.EST', weight: 0.15 },
          { code: 'PV.EST', weight: 0.15 },
          { code: 'VA.EST', weight: 0.10 }
        ]
      },
      {
        code: 'defense_capacity',
        weight: 0.40,
        indicators: [
          { code: 'MS.MIL.XPND.GD.ZS', weight: 1.0 }
        ]
      }
    ]
  },
  {
    code: 'human_capital',
    weight: 0.15,
    subPillars: [
      {
        code: 'health',
        weight: 0.50,
        indicators: [
          { code: 'SH.XPD.CHEX.GD.ZS', weight: 0.35 },
          { code: 'SH.MED.PHYS.ZS', weight: 0.30 },
          { code: 'SH.MED.BEDS.ZS', weight: 0.20 },
          { code: 'SP.DYN.IMRT.IN', weight: 0.15 }
        ]
      },
      {
        code: 'education',
        weight: 0.50,
        indicators: [
          { code: 'SE.XPD.TOTL.GD.ZS', weight: 0.40 },
          { code: 'SE.TER.ENRR', weight: 0.35 },
          { code: 'SE.ADT.LITR.ZS', weight: 0.25 }
        ]
      }
    ]
  },
  {
    code: 'material_sovereignty',
    weight: 0.10,
    subPillars: [
      {
        code: 'energy_security',
        weight: 0.55,
        indicators: [
          { code: 'EG.ELC.ACCS.ZS', weight: 0.25 },
          { code: 'EG.USE.PCAP.KG.OE', weight: 0.20 },
          { code: 'EG.IMP.CONS.ZS', weight: 0.20 },
          { code: 'EG.FEC.RNEW.ZS', weight: 0.15 },
          { code: 'EG.ELC.PROD.KH', weight: 0.10 },
          { code: 'NY.GDP.PETR.RT.ZS', weight: 0.05 },
          { code: 'NY.GDP.NGAS.RT.ZS', weight: 0.05 }
        ]
      },
      {
        code: 'food_security',
        weight: 0.45,
        indicators: [
          { code: 'AG.PRD.FOOD.XD', weight: 0.25 },
          { code: 'AG.YLD.CREL.KG', weight: 0.20 },
          { code: 'TM.VAL.FOOD.ZS.UN', weight: 0.20 },
          { code: 'AG.LND.ARBL.HA.PC', weight: 0.15 },
          { code: 'ER.H2O.FWST.ZS', weight: 0.10 },
          { code: 'AG.LND.FRST.ZS', weight: 0.10 }
        ]
      }
    ]
  },
  {
    code: 'innovation',
    weight: 0.05,
    subPillars: [
      {
        code: 'rnd_capacity',
        weight: 0.40,
        indicators: [
          { code: 'GB.XPD.RSDV.GD.ZS', weight: 0.50 },
          { code: 'SP.POP.SCIE.RD.P6', weight: 0.30 },
          { code: 'IP.JRN.ARTC.SC', weight: 0.20 }
        ]
      },
      {
        code: 'tech_adoption',
        weight: 0.35,
        indicators: [
          { code: 'IT.NET.USER.ZS', weight: 0.40 },
          { code: 'IT.CEL.SETS.P2', weight: 0.30 },
          { code: 'IT.NET.BBND.P2', weight: 0.30 }
        ]
      },
      {
        code: 'productive_innovation',
        weight: 0.25,
        indicators: [
          { code: 'IP.PAT.RESD', weight: 0.50 },
          { code: 'TX.VAL.TECH.MF.ZS', weight: 0.50 }
        ]
      }
    ]
  },
  {
    code: 'environment',
    weight: 0.05,
    subPillars: [
      {
        code: 'sustainability',
        weight: 1.0,
        indicators: [
          { code: 'EN.GHG.CO2.PC.CE.AR5', weight: 0.70 },
          { code: 'AG.LND.TOTL.K2', weight: 0.30 }
        ]
      }
    ]
  }
];

const IRC_INDICATOR_CODE = 'IRC';

const clamp = (value, min = 0, max = 100) => Math.max(min, Math.min(max, value));

const gaussianScore = (value, optimal, sigma) => {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  const exponent = -Math.pow(value - optimal, 2) / (2 * Math.pow(sigma, 2));
  return clamp(100 * Math.exp(exponent));
};

const linearScore = (value, p025, p975, invert = false) => {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  if (p025 === null || p975 === null || p975 === p025) return 50;
  const raw = invert
    ? 100 * (p975 - value) / (p975 - p025)
    : 100 * (value - p025) / (p975 - p025);
  return clamp(raw);
};

const wgiScore = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) return null;
  return clamp((value + 2.5) * 20);
};

const flattenIndicatorCodes = () => {
  const codes = new Set();
  PILLARS.forEach(pillar => {
    pillar.subPillars.forEach(sub => {
      sub.indicators.forEach(ind => codes.add(ind.code));
    });
  });
  return Array.from(codes);
};

async function getDefaultYear() {
  const result = await pool.query(
    `SELECT indicator.code, MAX(iv.year) AS max_year
     FROM indicator_value iv
     JOIN indicator ON indicator.id = iv.indicator_id
     WHERE indicator.code = ANY($1)
     GROUP BY indicator.code`,
    [WGI_CODES]
  );

  if (result.rows.length === 0) return 2023;
  const minMax = result.rows.reduce((min, row) => {
    const year = parseInt(row.max_year, 10);
    return Number.isNaN(year) ? min : Math.min(min, year);
  }, Number.POSITIVE_INFINITY);

  return Number.isFinite(minMax) ? minMax : 2023;
}

async function ensureIndicator() {
  await pool.query(
    `INSERT INTO indicator_category (code, name, description)
     VALUES ('composite', 'Indices composites', 'Indices synthétiques calculés')
     ON CONFLICT (code) DO NOTHING`
  );

  const categoryResult = await pool.query(
    `SELECT id FROM indicator_category WHERE code = 'composite'`
  );

  const categoryId = categoryResult.rows[0]?.id;
  if (!categoryId) {
    throw new Error('Impossible de créer la catégorie composite');
  }

  await pool.query(
    `INSERT INTO indicator (code, name, description, unit, category_id, source)
     VALUES ($1, $2, $3, $4, $5, $6)
     ON CONFLICT (code) DO UPDATE
     SET name = EXCLUDED.name,
         description = EXCLUDED.description,
         unit = EXCLUDED.unit,
         category_id = EXCLUDED.category_id,
         source = EXCLUDED.source`,
    [
      IRC_INDICATOR_CODE,
      'Index de Résilience Civilisationnelle',
      'Score composite (0-100) basé sur 7 piliers et 74 indicateurs',
      'score (0-100)',
      categoryId,
      'WorldDataVision IRC'
    ]
  );
}

async function loadIndicatorIds(indicatorCodes) {
  const result = await pool.query(
    'SELECT id, code FROM indicator WHERE code = ANY($1)',
    [indicatorCodes]
  );
  const map = new Map(result.rows.map(row => [row.code, row.id]));
  return map;
}

async function loadIndicatorStats(year, indicatorCodes) {
  const result = await pool.query(
    `SELECT i.code,
            PERCENTILE_CONT(0.025) WITHIN GROUP (ORDER BY iv.value) AS p025,
            PERCENTILE_CONT(0.975) WITHIN GROUP (ORDER BY iv.value) AS p975,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY iv.value) AS median
     FROM indicator_value iv
     JOIN indicator i ON i.id = iv.indicator_id
     WHERE iv.year = $1 AND i.code = ANY($2)
     GROUP BY i.code`,
    [year, indicatorCodes]
  );

  const stats = new Map();
  result.rows.forEach(row => {
    stats.set(row.code, {
      p025: row.p025 === null ? null : Number(row.p025),
      p975: row.p975 === null ? null : Number(row.p975),
      median: row.median === null ? null : Number(row.median)
    });
  });
  return stats;
}

async function loadRegionMedians(year, indicatorCodes) {
  const result = await pool.query(
    `SELECT i.code,
            c.region,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY iv.value) AS median
     FROM indicator_value iv
     JOIN indicator i ON i.id = iv.indicator_id
     JOIN country c ON c.id = iv.country_id
     WHERE iv.year = $1 AND i.code = ANY($2)
     GROUP BY i.code, c.region`,
    [year, indicatorCodes]
  );

  const regionMedians = new Map();
  result.rows.forEach(row => {
    if (!regionMedians.has(row.code)) {
      regionMedians.set(row.code, new Map());
    }
    regionMedians.get(row.code).set(row.region || 'UNKNOWN', row.median === null ? null : Number(row.median));
  });
  return regionMedians;
}

async function loadIndicatorValues(year, indicatorCodes) {
  const result = await pool.query(
    `SELECT i.code, iv.country_id, iv.value
     FROM indicator_value iv
     JOIN indicator i ON i.id = iv.indicator_id
     WHERE iv.year = $1 AND i.code = ANY($2)`,
    [year, indicatorCodes]
  );

  const values = new Map();
  result.rows.forEach(row => {
    if (!values.has(row.country_id)) {
      values.set(row.country_id, new Map());
    }
    values.get(row.country_id).set(row.code, Number(row.value));
  });

  return values;
}

function getMissingRatio(valueMap, indicatorCodes) {
  let missing = 0;
  indicatorCodes.forEach(code => {
    if (!valueMap || !valueMap.has(code) || valueMap.get(code) === null) {
      missing += 1;
    }
  });
  return indicatorCodes.length === 0 ? 1 : missing / indicatorCodes.length;
}

function getImputedValue({ code, region, valueMap, regionMedians, stats, useRegional }) {
  if (valueMap && valueMap.has(code)) return valueMap.get(code);
  if (useRegional) {
    const regional = regionMedians.get(code)?.get(region || 'UNKNOWN');
    if (regional !== null && regional !== undefined) return regional;
  }
  const globalMedian = stats.get(code)?.median;
  return globalMedian === undefined ? null : globalMedian;
}

function computeIndicatorScore(code, value, stats) {
  if (value === null || value === undefined || Number.isNaN(value)) return null;

  if (WGI_CODES.includes(code)) {
    return wgiScore(value);
  }

  if (GAUSSIAN_INDICATORS[code]) {
    const { optimal, sigma } = GAUSSIAN_INDICATORS[code];
    return gaussianScore(value, optimal, sigma);
  }

  const indicatorStats = stats.get(code) || { p025: null, p975: null };
  return linearScore(value, indicatorStats.p025, indicatorStats.p975, NEGATIVE_INDICATORS.has(code));
}

function geometricMean(values, weights) {
  let product = 1;
  let weightSum = 0;

  values.forEach((value, idx) => {
    if (value === null || value === undefined || Number.isNaN(value)) return;
    const weight = weights[idx];
    product *= Math.pow(Math.max(value, 0.0001), weight);
    weightSum += weight;
  });

  if (weightSum === 0) return null;
  return Math.pow(product, 1 / weightSum);
}

async function main() {
  const yearArg = parseInt(process.argv[2], 10);
  const targetYear = Number.isNaN(yearArg) ? await getDefaultYear() : yearArg;

  console.log(`\n🚀 Calcul IRC pour l'année ${targetYear}...`);

  await ensureIndicator();

  const indicatorCodes = flattenIndicatorCodes();
  const indicatorIds = await loadIndicatorIds(indicatorCodes);
  const missingIndicators = indicatorCodes.filter(code => !indicatorIds.has(code));
  if (missingIndicators.length > 0) {
    console.warn(`⚠️  Indicateurs manquants dans la table indicator: ${missingIndicators.join(', ')}`);
  }

  const stats = await loadIndicatorStats(targetYear, indicatorCodes);
  const regionMedians = await loadRegionMedians(targetYear, indicatorCodes);
  const valuesByCountry = await loadIndicatorValues(targetYear, indicatorCodes);

  const countriesResult = await pool.query('SELECT id, iso3, region FROM country');
  const countries = countriesResult.rows;

  const ircIndicatorIdResult = await pool.query('SELECT id FROM indicator WHERE code = $1', [IRC_INDICATOR_CODE]);
  const ircIndicatorId = ircIndicatorIdResult.rows[0]?.id;
  if (!ircIndicatorId) {
    throw new Error('Indicateur IRC introuvable après insertion');
  }

  let inserted = 0;
  let skipped = 0;

  for (const country of countries) {
    const valueMap = valuesByCountry.get(country.id) || new Map();

    const pillarScores = new Map();
    let availablePillars = 0;

    for (const pillar of PILLARS) {
      const pillarIndicators = pillar.subPillars.flatMap(sub => sub.indicators.map(ind => ind.code));
      const missingRatio = getMissingRatio(valueMap, pillarIndicators);

      if (missingRatio > 0.30) {
        pillarScores.set(pillar.code, null);
        continue;
      }

      const useRegional = missingRatio <= 0.10;

      const subScores = [];
      const subWeights = [];

      for (const sub of pillar.subPillars) {
        const indicatorScores = [];
        const indicatorWeights = [];

        for (const ind of sub.indicators) {
          const rawValue = getImputedValue({
            code: ind.code,
            region: country.region,
            valueMap,
            regionMedians,
            stats,
            useRegional
          });

          const score = computeIndicatorScore(ind.code, rawValue, stats);
          if (score === null) continue;

          indicatorScores.push(score);
          indicatorWeights.push(ind.weight);
        }

        const subScore = geometricMean(indicatorScores, indicatorWeights);
        if (subScore !== null) {
          subScores.push(subScore);
          subWeights.push(sub.weight);
        }
      }

      if (subScores.length === 0) {
        pillarScores.set(pillar.code, null);
        continue;
      }

      const pillarScore = subScores.reduce((sum, score, idx) => sum + score * subWeights[idx], 0) / subWeights.reduce((a, b) => a + b, 0);
      pillarScores.set(pillar.code, pillarScore);
      availablePillars += 1;
    }

    if (availablePillars < 5) {
      skipped += 1;
      continue;
    }

    let ircScore = 0;
    let totalWeight = 0;

    for (const pillar of PILLARS) {
      const pillarScore = pillarScores.get(pillar.code);
      if (pillarScore === null || pillarScore === undefined) continue;
      ircScore += pillarScore * pillar.weight;
      totalWeight += pillar.weight;
    }

    if (totalWeight === 0) {
      skipped += 1;
      continue;
    }

    const finalScore = ircScore / totalWeight;

    await pool.query(
      `INSERT INTO indicator_value (country_id, indicator_id, year, value)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (country_id, indicator_id, year)
       DO UPDATE SET value = EXCLUDED.value`,
      [country.id, ircIndicatorId, targetYear, finalScore]
    );

    inserted += 1;
  }

  console.log(`✅ IRC calculé pour ${inserted} pays (ignorés: ${skipped}).`);
  console.log('🎯 Indicateur IRC ajouté dans la base.');
}

main()
  .catch(error => {
    console.error('❌ Erreur lors du calcul IRC:', error);
  })
  .finally(() => pool.end());
