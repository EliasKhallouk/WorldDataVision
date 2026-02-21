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
  const [countrySelectionMode, setCountrySelectionMode] = useState('top5'); // 'top5', 'flop5', 'custom'
  const [customCountries, setCustomCountries] = useState([]);
  const [availableCountries, setAvailableCountries] = useState([]);
  const [countrySearchTerm, setCountrySearchTerm] = useState('');
  const comparisonCountries = ['FRA', 'USA', 'DEU', 'GBR', 'JPN'];
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  // Charger les indicateurs
  useEffect(() => {
    loadIndicators();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Charger une seule fois au démarrage

  // Charger les données quand l'indicateur change
  useEffect(() => {
    console.log('🔄 useEffect déclenché - viewMode:', viewMode, 'selectedIndicator:', selectedIndicator?.code);
    if (selectedIndicator) {
      if (viewMode === 'ranking') {
        loadRankingData();
      } else {
        loadEvolutionData();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIndicator, selectedYear, viewMode, countrySelectionMode, customCountries]);

  const loadIndicators = async () => {
    try {
      setLoading(true);
      const data = await getIndicators();
      setIndicators(data);
      
      // Sélectionner le premier indicateur de la catégorie active par défaut
      const filtered = getFilteredIndicators(data);
      if (filtered.length > 0 && !selectedIndicator) {
        setSelectedIndicator(filtered[0]);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des indicateurs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredIndicators = (indicatorsList = indicators) => {
    let filtered = indicatorsList;
    
    // Filtrer par catégorie
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(ind => ind.category_code === selectedCategory);
    }
    
    // Filtrer par recherche
    if (searchTerm) {
      filtered = filtered.filter(ind =>
        ind.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ind.code.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  };

  const loadRankingData = async () => {
    if (!selectedIndicator) return;
    
    try {
      // Utiliser selectedYear s'il est dans la plage de l'indicateur, sinon last_year
      let year = selectedIndicator.last_year;
      if (selectedYear && selectedYear >= selectedIndicator.first_year && selectedYear <= selectedIndicator.last_year) {
        year = selectedYear;
      }
      
      console.log('🔍 Chargement ranking pour:', selectedIndicator.code, 'année:', year);
      
      const data = await getIndicatorComparison(selectedIndicator.code, {
        year: year,
        limit: 20
      });
      
      console.log('✅ Données ranking reçues:', data, 'nombre de pays:', data.data?.length);
      setRankingData(data);
    } catch (error) {
      console.error('❌ Erreur lors du chargement du classement:', error);
      setRankingData(null);
    }
  };

  const loadEvolutionData = async () => {
    if (!selectedIndicator) return;
    
    try {
      // Utiliser selectedYear s'il est dans la plage de l'indicateur, sinon last_year
      let endYear = selectedIndicator.last_year;
      if (selectedYear && selectedYear >= selectedIndicator.first_year && selectedYear <= selectedIndicator.last_year) {
        endYear = selectedYear;
      }
      
      const startYear = Math.max(selectedIndicator.first_year, endYear - 20);
      
      let countriesToLoad = [];
      
      if (countrySelectionMode === 'top5' || countrySelectionMode === 'flop5') {
        // Charger le classement pour obtenir les top 5 ou flop 5
        const rankingData = await getIndicatorComparison(selectedIndicator.code, {
          year: endYear,
          limit: 200 // Charger tous les pays
        });
        
        if (rankingData && rankingData.data && rankingData.data.length > 0) {
          if (countrySelectionMode === 'top5') {
            countriesToLoad = rankingData.data.slice(0, 5).map(c => c.country_code);
          } else {
            countriesToLoad = rankingData.data.slice(-5).reverse().map(c => c.country_code);
          }
          
          // Stocker les pays disponibles pour le mode custom
          setAvailableCountries(rankingData.data.map(c => ({
            code: c.country_code,
            name: c.country_name
          })));
        }
      } else {
        // Mode custom
        countriesToLoad = customCountries.slice(0, 5);
      }
      
      if (countriesToLoad.length === 0) {
        setEvolutionData(null);
        return;
      }
      
      const data = await getIndicatorEvolution(selectedIndicator.code, {
        countries: countriesToLoad.join(','),
        startYear: startYear,
        endYear: endYear
      });
      setEvolutionData(data);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'évolution:', error);
    }
  };

  // Descriptions enrichies pour certains indicateurs clés
  const indicatorDescriptions = {
    'SP.POP.TOTL': {
      description: 'Population totale estimée en milieu d\'année, incluant tous les résidents quelle que soit leur citoyenneté.',
      interpretation: 'Une population croissante peut indiquer un développement économique, tandis qu\'une population décroissante peut signaler des défis démographiques.'
    },
    'SP.DYN.TFRT.IN': {
      description: 'Nombre moyen d\'enfants qu\'une femme aurait au cours de sa vie reproductive.',
      interpretation: 'Un taux < 2.1 indique un vieillissement de la population. Un taux > 3 peut indiquer une population très jeune.'
    },
    'SP.DYN.LE00.IN': {
      description: 'Nombre d\'années qu\'un nouveau-né peut s\'attendre à vivre si les conditions de mortalité actuelles restent constantes.',
      interpretation: 'Un indicateur clé du niveau de santé et de développement d\'un pays.'
    },
    'NY.GDP.PCAP.PP.KD': {
      description: 'PIB par habitant ajusté pour la parité de pouvoir d\'achat (PPA) en dollars internationaux constants.',
      interpretation: 'Mesure le niveau de vie relatif entre les pays en tenant compte des différences de coût de la vie.'
    },
    'EN.ATM.CO2E.PC': {
      description: 'Émissions de dioxyde de carbone par habitant en tonnes métriques.',
      interpretation: 'Indicateur clé de l\'empreinte carbone et de l\'impact environnemental d\'un pays.'
    }
  };

  // Catégories avec icônes
  const categories = [
    { code: 'all', name: 'Tous', icon: '📊' },
    { code: 'demographic', name: 'Démographie', icon: '👥' },
    { code: 'agriculture', name: 'Agriculture', icon: '🌾' },
    { code: 'environment', name: 'Environnement', icon: '🌍' },
    { code: 'energy', name: 'Énergie', icon: '⚡' },
    { code: 'institutional', name: 'Gouvernance', icon: '🏛️' },
    { code: 'economy', name: 'Économie', icon: '💰' },
    { code: 'social', name: 'Social', icon: '📚' },
    { code: 'technology', name: 'Technologies', icon: '💻' }
  ];

  const filteredIndicators = getFilteredIndicators();

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    setShowSuggestions(true);
    setHighlightedIndex(-1);
  };

  const handleSelectIndicator = (indicator) => {
    setSelectedIndicator(indicator);
    setSearchTerm('');
    setShowSuggestions(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || filteredIndicators.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < filteredIndicators.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < filteredIndicators.length) {
          handleSelectIndicator(filteredIndicators[highlightedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setHighlightedIndex(-1);
        break;
      default:
        break;
    }
  };

  if (loading) {
    return <div className="loading">Chargement des indicateurs...</div>;
  }

  return (
    <div className="indicators-dashboard">
      <div className="dashboard-header">
        <h2>📊 Indicateurs de développement</h2>
        <p className="subtitle">75 indicateurs économiques, sociaux et environnementaux de la Banque Mondiale</p>
      </div>

      {/* Filtres par catégorie */}
      <div className="category-filters">
        {categories.map(cat => (
          <button
            key={cat.code}
            className={`category-btn ${selectedCategory === cat.code ? 'active' : ''}`}
            onClick={() => {
              setSelectedCategory(cat.code);
              setSearchTerm('');
              // Sélectionner le premier indicateur de la nouvelle catégorie
              const newFiltered = cat.code === 'all' 
                ? indicators 
                : indicators.filter(ind => ind.category_code === cat.code);
              if (newFiltered.length > 0) {
                setSelectedIndicator(newFiltered[0]);
              }
            }}
          >
            <span className="category-icon">{cat.icon}</span>
            <span className="category-name">{cat.name}</span>
            <span className="category-count">
              {cat.code === 'all' 
                ? indicators.length 
                : indicators.filter(ind => ind.category_code === cat.code).length}
            </span>
          </button>
        ))}
      </div>

      {/* Champ de recherche avec autocomplétion */}
      <div className="indicator-search-container">
        <div className="selected-indicator-display">
          {selectedIndicator && (
            <div className="current-indicator">
              <span className="current-label">Indicateur actuel:</span>
              <span className="current-name">{selectedIndicator.name}</span>
              <span className="current-code">({selectedIndicator.code})</span>
            </div>
          )}
        </div>
        
        <div className="search-autocomplete">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Rechercher un indicateur (nom ou code)..."
              value={searchTerm}
              onChange={handleSearchChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              className="autocomplete-input"
            />
            {searchTerm && (
              <button 
                className="clear-search"
                onClick={() => {
                  setSearchTerm('');
                  setShowSuggestions(false);
                }}
              >
                ✕
              </button>
            )}
          </div>

          {showSuggestions && filteredIndicators.length > 0 && (
            <div className="suggestions-dropdown">
              <div className="suggestions-header">
                {searchTerm 
                  ? `${filteredIndicators.length} résultat${filteredIndicators.length > 1 ? 's' : ''}` 
                  : `${filteredIndicators.length} indicateur${filteredIndicators.length > 1 ? 's' : ''} - ${categories.find(c => c.code === selectedCategory)?.name || 'Tous'}`
                }
              </div>
              <ul className="suggestions-list">
                {filteredIndicators.map((indicator, index) => (
                  <li
                    key={indicator.code}
                    className={`suggestion-item ${
                      index === highlightedIndex ? 'highlighted' : ''
                    } ${
                      selectedIndicator?.code === indicator.code ? 'selected' : ''
                    }`}
                    onClick={() => handleSelectIndicator(indicator)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                  >
                    <div className="suggestion-main">
                      <span className="suggestion-name">{indicator.name}</span>
                      <span className="suggestion-code">{indicator.code}</span>
                    </div>
                    <div className="suggestion-meta">
                      <span className="suggestion-category">
                        {categories.find(c => c.code === indicator.category_code)?.name || 'Autre'}
                      </span>
                      <span className="suggestion-period">
                        {indicator.first_year} - {indicator.last_year}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {showSuggestions && searchTerm && filteredIndicators.length === 0 && (
            <div className="suggestions-dropdown">
              <div className="no-results">
                Aucun indicateur trouvé pour "{searchTerm}"
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Carte d'information enrichie */}
      {selectedIndicator && (
        <div className="indicator-info-card">
          <div className="info-header">
            <h3>{selectedIndicator.name}</h3>
            <span className="indicator-code">{selectedIndicator.code}</span>
          </div>
          
          {indicatorDescriptions[selectedIndicator.code] && (
            <div className="info-body">
              <div className="info-section">
                <h4>📋 Description</h4>
                <p>{indicatorDescriptions[selectedIndicator.code].description}</p>
              </div>
              <div className="info-section">
                <h4>💡 Interprétation</h4>
                <p>{indicatorDescriptions[selectedIndicator.code].interpretation}</p>
              </div>
            </div>
          )}
          
          <div className="info-metadata">
            <div className="meta-item">
              <span className="meta-label">Unité</span>
              <span className="meta-value">{selectedIndicator.unit || 'N/A'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Source</span>
              <span className="meta-value">{selectedIndicator.source}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Pays couverts</span>
              <span className="meta-value">{selectedIndicator.country_count}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Période</span>
              <span className="meta-value">{selectedIndicator.first_year} - {selectedIndicator.last_year}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Points de données</span>
              <span className="meta-value">{selectedIndicator.value_count?.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

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

      {/* Sélection des pays pour l'évolution */}
      {viewMode === 'evolution' && (
        <div className="country-selection-panel">
          <div className="country-mode-buttons">
            <button
              className={`country-mode-btn ${countrySelectionMode === 'top5' ? 'active' : ''}`}
              onClick={() => setCountrySelectionMode('top5')}
            >
              🥇 Top 5
            </button>
            <button
              className={`country-mode-btn ${countrySelectionMode === 'flop5' ? 'active' : ''}`}
              onClick={() => setCountrySelectionMode('flop5')}
            >
              📉 Flop 5
            </button>
            <button
              className={`country-mode-btn ${countrySelectionMode === 'custom' ? 'active' : ''}`}
              onClick={() => setCountrySelectionMode('custom')}
            >
              ⚙️ Personnalisés
            </button>
          </div>

          {countrySelectionMode === 'custom' && availableCountries.length > 0 && (
            <div className="custom-countries-selector">
              <label>Sélectionner jusqu'à 5 pays :</label>
              
              {/* Pays sélectionnés */}
              {customCountries.length > 0 && (
                <div className="selected-countries-tags">
                  {customCountries.map(countryCode => {
                    const country = availableCountries.find(c => c.code === countryCode);
                    return (
                      <span key={countryCode} className="country-tag">
                        {country?.name || countryCode}
                        <button
                          className="remove-tag"
                          onClick={() => setCustomCountries(customCountries.filter(c => c !== countryCode))}
                          title="Retirer"
                        >
                          ×
                        </button>
                      </span>
                    );
                  })}
                </div>
              )}
              
              {/* Barre de recherche */}
              {customCountries.length < 5 && (
                <div className="country-search-box">
                  <input
                    type="text"
                    placeholder="Rechercher un pays..."
                    value={countrySearchTerm}
                    onChange={(e) => setCountrySearchTerm(e.target.value)}
                    className="country-search-input"
                  />
                  {countrySearchTerm && (
                    <button 
                      className="clear-country-search"
                      onClick={() => setCountrySearchTerm('')}
                    >
                      ✕
                    </button>
                  )}
                </div>
              )}
              
              {/* Résultats de recherche */}
              {countrySearchTerm && customCountries.length < 5 && (
                <div className="country-search-results">
                  {availableCountries
                    .filter(country => 
                      !customCountries.includes(country.code) &&
                      (country.name.toLowerCase().includes(countrySearchTerm.toLowerCase()) ||
                       country.code.toLowerCase().includes(countrySearchTerm.toLowerCase()))
                    )
                    .slice(0, 10)
                    .map(country => (
                      <div
                        key={country.code}
                        className="country-search-item"
                        onClick={() => {
                          setCustomCountries([...customCountries, country.code]);
                          setCountrySearchTerm('');
                        }}
                      >
                        <span className="country-name">{country.name}</span>
                        <span className="country-code">{country.code}</span>
                      </div>
                    ))}
                  {availableCountries.filter(country => 
                    !customCountries.includes(country.code) &&
                    (country.name.toLowerCase().includes(countrySearchTerm.toLowerCase()) ||
                     country.code.toLowerCase().includes(countrySearchTerm.toLowerCase()))
                  ).length === 0 && (
                    <div className="no-results">Aucun pays trouvé</div>
                  )}
                </div>
              )}
              
              <div className="selection-info">
                {customCountries.length} / 5 pays sélectionnés
              </div>
            </div>
          )}
        </div>
      )}

      {/* Contenu */}
      <div className="dashboard-content">
        {viewMode === 'ranking' && (
          rankingData ? (
            <>
              {console.log('🎯 Affichage ranking avec data:', rankingData)}
              <IndicatorRanking 
                data={rankingData} 
                selectedCountry={selectedCountry}
              />
            </>
          ) : (
            <div className="loading">Chargement du classement...</div>
          )
        )}
        
        {viewMode === 'evolution' && (
          evolutionData ? (
            <IndicatorChart 
              data={evolutionData}
              selectedCountry={selectedCountry}
            />
          ) : (
            <div className="loading">Chargement de l'évolution...</div>
          )
        )}
      </div>
    </div>
  );
};

export default IndicatorsDashboard;
