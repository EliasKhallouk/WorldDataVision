import { useEffect, useState } from 'react';
import './App.css';
import CountryDetails from './components/CountryDetails';
import FilterPanel from './components/FilterPanel';
import IndicatorsDashboard from './components/IndicatorsDashboard';
import Legend from './components/Legend';
import ScatterPlot from './components/ScatterPlot';
import TimelinePlayer from './components/TimelinePlayer';
import WorldMap from './components/WorldMap';
import {
    getAgeGroups,
    getCountry,
    getDemographicStats,
    getGenderBalance,
    getLanguages,
    getPopulationPyramid,
    getPopulationSummary,
    getPopulationTrend,
    getScatterData,
    getSexCategories,
    getStats,
    getYears
} from './services/api';
import { calculateStats, formatCompactNumber } from './utils/helpers';

const InfoTooltip = ({ text }) => (
  <span className="info-tooltip" role="img" aria-label="Information">
    <svg className="info-icon" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <circle cx="8" cy="8" r="7" fill="none" stroke="var(--color-neutral-400)" strokeWidth="1.5"/>
      <text x="8" y="11.5" textAnchor="middle" fill="var(--color-neutral-400)" fontSize="10" fontWeight="600">i</text>
    </svg>
    <span className="tooltip-text">{text}</span>
  </span>
);

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
  const [demographicStats, setDemographicStats] = useState(null);
  const [genderBalance, setGenderBalance] = useState(null);
  const [scatterData, setScatterData] = useState([]);

  // Charger les métadonnées au démarrage
  useEffect(() => {
    loadMetadata();
    loadGlobalStats();
  }, []);

  // Charger les données de population quand les filtres changent
  useEffect(() => {
    if (selectedYear) {
      loadPopulationData();
      loadDemographicStats();
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

  const loadDemographicStats = async () => {
    try {
      const [demoData, genderData, scatterDataResponse] = await Promise.all([
        getDemographicStats({
          year: selectedYear,
          sex: selectedSex,
          language: selectedLanguage !== 'ALL' ? selectedLanguage : undefined
        }),
        getGenderBalance({
          year: selectedYear,
          language: selectedLanguage !== 'ALL' ? selectedLanguage : undefined
        }),
        getScatterData({
          year: selectedYear,
          language: selectedLanguage !== 'ALL' ? selectedLanguage : undefined
        })
      ]);

      setDemographicStats(demoData.data);
      setGenderBalance(genderData.data);
      setScatterData(scatterDataResponse.data || []);
    } catch (err) {
      console.error('Erreur lors du chargement des stats démographiques:', err);
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
              <h1>WorldDataVision</h1>
              <p className="header-subtitle">
                Plateforme d'analyse des données mondiales
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
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        <div className="top-row">
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
                    <strong>{stats.countriesWithData}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Population moyenne:</span>
                    <strong>{formatCompactNumber(stats.avg)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Population médiane:</span>
                    <strong>{formatCompactNumber(stats.median)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Pays le plus peuplé:</span>
                    <strong>{stats.maxCountry?.name || 'N/A'}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Population max:</span>
                    <strong>{formatCompactNumber(stats.max)}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Pays le moins peuplé:</span>
                    <strong>{stats.minCountry?.name || 'N/A'}</strong>
                  </div>
                  <div className="stat-row">
                    <span>Population min:</span>
                    <strong>{formatCompactNumber(stats.min)}</strong>
                  </div>
                  
                  {demographicStats && (
                    <>
                      <h3 className="stats-section-heading">Démographie</h3>
                      <div className="stat-row">
                        <span>% Population &lt; 15 ans:</span>
                        <strong>{demographicStats.pct_under_15}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>% Population &gt; 65 ans:</span>
                        <strong>{demographicStats.pct_over_65}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>% Population active (15-65):</span>
                        <strong>{demographicStats.pct_working_age}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Âge médian estimé:
                          <InfoTooltip text="Âge qui divise la population en deux groupes égaux. Indique si une population est jeune (<30 ans) ou âgée (>40 ans)." />
                        </span>
                        <strong>{demographicStats.median_age_estimated} ans</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Ratio dépendants/actifs:
                          <InfoTooltip text="Nombre de personnes dépendantes (enfants <15 ans + retraités >65 ans) pour 100 personnes en âge de travailler (15-65 ans). Important pour les systèmes de retraite." />
                        </span>
                        <strong>{demographicStats.dependency_ratio}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Ratio actifs/dépendants:
                          <InfoTooltip text="Nombre de personnes en âge de travailler pour chaque personne dépendante. C'est l'inverse du ratio précédent. Plus élevé = meilleur soutien économique." />
                        </span>
                        <strong>{demographicStats.active_inactive_ratio}</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Indice de vieillissement:
                          <InfoTooltip text="Nombre de personnes âgées (>65 ans) pour 100 jeunes (<15 ans). <100 = population jeune, >100 = population vieillissante." />
                        </span>
                        <strong>{demographicStats.aging_index}</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Indice de jeunesse:
                          <InfoTooltip text="Nombre de jeunes (<15 ans) pour 100 personnes âgées (>65 ans). >100 = population jeune, <100 = population vieillissante. C'est l'inverse de l'indice de vieillissement." />
                        </span>
                        <strong>{demographicStats.youth_index}</strong>
                      </div>
                    </>
                  )}

                  {genderBalance && (
                    <>
                      <h3 className="stats-section-heading">Équilibre H/F</h3>
                      <div className="stat-row">
                        <span>% Hommes:</span>
                        <strong>{genderBalance.pct_male}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>% Femmes:</span>
                        <strong>{genderBalance.pct_female}%</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Ratio H/F:
                          <InfoTooltip text="Nombre d'hommes pour 100 femmes. 100 = équilibre parfait, >100 = plus d'hommes, <100 = plus de femmes." />
                        </span>
                        <strong>{genderBalance.gender_ratio}</strong>
                      </div>
                      <div className="stat-row">
                        <span>
                          Indice d'équilibre:
                          <InfoTooltip text="Mesure de l'équilibre entre hommes et femmes. 100 = parfait équilibre, plus la valeur est basse, plus le déséquilibre est important." />
                        </span>
                        <strong>{genderBalance.gender_balance_index}</strong>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </div>

          <div className="content-column">
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

            {scatterData.length > 0 && (
              <ScatterPlot data={scatterData} width={1200} height={600} />
            )}

            <IndicatorsDashboard 
              selectedYear={selectedYear} 
              selectedCountry={selectedCountry}
            />
          </div>
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
