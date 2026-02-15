import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { formatCompactNumber } from '../utils/helpers';
import './CountryDetails.css';

const CountryDetails = ({ country, trend, pyramid, selectedYear, onClose }) => {
  if (!country) return null;

  // Nettoyer et convertir les données de tendance
  const cleanTrend = trend && trend.length > 0 
    ? trend.map(item => ({
        ...item,
        year: parseInt(item.year, 10),
        total_population: parseInt(item.total_population, 10) || 0
      }))
    : [];

  // Nettoyer et convertir les données de pyramide
  const cleanPyramid = pyramid && pyramid.length > 0
    ? pyramid.map(item => ({
        ...item,
        male: parseInt(item.male, 10) || 0,
        female: parseInt(item.female, 10) || 0
      }))
    : [];

  return (
    <div className="country-details-overlay" onClick={onClose}>
      <div className="country-details" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="country-header">
          <div className="country-title">
            {country.flag && <span className="country-flag">{country.flag}</span>}
            <div>
              <h2>{country.name } {selectedYear && `(${selectedYear})`}</h2>
              {country.name_local && country.name_local !== country.name && (
                <p className="country-name-local">{country.name_local}</p>
              )}
            </div>
          </div>
          <p className="country-code">{country.iso2} / {country.iso3}</p>
        </div>

        <div className="country-info-grid">
          <div className="info-section">
            <h3>📍 Informations générales</h3>
            <div className="info-items">
              {country.continent && (
                <div className="info-item">
                  <span className="info-label">Continent:</span>
                  <span className="info-value">{country.continent}</span>
                </div>
              )}
              {country.region && (
                <div className="info-item">
                  <span className="info-label">Région:</span>
                  <span className="info-value">{country.region}</span>
                </div>
              )}
              {country.area_sq_km && (
                <div className="info-item">
                  <span className="info-label">Superficie:</span>
                  <span className="info-value">{parseInt(country.area_sq_km).toLocaleString()} km²</span>
                </div>
              )}
              {country.total_population && (
                <div className="info-item">
                  <span className="info-label">Population:</span>
                  <span className="info-value">{formatCompactNumber(country.total_population)}</span>
                </div>
              )}
              {country.is_independent !== null && (
                <div className="info-item">
                  <span className="info-label">Statut:</span>
                  <span className="info-value">{country.is_independent ? 'Indépendant' : 'Territoire'}</span>
                </div>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>🏛️ Capitale</h3>
            <div className="info-items">
              {country.capital && (
                <div className="info-item">
                  <span className="info-label">Ville:</span>
                  <span className="info-value">{country.capital}</span>
                </div>
              )}
              {country.capital_latitude && country.capital_longitude && (
                <div className="info-item">
                  <span className="info-label">Coordonnées:</span>
                  <span className="info-value">
                    {parseFloat(country.capital_latitude).toFixed(4)}°, {parseFloat(country.capital_longitude).toFixed(4)}°
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>💰 Devise</h3>
            <div className="info-items">
              {country.currency_name && (
                <div className="info-item">
                  <span className="info-label">Nom:</span>
                  <span className="info-value">{country.currency_name}</span>
                </div>
              )}
              {country.currency_code && (
                <div className="info-item">
                  <span className="info-label">Code:</span>
                  <span className="info-value">{country.currency_code} {country.currency_symbol || ''}</span>
                </div>
              )}
              {country.currency_local && country.currency_local !== country.currency_name && (
                <div className="info-item">
                  <span className="info-label">Nom local:</span>
                  <span className="info-value">{country.currency_local}</span>
                </div>
              )}
            </div>
          </div>

          {country.languages && country.languages.length > 0 && (
            <div className="info-section">
              <h3>🗣️ Langues</h3>
              <div className="info-items">
                <div className="info-item">
                  <span className="info-value languages-list">
                    {country.languages.map((lang, index) => (
                      <span key={lang.id} className="language-tag">
                        {lang.name}
                      </span>
                    ))}
                  </span>
                </div>
              </div>
            </div>
          )}

          {country.timezones && country.timezones.length > 0 && (
            <div className="info-section">
              <h3>🕐 Fuseaux horaires</h3>
              <div className="info-items">
                <div className="info-item">
                  <span className="info-value">
                    {country.timezones.join(', ')}
                  </span>
                </div>
              </div>
            </div>
          )}

          {country.borders && country.borders.length > 0 && (
            <div className="info-section">
              <h3>🗺️ Pays frontaliers</h3>
              <div className="info-items">
                <div className="info-item">
                  <span className="info-value">
                    {country.borders.join(', ')} ({country.borders.length})
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {cleanTrend.length > 0 && (
          <div className="chart-section">
            <h3>Évolution de la population</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cleanTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="year" 
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => value.toString()}
                />
                <YAxis 
                  tickFormatter={formatCompactNumber}
                  domain={[0, 'auto']}
                />
                <Tooltip 
                  formatter={(value) => formatCompactNumber(value)}
                  labelFormatter={(value) => `Année: ${value}`}
                  labelStyle={{ color: '#333' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="total_population" 
                  stroke="#4a90e2" 
                  strokeWidth={2}
                  name="Population"
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {cleanPyramid.length > 0 && (
          <div className="chart-section">
            <h3>Pyramide des âges</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart 
                data={cleanPyramid}
                layout="vertical"
                margin={{ left: 20, right: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={formatCompactNumber} />
                <YAxis dataKey="age_group" type="category" width={60} />
                <Tooltip formatter={(value) => formatCompactNumber(value)} />
                <Legend />
                <Bar dataKey="male" fill="#4a90e2" name="Hommes" />
                <Bar dataKey="female" fill="#e74c3c" name="Femmes" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default CountryDetails;
