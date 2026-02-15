import { useEffect, useState } from 'react';
import './App.css';
import CountryDetails from './components/CountryDetails';
import FilterPanel from './components/FilterPanel';
import Legend from './components/Legend';
import TimelinePlayer from './components/TimelinePlayer';
import WorldMap from './components/WorldMap';
import {
  getAgeGroups,
  getCountry,
  getLanguages,
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
  const [ageGroups, setAgeGroups] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedSex, setSelectedSex] = useState('total');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState('ALL');
  const [selectedLanguage, setSelectedLanguage] = useState('ALL');
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
  }, [selectedYear, selectedSex, selectedAgeGroup, selectedLanguage]);

  const loadMetadata = async () => {
    try {
      const [yearsData, sexData, ageGroupsData, languagesData] = await Promise.all([
        getYears(),
        getSexCategories(),
        getAgeGroups(),
        getLanguages()
      ]);

      const yearsList = yearsData.data;
      setYears(yearsList);
      setSexCategories(sexData.data);
      setAgeGroups(ageGroupsData.data);
      setLanguages(languagesData.data);

      // Sélectionner 2024 par défaut, ou la dernière année si 2024 n'existe pas
      if (yearsList.length > 0) {
        const defaultYear = yearsList.includes(2024) ? 2024 : yearsList[yearsList.length - 1];
        setSelectedYear(defaultYear);
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
    // Ne pas activer le loading pour éviter le clignotement
    // Garder les anciennes données affichées pendant le chargement
    setError(null);

    try {
      const data = await getPopulationSummary({
        year: selectedYear,
        sex: selectedSex,
        ageGroup: selectedAgeGroup !== 'ALL' ? selectedAgeGroup : undefined,
        language: selectedLanguage !== 'ALL' ? selectedLanguage : undefined
      });

      setPopulationData(data.data);
      setLoading(false);
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError('Impossible de charger les données de population');
      setLoading(false);
    }
  };

  const handleCountryClick = async (country) => {
    try {
      setSelectedCountry(country);

      // Charger les données détaillées du pays depuis l'API
      const [countryDetails, trendData, pyramidData] = await Promise.all([
        getCountry(country.iso3),
        getPopulationTrend(country.iso3, { sex: selectedSex }),
        getPopulationPyramid(country.iso3, { year: selectedYear })
      ]);

      // Combiner les données de population avec les détails complets du pays
      const fullCountryData = {
        ...countryDetails.data,
        total_population: country.total_population
      };

      setSelectedCountry(fullCountryData);
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
          <div className="header-main">
            <div className="header-left">
              <h1>🌍 WorldDataVision</h1>
              <p className="header-subtitle">
                Visualisation interactive des données mondiales de population
              </p>
            </div>
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
              ageGroups={ageGroups}
              languages={languages}
              selectedYear={selectedYear}
              selectedSex={selectedSex}
              selectedAgeGroup={selectedAgeGroup}
              selectedLanguage={selectedLanguage}
              onYearChange={setSelectedYear}
              onSexChange={setSelectedSex}
              onAgeGroupChange={setSelectedAgeGroup}
              onLanguageChange={setSelectedLanguage}
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
          {years.length > 0 && selectedYear && (
            <TimelinePlayer
              years={years}
              selectedYear={selectedYear}
              onYearChange={setSelectedYear}
            />
          )}
          <WorldMap
            data={populationData}
            onCountryClick={handleCountryClick}
            selectedCountry={selectedCountry?.iso3}
          />
        </div>
      </main>

      {selectedCountry && (
        <CountryDetails
          country={selectedCountry}
          trend={countryTrend}
          pyramid={countryPyramid}
          selectedYear={selectedYear}
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
