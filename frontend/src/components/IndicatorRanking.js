import './IndicatorRanking.css';

const IndicatorRanking = ({ data, selectedCountry }) => {
  if (!data || !data.data) return null;

  const { indicator, year, data: countries } = data;

  // Trouver la position du pays sélectionné
  const selectedCountryRank = selectedCountry 
    ? countries.findIndex(c => c.country_code === selectedCountry.iso3) + 1 
    : null;

  const formatValue = (value) => {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    } else {
      return value.toFixed(2);
    }
  };

  const getValueColor = (index) => {
    const ratio = index / countries.length;
    if (ratio < 0.33) return '#2d8a56'; // Institutional green
    if (ratio < 0.66) return '#b8860b'; // Institutional amber
    return '#9b2c2c'; // Institutional red
  };

  // Trouver la valeur max pour normaliser les barres
  const maxValue = Math.max(...countries.map(c => c.value));
  const minValue = Math.min(...countries.map(c => c.value));

  return (
    <div className="indicator-ranking">
      <div className="ranking-header">
        <h3>{indicator.name}</h3>
        <div className="ranking-meta">
          <span className="ranking-year">Année: {year}</span>
          <span className="ranking-unit">{indicator.unit}</span>
        </div>
      </div>

      {selectedCountry && selectedCountryRank && (
        <div className="selected-country-banner">
          <span className="banner-text">
            <strong>{selectedCountry.name}</strong> — classé #{selectedCountryRank} sur {countries.length} pays
          </span>
        </div>
      )}

      <div className="ranking-list">
        {countries.map((country, index) => {
          const isSelected = selectedCountry && country.country_code === selectedCountry.iso3;
          const rank = index + 1;
          
          return (
            <div 
              key={country.country_code} 
              className={`ranking-item ${isSelected ? 'selected' : ''}`}
            >
              <div className="ranking-position">
                <span className={`rank-number ${rank <= 3 ? `top-${rank}` : ''}`}>#{rank}</span>
              </div>

              <div className="country-info">
                <span className="country-name">{country.country_name}</span>
                <span className="country-region">{country.region}</span>
              </div>

              <div className="value-container">
                <div 
                  className="value-bar" 
                  style={{
                    width: `${((country.value - minValue) / (maxValue - minValue)) * 100}%`,
                    backgroundColor: getValueColor(index)
                  }}
                />
                <span className="value-text" style={{ color: getValueColor(index) }}>
                  {formatValue(country.value)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default IndicatorRanking;
