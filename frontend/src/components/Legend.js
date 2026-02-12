import { generateLegendScale } from '../utils/helpers';
import './Legend.css';

const Legend = ({ min, max, title = 'Population' }) => {
  const scale = generateLegendScale(min, max, 7);

  return (
    <div className="legend">
      <h3 className="legend-title">{title}</h3>
      <div className="legend-description">
        Échelle logarithmique
      </div>
      <div className="legend-scale">
        {scale.map((item, index) => (
          <div key={index} className="legend-item">
            <div 
              className="legend-color"
              style={{ backgroundColor: item.color }}
            />
            <span className="legend-label">{item.label}</span>
          </div>
        ))}
      </div>
      <div className="legend-note">
        <span className="legend-color no-data" />
        <span className="legend-label">Pas de données</span>
      </div>
    </div>
  );
};

export default Legend;
