/**
 * Formate un nombre avec des séparateurs de milliers
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return 'N/A';
  return new Intl.NumberFormat('fr-FR').format(num);
};

/**
 * Formate un grand nombre en notation compacte (M pour millions, B pour milliards)
 */
export const formatCompactNumber = (num) => {
  // Gérer les cas invalides
  if (num === null || num === undefined || num === '') return 'N/A';
  
  // Convertir en nombre si c'est une chaîne
  const value = typeof num === 'string' ? parseFloat(num) : num;
  
  // Vérifier si c'est un nombre valide
  if (isNaN(value)) return 'N/A';
  
  if (value >= 1e9) {
    return (value / 1e9).toFixed(2) + ' Mds';
  } else if (value >= 1e6) {
    return (value / 1e6).toFixed(2) + ' M';
  } else if (value >= 1e3) {
    return (value / 1e3).toFixed(1) + ' K';
  }
  return formatNumber(value);
};

/**
 * Calcule une couleur basée sur une valeur et un range
 * Utilise une échelle logarithmique pour mieux visualiser les écarts importants
 */
export const getColorForValue = (value, min, max) => {
  if (value === null || value === undefined || value === 0) {
    return '#e0e0e0'; // Gris pour pas de données
  }

  // Utiliser une échelle logarithmique pour mieux répartir les couleurs
  // car les populations varient de ~10K à ~1.4 milliards
  const logMin = Math.log10(Math.max(min, 1));
  const logMax = Math.log10(Math.max(max, 1));
  const logValue = Math.log10(Math.max(value, 1));
  const normalized = (logValue - logMin) / (logMax - logMin);
  
  // Échelle de couleurs plus contrastée : jaune clair -> vert -> bleu -> violet foncé
  const colors = [
    { threshold: 0.0, color: '#ffffd4' },   // Très petit (jaune très clair)
    { threshold: 0.15, color: '#fee391' },  // Petit (jaune)
    { threshold: 0.3, color: '#fec44f' },   // Petit-moyen (orange clair)
    { threshold: 0.45, color: '#fe9929' },  // Moyen (orange)
    { threshold: 0.6, color: '#d95f0e' },   // Moyen-grand (orange foncé)
    { threshold: 0.75, color: '#993404' },  // Grand (marron)
    { threshold: 1.0, color: '#662506' }    // Très grand (marron très foncé)
  ];

  // Trouver la couleur appropriée
  for (let i = 0; i < colors.length - 1; i++) {
    if (normalized >= colors[i].threshold && normalized <= colors[i + 1].threshold) {
      return colors[i].color;
    }
  }

  return colors[colors.length - 1].color;
};

/**
 * Génère une échelle de légende avec distribution logarithmique
 */
export const generateLegendScale = (min, max, steps = 7) => {
  const scale = [];
  
  // Utiliser une échelle logarithmique pour la légende aussi
  const logMin = Math.log10(Math.max(min, 1));
  const logMax = Math.log10(Math.max(max, 1));
  const logStep = (logMax - logMin) / (steps - 1);
  
  for (let i = 0; i < steps; i++) {
    const logValue = logMin + (logStep * i);
    const value = Math.pow(10, logValue);
    scale.push({
      value,
      color: getColorForValue(value, min, max),
      label: formatCompactNumber(value)
    });
  }
  
  return scale;
};

/**
 * Convertit un code ISO3 en ISO2
 */
export const iso3ToIso2 = (iso3, countries) => {
  const country = countries.find(c => c.iso3 === iso3);
  return country ? country.iso2 : null;
};

/**
 * Trouve un pays par son code ISO
 */
export const findCountryByCode = (code, countries) => {
  return countries.find(c => 
    c.iso2 === code.toUpperCase() || 
    c.iso3 === code.toUpperCase()
  );
};

/**
 * Calcule les statistiques d'un dataset
 */
export const calculateStats = (data) => {
  if (!data || data.length === 0) {
    return { 
      min: 0, 
      max: 0, 
      avg: 0, 
      sum: 0,
      median: 0,
      countriesWithData: 0,
      maxCountry: null,
      minCountry: null
    };
  }

  const validData = data.filter(d => d.total_population > 0);
  const values = validData.map(d => d.total_population);
  const sum = values.reduce((a, b) => a + b, 0);
  
  // Trouver pays avec population max et min
  const maxCountry = validData.reduce((prev, current) => 
    (prev.total_population > current.total_population) ? prev : current
  , validData[0]);
  
  const minCountry = validData.reduce((prev, current) => 
    (prev.total_population < current.total_population) ? prev : current
  , validData[0]);
  
  // Calculer la médiane
  const sorted = [...values].sort((a, b) => a - b);
  const median = sorted.length % 2 === 0
    ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    : sorted[Math.floor(sorted.length / 2)];
  
  return {
    min: Math.min(...values),
    max: Math.max(...values),
    avg: sum / values.length,
    sum,
    median,
    countriesWithData: validData.length,
    maxCountry,
    minCountry
  };
};
