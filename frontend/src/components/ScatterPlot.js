import { useEffect, useRef, useState } from 'react';
import './ScatterPlot.css';

const ScatterPlot = ({ data, width = 800, height = 500 }) => {
  const canvasRef = useRef(null);
  const [hoveredCountry, setHoveredCountry] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [growthRange, setGrowthRange] = useState({ min: 0, max: 0 });

  useEffect(() => {
    if (!data || data.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Marges
    const margin = { top: 40, right: 40, bottom: 60, left: 70 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    // Effacer le canvas
    ctx.clearRect(0, 0, width, height);

    // Trouver les min/max pour les échelles
    const growthRates = data.map(d => parseFloat(d.growth_rate));
    const medianAges = data.map(d => parseFloat(d.median_age));
    const populations = data.map(d => d.population);

    const minGrowth = Math.min(...growthRates);
    const maxGrowth = Math.max(...growthRates);
    const minAge = Math.min(...medianAges);
    const maxAge = Math.max(...medianAges);
    const maxPop = Math.max(...populations);

    // Sauvegarder la plage de croissance pour la légende
    setGrowthRange({ min: minGrowth, max: maxGrowth });

    // Ajouter une marge aux échelles
    const growthPadding = (maxGrowth - minGrowth) * 0.1;
    const agePadding = (maxAge - minAge) * 0.1;

    // Échelles
    const xScale = (value) => margin.left + ((value - (minGrowth - growthPadding)) / (maxGrowth - minGrowth + 2 * growthPadding)) * plotWidth;
    const yScale = (value) => height - margin.bottom - ((value - (minAge - agePadding)) / (maxAge - minAge + 2 * agePadding)) * plotHeight;
    const sizeScale = (value) => Math.sqrt(value / maxPop) * 40 + 3;

    // Dessiner la grille
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    
    // Lignes verticales
    for (let i = 0; i <= 10; i++) {
      const x = margin.left + (i / 10) * plotWidth;
      ctx.beginPath();
      ctx.moveTo(x, margin.top);
      ctx.lineTo(x, height - margin.bottom);
      ctx.stroke();
    }
    
    // Lignes horizontales
    for (let i = 0; i <= 10; i++) {
      const y = margin.top + (i / 10) * plotHeight;
      ctx.beginPath();
      ctx.moveTo(margin.left, y);
      ctx.lineTo(width - margin.right, y);
      ctx.stroke();
    }

    // Dessiner les axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    
    // Axe X
    ctx.beginPath();
    ctx.moveTo(margin.left, height - margin.bottom);
    ctx.lineTo(width - margin.right, height - margin.bottom);
    ctx.stroke();
    
    // Axe Y
    ctx.beginPath();
    ctx.moveTo(margin.left, margin.top);
    ctx.lineTo(margin.left, height - margin.bottom);
    ctx.stroke();

    // Labels des axes
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    
    // Label X
    ctx.fillText('Taux de croissance (%)', width / 2, height - 10);
    
    // Label Y
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Âge médian (années)', 0, 0);
    ctx.restore();

    // Titre
    ctx.font = 'bold 16px Arial';
    ctx.fillText('Croissance vs Âge médian par pays', width / 2, 20);

    // Échelle des axes
    ctx.font = '11px Arial';
    ctx.fillStyle = '#666';
    
    // Échelle X
    for (let i = 0; i <= 5; i++) {
      const value = minGrowth - growthPadding + (i / 5) * (maxGrowth - minGrowth + 2 * growthPadding);
      const x = margin.left + (i / 5) * plotWidth;
      ctx.textAlign = 'center';
      ctx.fillText(value.toFixed(1), x, height - margin.bottom + 20);
    }
    
    // Échelle Y
    for (let i = 0; i <= 5; i++) {
      const value = minAge - agePadding + (i / 5) * (maxAge - minAge + 2 * agePadding);
      const y = height - margin.bottom - (i / 5) * plotHeight;
      ctx.textAlign = 'right';
      ctx.fillText(value.toFixed(0), margin.left - 10, y + 4);
    }

    // Fonction pour calculer la couleur en dégradé basée sur le taux de croissance
    const getGradientColor = (growthRate) => {
      // Normaliser le taux de croissance entre le min et le max des données
      const normalized = Math.max(0, Math.min(1, (growthRate - minGrowth) / (maxGrowth - minGrowth)));
      
      let r, g, b;
      
      if (normalized < 0.5) {
        // De rouge institutionnel à ambre (min à médiane)
        const t = normalized * 2;
        r = Math.round(155 + (184 - 155) * t);
        g = Math.round(44 + (134 - 44) * t);
        b = Math.round(44 + (11 - 44) * t);
      } else {
        // De ambre à vert institutionnel (médiane à max)
        const t = (normalized - 0.5) * 2;
        r = Math.round(184 - (184 - 45) * t);
        g = Math.round(134 + (138 - 134) * t);
        b = Math.round(11 + (86 - 11) * t);
      }
      
      return `rgba(${r}, ${g}, ${b}, 0.65)`;
    };

    // Dessiner les points
    data.forEach(country => {
      const x = xScale(parseFloat(country.growth_rate));
      const y = yScale(parseFloat(country.median_age));
      const radius = sizeScale(country.population);

      // Couleur en dégradé basée sur le taux de croissance
      const growthRate = parseFloat(country.growth_rate);
      const color = getGradientColor(growthRate);

      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = hoveredCountry?.iso3 === country.iso3 ? '#000' : 'rgba(0, 0, 0, 0.3)';
      ctx.lineWidth = hoveredCountry?.iso3 === country.iso3 ? 3 : 1;
      ctx.stroke();
    });

  }, [data, width, height, hoveredCountry]);

  const handleMouseMove = (e) => {
    if (!data) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    setMousePos({ x: e.clientX, y: e.clientY });

    // Marges
    const margin = { top: 40, right: 40, bottom: 60, left: 70 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    // Échelles
    const growthRates = data.map(d => parseFloat(d.growth_rate));
    const medianAges = data.map(d => parseFloat(d.median_age));
    const populations = data.map(d => d.population);

    const minGrowth = Math.min(...growthRates);
    const maxGrowth = Math.max(...growthRates);
    const minAge = Math.min(...medianAges);
    const maxAge = Math.max(...medianAges);
    const maxPop = Math.max(...populations);

    const growthPadding = (maxGrowth - minGrowth) * 0.1;
    const agePadding = (maxAge - minAge) * 0.1;

    const xScale = (value) => margin.left + ((value - (minGrowth - growthPadding)) / (maxGrowth - minGrowth + 2 * growthPadding)) * plotWidth;
    const yScale = (value) => height - margin.bottom - ((value - (minAge - agePadding)) / (maxAge - minAge + 2 * agePadding)) * plotHeight;
    const sizeScale = (value) => Math.sqrt(value / maxPop) * 40 + 3;

    // Trouver le pays sous la souris
    let found = null;
    for (const country of data) {
      const x = xScale(parseFloat(country.growth_rate));
      const y = yScale(parseFloat(country.median_age));
      const radius = sizeScale(country.population);

      const distance = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2);
      if (distance <= radius) {
        found = country;
        break;
      }
    }

    setHoveredCountry(found);
  };

  const handleMouseLeave = () => {
    setHoveredCountry(null);
  };

  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <div className="scatter-plot-container">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="scatter-canvas"
      />
      {hoveredCountry && (
        <div 
          className="scatter-tooltip" 
          style={{ 
            left: mousePos.x + 15, 
            top: mousePos.y + 15 
          }}
        >
          <strong>{hoveredCountry.name}</strong>
          <div>Population: {formatNumber(hoveredCountry.population)}</div>
          <div>Croissance: {hoveredCountry.growth_rate}%</div>
          <div>Âge médian: {hoveredCountry.median_age} ans</div>
        </div>
      )}
      <div className="scatter-legend">
        <div className="legend-gradient">
          <div className="gradient-bar"></div>
          <div className="gradient-labels">
            <span>{growthRange.min.toFixed(1)}%</span>
            <span>{((growthRange.min + growthRange.max) / 2).toFixed(1)}%</span>
            <span>{growthRange.max.toFixed(1)}%</span>
          </div>
        </div>
        <div className="legend-text">Taux de croissance démographique (sur 10 ans)</div>
      </div>
    </div>
  );
};

export default ScatterPlot;
