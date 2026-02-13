import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { formatCompactNumber } from '../utils/helpers';
import './CountryDetails.css';

const CountryDetails = ({ country, trend, pyramid, onClose }) => {
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
          <h2>{country.name}</h2>
          <p className="country-code">{country.iso3}</p>
        </div>

        <div className="country-info">
          {country.region && (
            <div className="info-item">
              <span className="info-label">Région:</span>
              <span className="info-value">{country.region}</span>
            </div>
          )}
          {country.capital && (
            <div className="info-item">
              <span className="info-label">Capitale:</span>
              <span className="info-value">{country.capital}</span>
            </div>
          )}
          {country.total_population && (
            <div className="info-item">
              <span className="info-label">Population:</span>
              <span className="info-value">
                {formatCompactNumber(country.total_population)}
              </span>
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
