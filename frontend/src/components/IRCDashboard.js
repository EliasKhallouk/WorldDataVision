import axios from 'axios';
import { useEffect, useState } from 'react';
import './IRCDashboard.css';
import IndicatorChart from './IndicatorChart';
import IndicatorInfo from './IndicatorInfo';
import IndicatorRanking from './IndicatorRanking';

const IRCDashboard = () => {
  const [indicators, setIndicators] = useState([]);
  const [categories, setCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('demographic');
  const [selectedIndicator, setSelectedIndicator] = useState(null);
  const [viewMode, setViewMode] = useState('ranking'); // 'ranking' ou 'evolution'
  const [searchTerm, setSearchTerm] = useState('');

  // Mapping des codes de catégories vers leurs icônes et noms français
  const categoryConfig = {
    'demographic': { name: 'Démographie', icon: '👥', label: 'Démographie' },
    'agriculture': { name: 'Agriculture', icon: '🌾', label: 'Agriculture' },
    'environment': { name: 'Environnement', icon: '🌍', label: 'Environnement' },
    'energy': { name: 'Énergie', icon: '⚡', label: 'Énergie' },
    'institutional': { name: 'Institutionnel', icon: '🏛️', label: 'Gouvernance' },
    'economy': { name: 'Économie', icon: '📊', label: 'Économie' },
    'social': { name: 'Social', icon: '📚', label: 'Social' },
    'technology': { name: 'Technologie', icon: '💻', label: 'Technologies' }
  };

  useEffect(() => {
    loadIndicators();
  }, []);

  const loadIndicators = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/indicators');
      const allIndicators = response.data;
      setIndicators(allIndicators);
      
      // Grouper les indicateurs par catégorie
      const grouped = {};
      allIndicators.forEach(ind => {
        const catCode = ind.category_code;
        if (!grouped[catCode]) {
          grouped[catCode] = [];
        }
        grouped[catCode].push(ind);
      });
      setCategories(grouped);
      
      // Sélectionner le premier indicateur de la première catégorie
      if (allIndicators.length > 0 && !selectedIndicator) {
        setSelectedIndicator(allIndicators[0]);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des indicateurs:', error);
    }
  };

  const getCategoryIndicators = () => {
    return categories[selectedCategory] || [];
  };

  const getFilteredIndicators = () => {
    const categoryIndicators = getCategoryIndicators();
    if (!searchTerm) return categoryIndicators;
    
    return categoryIndicators.filter(ind =>
      ind.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ind.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const filteredIndicators = getFilteredIndicators();
  const currentCategory = categoryConfig[selectedCategory] || { name: 'Catégorie', icon: '📊', label: 'Catégorie' };

  return (
    <div className="irc-dashboard">
      <div className="irc-header">
        <h1>📊 Tableau de bord IRC - Indicateurs mondiaux</h1>
        <p className="irc-subtitle">
          75 indicateurs de développement issus de la Banque Mondiale
        </p>
      </div>

      {/* Navigation par catégories */}
      <div className="irc-categories">
        {Object.entries(categories).map(([catCode, catIndicators]) => {
          const config = categoryConfig[catCode] || { name: catCode, icon: '📊', label: catCode };
          return (
            <button
              key={catCode}
              className={`category-btn ${selectedCategory === catCode ? 'active' : ''}`}
              onClick={() => {
                setSelectedCategory(catCode);
                setSearchTerm('');
                // Sélectionner le premier indicateur de la nouvelle catégorie
                if (catIndicators.length > 0) {
                  setSelectedIndicator(catIndicators[0]);
                }
              }}
            >
              <span className="category-icon">{config.icon}</span>
              <span className="category-name">{config.label}</span>
              <span className="category-count">{catIndicators.length}</span>
            </button>
          );
        })}
      </div>

      {/* Barre de recherche et sélection */}
      <div className="irc-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder={`Rechercher parmi ${getCategoryIndicators().length} indicateurs ${currentCategory.name.toLowerCase()}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button 
              className="clear-search"
              onClick={() => setSearchTerm('')}
            >
              ✕
            </button>
          )}
        </div>

        <div className="indicator-selector">
          <label>Indicateur sélectionné :</label>
          <select
            value={selectedIndicator?.code || ''}
            onChange={(e) => {
              const ind = indicators.find(i => i.code === e.target.value);
              setSelectedIndicator(ind);
            }}
          >
            {filteredIndicators.map(ind => (
              <option key={ind.code} value={ind.code}>
                {ind.name}
              </option>
            ))}
          </select>
        </div>

        <div className="view-mode-selector">
          <button
            className={`mode-btn ${viewMode === 'ranking' ? 'active' : ''}`}
            onClick={() => setViewMode('ranking')}
          >
            🏆 Classement
          </button>
          <button
            className={`mode-btn ${viewMode === 'evolution' ? 'active' : ''}`}
            onClick={() => setViewMode('evolution')}
          >
            📈 Évolution
          </button>
        </div>
      </div>

      {/* Zone de visualisation */}
      <div className="irc-visualization">
        {selectedIndicator && <IndicatorInfo indicator={selectedIndicator} />}
        
        {selectedIndicator && viewMode === 'ranking' && (
          <IndicatorRanking 
            indicatorCode={selectedIndicator.code}
            indicatorName={selectedIndicator.name}
          />
        )}
        
        {selectedIndicator && viewMode === 'evolution' && (
          <IndicatorChart 
            indicatorCode={selectedIndicator.code}
            indicatorName={selectedIndicator.name}
          />
        )}
      </div>

      {/* Statistiques de la catégorie */}
      <div className="category-stats">
        <div className="stat-card">
          <div className="stat-value">{getCategoryIndicators().length}</div>
          <div className="stat-label">Indicateurs disponibles</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{filteredIndicators.length}</div>
          <div className="stat-label">Indicateurs affichés</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{currentCategory.icon}</div>
          <div className="stat-label">{currentCategory.label}</div>
        </div>
      </div>
    </div>
  );
};

export default IRCDashboard;
