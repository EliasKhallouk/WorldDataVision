import { useEffect, useState } from 'react';
import './App.css';
import CountryDetails from './components/CountryDetails';
import FilterPanel from './components/FilterPanel';
import Legend from './components/Legend';
import WorldMap from './components/WorldMap';
import {
    getPopulationPyramid,
    getPopulationSummary,
    getPopulationTrend,
    getSexCategories,
    getStats,
    getYears
} from './services/api';
import { calculateStats, formatCompactNumber } from './utils/helpers';

function App() {
  const [populationData, setPopulationData] = useState([]);
  const [years, setYears] = useState([]);
  const [sexCategories, setSexCategories] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedSex, setSelectedSex] = useState('total');
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countryTrend, setCountryTrend] = useState([]);
  const [countryPyramid, setCountryPyramid] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [globalStats, setGlobalStats] = useState(null);

  // Charger les métadonnées au démarrage
  useEffect(() => {
    loadMetadata();
    loadGlobalStats();
  }, []);

  // Charger les données de population quand les filtres changent
  useEffect(() => {
    if (selectedYear) {
      loadPopulationData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedYear, selectedSex]);

  const loadMetadata = async () => {
    try {
      const [yearsData, sexData] = await Promise.all([
        getYears(),
        getSexCategories()
      ]);

      const yearsList = yearsData.data;
      setYears(yearsList);
      setSexCategories(sexData.data);

      // Sélectionner l'année la plus récente par défaut
      if (yearsList.length > 0) {
        setSelectedYear(yearsList[yearsList.length - 1]);
      }
    } catch (err) {
      console.error('Erreur lors du chargement des métadonnées:', err);
      setError('Impossible de charger les métadonnées');
    }
  };

  const loadGlobalStats = async () => {
    try {
      const statsData = await getStats();
      setGlobalStats(statsData.data);
    } catch (err) {
      console.error('Erreur lors du chargement des statistiques:', err);
    }
  };

  const loadPopulationData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getPopulationSummary({
        year: selectedYear,
        sex: selectedSex
      });

      setPopulationData(data.data);
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError('Impossible de charger les données de population');
    } finally {
      setLoading(false);
    }
  };

  const handleCountryClick = async (country) => {
    try {
      setSelectedCountry(country);

      // Charger les données détaillées du pays
      const [trendData, pyramidData] = await Promise.all([
        getPopulationTrend(country.iso3, { sex: selectedSex }),
        getPopulationPyramid(country.iso3, { year: selectedYear })
      ]);

      setCountryTrend(trendData.data);
      setCountryPyramid(pyramidData.data);
    } catch (err) {
      console.error('Erreur lors du chargement des détails du pays:', err);
    }
  };

  const handleCloseDetails = () => {
    setSelectedCountry(null);
    setCountryTrend([]);
    setCountryPyramid([]);
  };

  const stats = calculateStats(populationData);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🌍 WorldDataVision</h1>
          <p className="header-subtitle">
            Visualisation interactive des données mondiales de population
          </p>
          {globalStats && (
            <div className="global-stats">
              <div className="stat-item">
                <span className="stat-value">{globalStats.total_countries}</span>
                <span className="stat-label">Pays</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{globalStats.total_years}</span>
                <span className="stat-label">Années</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {formatCompactNumber(globalStats.total_data_points)}
                </span>
                <span className="stat-label">Points de données</span>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <div className="sidebar">
          {years.length > 0 && sexCategories.length > 0 && (
            <FilterPanel
              years={years}
              sexCategories={sexCategories}
              selectedYear={selectedYear}
              selectedSex={selectedSex}
              onYearChange={setSelectedYear}
              onSexChange={setSelectedSex}
            />
          )}

          {!loading && populationData.length > 0 && (
            <>
              <Legend min={stats.min} max={stats.max} />
              
              <div className="stats-panel">
                <h3>Statistiques</h3>
                <div className="stat-row">
                  <span>Population totale:</span>
                  <strong>{formatCompactNumber(stats.sum)}</strong>
                </div>
                <div className="stat-row">
                  <span>Pays avec données:</span>
                  <strong>{populationData.filter(d => d.total_population > 0).length}</strong>
                </div>
                <div className="stat-row">
                  <span>Population max:</span>
                  <strong>{formatCompactNumber(stats.max)}</strong>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="map-container">
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Chargement des données...</p>
            </div>
          ) : (
            <WorldMap
              data={populationData}
              onCountryClick={handleCountryClick}
              selectedCountry={selectedCountry?.iso3}
            />
          )}
        </div>
      </main>

      {selectedCountry && (
        <CountryDetails
          country={selectedCountry}
          trend={countryTrend}
          pyramid={countryPyramid}
          onClose={handleCloseDetails}
        />
      )}

      <footer className="app-footer">
        <p>
          Données issues de la base PostgreSQL WorldDataVision | 
          Carte basée sur <a 
            href="https://github.com/raphaellepuschitz/SVG-World-Map" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            SVG World Map
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
