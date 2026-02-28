import { useEffect, useRef } from 'react';
import './IndicatorChart.css';

const IndicatorChart = ({ data, selectedCountry }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (data && data.data && canvasRef.current) {
      drawChart();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, selectedCountry]);

  const drawChart = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (!data || !data.data || data.data.length === 0) return;

    const { indicator, data: countries } = data;
    
    // Marges
    const margin = { top: 40, right: 40, bottom: 60, left: 80 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // Trouver les min/max pour les axes
    let minYear = Infinity, maxYear = -Infinity;
    let minValue = Infinity, maxValue = -Infinity;

    countries.forEach(country => {
      country.values.forEach(v => {
        minYear = Math.min(minYear, v.year);
        maxYear = Math.max(maxYear, v.year);
        minValue = Math.min(minValue, v.value);
        maxValue = Math.max(maxValue, v.value);
      });
    });

    // Gérer le cas où il n'y a qu'une seule année (éviter division par zéro)
    if (minYear === maxYear) {
      minYear = minYear - 1;
      maxYear = maxYear + 1;
    }

    // Ajouter une marge aux valeurs
    const valueRange = maxValue - minValue;
    // Éviter division par zéro si toutes les valeurs sont identiques
    if (valueRange === 0) {
      minValue = minValue - 1;
      maxValue = maxValue + 1;
    } else {
      minValue = minValue - valueRange * 0.1;
      maxValue = maxValue + valueRange * 0.1;
    }

    // Fonctions de scale
    const scaleX = (year) => margin.left + ((year - minYear) / (maxYear - minYear)) * chartWidth;
    const scaleY = (value) => margin.top + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight;

    // Dessiner la grille
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    
    // Lignes horizontales
    for (let i = 0; i <= 5; i++) {
      const value = minValue + (maxValue - minValue) * (i / 5);
      const y = scaleY(value);
      
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(width - margin.right, y);
      ctx.stroke();

      // Labels Y
      ctx.fillStyle = '#718096';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(value.toFixed(1), margin.left - 10, y + 4);
    }

    // Lignes verticales
    const yearStep = Math.ceil((maxYear - minYear) / 10);
    for (let year = minYear; year <= maxYear; year += yearStep) {
      const x = scaleX(year);
      
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, height - margin.bottom);
      ctx.stroke();

      // Labels X
      ctx.fillStyle = '#718096';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(year, x, height - margin.bottom + 20);
    }

    // Couleurs pour chaque pays
    const colors = [
      '#2563a0', '#b8860b', '#2d8a56', '#9b2c2c', '#6b46a0',
      '#0e7490', '#92400e', '#4338a0', '#065f46', '#7c3aed'
    ];

    // Dessiner les lignes pour chaque pays
    countries.forEach((country, index) => {
      const color = colors[index % colors.length];
      const isSelected = selectedCountry && country.country_code === selectedCountry.iso3;
      
      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.setLineDash(isSelected ? [] : []);

      // Dessiner la ligne
      ctx.beginPath();
      country.values.forEach((point, i) => {
        const x = scaleX(point.year);
        const y = scaleY(point.value);
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();

      // Dessiner les points
      country.values.forEach(point => {
        const x = scaleX(point.year);
        const y = scaleY(point.value);
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, isSelected ? 5 : 3, 0, 2 * Math.PI);
        ctx.fill();
      });
    });

    // Titre des axes
    ctx.fillStyle = '#1a202c';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    
    // Axe X
    ctx.fillText('Année', width / 2, height - 10);
    
    // Axe Y (vertical)
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(indicator.unit, 0, 0);
    ctx.restore();
  };

  const handleMouseMove = (e) => {
    // Logique pour détecter les points survolés (désactivée pour l'instant)
  };

  return (
    <div className="indicator-chart">
      <div className="chart-header">
        <h3>{data.indicator.name}</h3>
        <p className="chart-subtitle">Évolution temporelle par pays</p>
      </div>

      <canvas
        ref={canvasRef}
        width={900}
        height={500}
        onMouseMove={handleMouseMove}
      />

      {/* Légende */}
      <div className="chart-legend">
        {[...data.data]
          .sort((a, b) => {
            // Trier par la dernière valeur IRC (décroissant)
            const valueA = a.values.length > 0 ? a.values[a.values.length - 1].value : 0;
            const valueB = b.values.length > 0 ? b.values[b.values.length - 1].value : 0;
            return valueB - valueA;
          })
          .map((country) => {
            const colors = [
              '#2563a0', '#b8860b', '#2d8a56', '#9b2c2c', '#6b46a0',
              '#0e7490', '#92400e', '#4338a0', '#065f46', '#7c3aed'
            ];
            // Trouver l'index original pour garder la même couleur
            const originalIndex = data.data.findIndex(c => c.country_code === country.country_code);
            const color = colors[originalIndex % colors.length];
            const isSelected = selectedCountry && country.country_code === selectedCountry.iso3;

            return (
              <div key={country.country_code} className={`legend-item ${isSelected ? 'selected' : ''}`}>
                <div 
                  className="legend-color" 
                  style={{ backgroundColor: color }}
                />
                <span className="legend-label">{country.country_name}</span>
                {country.values.length > 0 && (
                  <span className="legend-value">
                    {country.values[country.values.length - 1].value.toFixed(2)}
                  </span>
                )}
              </div>
            );
          })
        }
      </div>
    </div>
  );
};

export default IndicatorChart;
