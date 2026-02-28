import { useEffect, useMemo, useState } from 'react';
import {
    getIndicatorComparison,
    getIndicatorEvolution,
    getYears
} from '../services/api';
import './IRCVisualizations.css';
import IndicatorChart from './IndicatorChart';
import IndicatorRanking from './IndicatorRanking';

const IRC_CODE = 'IRC';
const MIN_IRC_YEAR = 1996;

const IRCVisualizations = () => {
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(2022);
  const [rankingData, setRankingData] = useState(null);
  const [bottomRankingData, setBottomRankingData] = useState(null);
  const [evolutionData, setEvolutionData] = useState(null);
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [loadingRanking, setLoadingRanking] = useState(false);
  const [loadingEvolution, setLoadingEvolution] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadYears = async () => {
      try {
        const response = await getYears();
        const availableYears = (response?.data || [])
          .filter((year) => year >= MIN_IRC_YEAR)
          .sort((a, b) => b - a);
        setYears(availableYears);
        if (availableYears.length > 0) {
          setSelectedYear(availableYears.includes(2022) ? 2022 : availableYears[0]);
        }
      } catch (err) {
        console.error('Erreur lors du chargement des années IRC:', err);
        setError('Impossible de charger les années IRC');
      }
    };

    loadYears();
  }, []);

  useEffect(() => {
    if (!selectedYear) return;

    const loadRanking = async () => {
      setLoadingRanking(true);
      setError(null);
      try {
        // Charger Top 20
        const topData = await getIndicatorComparison(IRC_CODE, {
          year: selectedYear,
          limit: 20,
          sort: 'desc'
        });
        setRankingData(topData);

        // Charger Bottom 20
        const bottomData = await getIndicatorComparison(IRC_CODE, {
          year: selectedYear,
          limit: 20,
          sort: 'asc'
        });
        setBottomRankingData(bottomData);

        if (topData?.data?.length > 0) {
          const defaultSelection = topData.data
            .slice(0, 5)
            .map((country) => country.country_code);
          setSelectedCountries((prev) => (prev.length > 0 ? prev : defaultSelection));
        } else {
          setSelectedCountries([]);
        }
      } catch (err) {
        console.error('Erreur lors du chargement du classement IRC:', err);
        setError('Impossible de charger le classement IRC pour cette année');
        setRankingData(null);
        setBottomRankingData(null);
        setSelectedCountries([]);
      } finally {
        setLoadingRanking(false);
      }
    };

    loadRanking();
  }, [selectedYear]);

  useEffect(() => {
    if (!selectedCountries.length) {
      setEvolutionData(null);
      return;
    }

    const loadEvolution = async () => {
      setLoadingEvolution(true);
      setError(null);
      try {
        const startYear = Math.max(MIN_IRC_YEAR, selectedYear - 15);
        // Si startYear === selectedYear (cas de 1996), on prend au moins 2 ans pour éviter les bugs graphiques
        const adjustedStartYear = startYear === selectedYear ? Math.max(MIN_IRC_YEAR, selectedYear - 1) : startYear;
        const data = await getIndicatorEvolution(IRC_CODE, {
          countries: selectedCountries.join(','),
          startYear: adjustedStartYear,
          endYear: selectedYear
        });
        setEvolutionData(data);
      } catch (err) {
        console.error('Erreur lors du chargement de l\'évolution IRC:', err);
        setError('Impossible de charger l\'évolution IRC');
        setEvolutionData(null);
      } finally {
        setLoadingEvolution(false);
      }
    };

    loadEvolution();
  }, [selectedCountries, selectedYear]);

  const coverage = rankingData?.data?.length || 0;

  const averageTopScore = useMemo(() => {
    if (!rankingData?.data?.length) return null;
    const total = rankingData.data.reduce((sum, row) => sum + row.value, 0);
    return total / rankingData.data.length;
  }, [rankingData]);

  const handleCountryToggle = (countryCode) => {
    setSelectedCountries((prev) => {
      if (prev.includes(countryCode)) {
        return prev.filter((code) => code !== countryCode);
      }
      return [...prev, countryCode];
    });
  };

  return (
    <section className="irc-visualizations">
      <div className="irc-visualizations-header">
        <div>
          <h2>Indice de Résilience Civilisationnelle (IRC)</h2>
          <p className="irc-visualizations-subtitle">
            Visualisez l\'IRC calculé à partir des 74 indicateurs : classement, tendances et stabilité.
          </p>
        </div>
        <div className="irc-year-select">
          <label htmlFor="irc-year">Année</label>
          <select
            id="irc-year"
            value={selectedYear || ''}
            onChange={(event) => setSelectedYear(parseInt(event.target.value, 10))}
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="irc-error">{error}</div>}

      <div className="irc-summary-grid">
        <div className="irc-summary-card">
          <span className="label">Couverture pays</span>
          <span className="value">{coverage}</span>
        </div>
        <div className="irc-summary-card">
          <span className="label">Score moyen (Top 20)</span>
          <span className="value">{averageTopScore ? averageTopScore.toFixed(2) : '—'}</span>
        </div>
        <div className="irc-summary-card">
          <span className="label">Période de tendance</span>
          <span className="value">
            {selectedYear ? `${Math.max(MIN_IRC_YEAR, selectedYear - 15)}-${selectedYear}` : '—'}
          </span>
        </div>
      </div>

      <div className="irc-rankings-row">
        <div className="irc-panel">
          <div className="irc-panel-header">
            <h3>🏆 Top 20</h3>
            <span>Les plus résilients</span>
          </div>
          {rankingData && rankingData.data?.length > 0 ? (
            <IndicatorRanking data={rankingData} />
          ) : (
            <div className="irc-empty">Aucune donnée IRC pour cette année.</div>
          )}
        </div>

        <div className="irc-panel">
          <div className="irc-panel-header">
            <h3>⚠️ Flop 20</h3>
            <span>Les plus vulnérables</span>
          </div>
          {bottomRankingData && bottomRankingData.data?.length > 0 ? (
            <IndicatorRanking data={bottomRankingData} />
          ) : (
            <div className="irc-empty">Aucune donnée IRC pour cette année.</div>
          )}
        </div>
      </div>

      <div className="irc-panel irc-evolution-panel">
        <div className="irc-panel-header">
          <h3>📈 Évolution IRC - Comparaison</h3>
          <span>{loadingEvolution ? 'Chargement...' : `${selectedCountries.length} pays sélectionnés`}</span>
        </div>
        
        <div className="irc-country-selector-full">
          <div className="irc-selector-section">
            <h4>🏆 Top 20</h4>
            <div className="irc-country-chips">
              {rankingData?.data?.map((country) => (
                <label key={country.country_code} className="irc-country-chip">
                  <input
                    type="checkbox"
                    checked={selectedCountries.includes(country.country_code)}
                    onChange={() => handleCountryToggle(country.country_code)}
                  />
                  <span>{country.country_name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="irc-selector-section">
            <h4>⚠️ Flop 20</h4>
            <div className="irc-country-chips">
              {bottomRankingData?.data?.map((country) => (
                <label key={country.country_code} className="irc-country-chip">
                  <input
                    type="checkbox"
                    checked={selectedCountries.includes(country.country_code)}
                    onChange={() => handleCountryToggle(country.country_code)}
                  />
                  <span>{country.country_name}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {evolutionData && evolutionData.data?.length > 0 ? (
          <div className="irc-chart-container">
            <IndicatorChart data={evolutionData} />
          </div>
        ) : (
          <div className="irc-empty">Sélectionnez des pays ci-dessus pour voir leur évolution.</div>
        )}
      </div>
    </section>
  );
};

export default IRCVisualizations;
