import { useEffect, useState } from 'react';
import { getIndicatorComparison, getIndicatorEvolution, getIndicators } from '../services/api';
import IndicatorChart from './IndicatorChart';
import IndicatorRanking from './IndicatorRanking';
import './IndicatorsDashboard.css';

const IndicatorsDashboard = ({ selectedYear, selectedCountry }) => {
  const [indicators, setIndicators] = useState([]);
  const [selectedIndicator, setSelectedIndicator] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('ranking'); // 'ranking' ou 'evolution'
  const [rankingData, setRankingData] = useState(null);
  const [evolutionData, setEvolutionData] = useState(null);
  const [comparisonCountries, setComparisonCountries] = useState(['FRA', 'USA', 'DEU', 'GBR', 'JPN']);
  const [loading, setLoading] = useState(true);

  // Charger les indicateurs
  useEffect(() => {
    loadIndicators();
  }, [selectedCategory]);

  // Charger les données quand l'indicateur change
  useEffect(() => {
    if (selectedIndicator) {
      if (viewMode === 'ranking') {
        loadRankingData();
      } else {
        loadEvolutionData();
      }
    }
  }, [selectedIndicator, selectedYear, viewMode, comparisonCountries]);

  const loadIndicators = async () => {
    try {
      setLoading(true);
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {};
      const data = await getIndicators(params);
      setIndicators(data);
      
      // Sélectionner le premier indicateur par défaut
      if (data.length > 0 && !selectedIndicator) {
        setSelectedIndicator(data[0]);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des indicateurs:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRankingData = async () => {
    if (!selectedIndicator || !selectedYear) return;
    
    try {
      const data = await getIndicatorComparison(selectedIndicator.code, {
        year: selectedYear,
        limit: 20
      });
      setRankingData(data);
    } catch (error) {
      console.error('Erreur lors du chargement du classement:', error);
    }
  };

  const loadEvolutionData = async () => {
    if (!selectedIndicator) return;
    
    try {
      const countries = selectedCountry ? [selectedCountry.iso3, ...comparisonCountries] : comparisonCountries;
      const uniqueCountries = [...new Set(countries)].slice(0, 5);
      
      const data = await getIndicatorEvolution(selectedIndicator.code, {
        countries: uniqueCountries.join(','),
        startYear: selectedYear ? selectedYear - 20 : undefined,
        endYear: selectedYear
      });
      setEvolutionData(data);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'évolution:', error);
    }
  };

  const categories = [
    { code: 'all', name: 'Tous les indicateurs', icon: '📊' },
    { code: 'economy', name: 'Économie', icon: '💰' },
    { code: 'social', name: 'Social', icon: '👥' },
    { code: 'demographic', name: 'Démographie', icon: '📈' },
    { code: 'institutional', name: 'Institutionnel', icon: '🏛️' }
  ];

  if (loading && indicators.length === 0) {
    return (
      <div className="indicators-dashboard">
        <div className="loading">Chargement des indicateurs...</div>
      </div>
    );
  }

  return (
    <div className="indicators-dashboard">
      <div className="dashboard-header">
        <h2>📊 Indicateurs de développement</h2>
        <p className="subtitle">Données économiques, sociales et institutionnelles</p>
      </div>

      {/* Filtres par catégorie */}
      <div className="category-filters">
        {categories.map(cat => (
          <button
            key={cat.code}
            className={`category-btn ${selectedCategory === cat.code ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat.code)}
          >
            <span className="category-icon">{cat.icon}</span>
            <span className="category-name">{cat.name}</span>
          </button>
        ))}
      </div>

      {/* Sélection de l'indicateur */}
      <div className="indicator-selector">
        <label htmlFor="indicator-select">Sélectionner un indicateur:</label>
        <select
          id="indicator-select"
          value={selectedIndicator?.code || ''}
          onChange={(e) => {
            const indicator = indicators.find(i => i.code === e.target.value);
            setSelectedIndicator(indicator);
          }}
        >
          {indicators.map(indicator => (
            <option key={indicator.code} value={indicator.code}>
              {indicator.name}
            </option>
          ))}
        </select>
        
        {selectedIndicator && (
          <div className="indicator-info">
            <span className="indicator-unit">Unité: {selectedIndicator.unit}</span>
            <span className="indicator-coverage">
              {selectedIndicator.country_count} pays • {selectedIndicator.first_year}-{selectedIndicator.last_year}
            </span>
          </div>
        )}
      </div>

      {/* Modes de visualisation */}
      <div className="view-modes">
        <button
          className={`view-mode-btn ${viewMode === 'ranking' ? 'active' : ''}`}
          onClick={() => setViewMode('ranking')}
        >
          🏆 Classement
        </button>
        <button
          className={`view-mode-btn ${viewMode === 'evolution' ? 'active' : ''}`}
          onClick={() => setViewMode('evolution')}
        >
          📈 Évolution
        </button>
      </div>

      {/* Contenu */}
      <div className="dashboard-content">
        {viewMode === 'ranking' && rankingData && (
          <IndicatorRanking 
            data={rankingData} 
            selectedCountry={selectedCountry}
          />
        )}
        
        {viewMode === 'evolution' && evolutionData && (
          <IndicatorChart 
            data={evolutionData}
            selectedCountry={selectedCountry}
          />
        )}
      </div>
    </div>
  );
};

export default IndicatorsDashboard;
