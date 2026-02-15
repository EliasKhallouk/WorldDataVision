import React, { useCallback, useEffect, useRef, useState } from 'react';
import { getCountryMapping } from '../services/api';
import { getColorForValue } from '../utils/helpers';
import './WorldMap.css';

const WorldMap = ({ data, onCountryClick, onCountryHover, selectedCountry }) => {
  const [svgContent, setSvgContent] = useState(null);
  const [hoveredCountry, setHoveredCountry] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [iso2ToIso3, setIso2ToIso3] = useState({});
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const mapRef = useRef(null);
  const svgRef = useRef(null);
  const hasMovedRef = useRef(false);

  // Calculer min et max pour l'échelle de couleurs
  const stats = React.useMemo(() => {
    if (!data || data.length === 0) return { min: 0, max: 0 };
    const populations = data.map(d => d.total_population || 0).filter(p => p > 0);
    return {
      min: Math.min(...populations),
      max: Math.max(...populations)
    };
  }, [data]);

  // Charger le mapping ISO2 -> ISO3
  useEffect(() => {
    getCountryMapping()
      .then(response => {
        if (response.success) {
          setIso2ToIso3(response.data);
        }
      })
      .catch(err => console.error('Erreur lors du chargement du mapping ISO:', err));
  }, []);

  // Charger le SVG de la carte
  useEffect(() => {
    fetch('/world-map.svg')
      .then(res => res.text())
      .then(svg => setSvgContent(svg))
      .catch(err => console.error('Erreur lors du chargement de la carte SVG:', err));
  }, []);

  // Gérer le zoom avec la molette
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.min(Math.max(zoom * delta, 1), 10);
    setZoom(newZoom);
  }, [zoom]);

  // Gérer le début du drag
  const handleMouseDown = useCallback((e) => {
    setIsDragging(true);
    hasMovedRef.current = false;
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  }, [pan]);

  // Gérer le déplacement pendant le drag
  const handleMouseMoveMap = useCallback((e) => {
    if (isDragging) {
      hasMovedRef.current = true;
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  }, [isDragging, dragStart]);

  // Gérer la fin du drag
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Réinitialiser le zoom et pan
  const handleReset = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  // Zoom in/out avec boutons
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev * 1.3, 10));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev / 1.3, 1));
  }, []);

  // Appliquer les event listeners pour le drag
  useEffect(() => {
    const mapContainer = mapRef.current;
    if (!mapContainer) return;

    mapContainer.addEventListener('wheel', handleWheel, { passive: false });
    mapContainer.addEventListener('mousedown', handleMouseDown);
    mapContainer.addEventListener('mousemove', handleMouseMoveMap);
    mapContainer.addEventListener('mouseup', handleMouseUp);
    mapContainer.addEventListener('mouseleave', handleMouseUp);

    return () => {
      mapContainer.removeEventListener('wheel', handleWheel);
      mapContainer.removeEventListener('mousedown', handleMouseDown);
      mapContainer.removeEventListener('mousemove', handleMouseMoveMap);
      mapContainer.removeEventListener('mouseup', handleMouseUp);
      mapContainer.removeEventListener('mouseleave', handleMouseUp);
    };
  }, [handleWheel, handleMouseDown, handleMouseMoveMap, handleMouseUp]);

  // Appliquer la transformation au SVG
  useEffect(() => {
    if (!mapRef.current) return;
    const svg = mapRef.current.querySelector('svg');
    if (!svg) return;

    svgRef.current = svg;
    const g = svg.querySelector('g');
    if (g) {
      g.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`;
      g.style.transformOrigin = 'center';
    } else {
      svg.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`;
      svg.style.transformOrigin = 'center';
    }
  }, [zoom, pan]);

  // Appliquer les couleurs et les événements aux pays
  useEffect(() => {
    if (!svgContent || !mapRef.current || !data || Object.keys(iso2ToIso3).length === 0) return;

    const svg = mapRef.current.querySelector('svg');
    if (!svg) return;

    // Créer un mapping ISO3 -> données
    const dataMap = data.reduce((acc, item) => {
      acc[item.iso3] = item;
      return acc;
    }, {});

    // Mapping manuel des noms anglais du SVG vers codes ISO3
    const nameToIso3 = {
      'UNITED STATES': 'USA',
      'RUSSIA': 'RUS',
      'RUSSIAN FEDERATION': 'RUS',
      'CHINA': 'CHN',
      'INDIA': 'IND',
      'BRAZIL': 'BRA',
      'CANADA': 'CAN',
      'AUSTRALIA': 'AUS',
      'GERMANY': 'DEU',
      'UNITED KINGDOM': 'GBR',
      'FRANCE': 'FRA',
      'ITALY': 'ITA',
      'SPAIN': 'ESP',
      'MEXICO': 'MEX',
      'JAPAN': 'JPN',
      'SOUTH KOREA': 'KOR',
      'INDONESIA': 'IDN',
      'TURKEY': 'TUR',
      'SAUDI ARABIA': 'SAU',
      'ARGENTINA': 'ARG',
      'SOUTH AFRICA': 'ZAF',
      'EGYPT': 'EGY',
      'IRAN': 'IRN',
      'THAILAND': 'THA',
      'VIETNAM': 'VNM',
      'POLAND': 'POL',
      'UKRAINE': 'UKR',
      'ALGERIA': 'DZA',
      'SUDAN': 'SDN',
      'IRAQ': 'IRQ',
      'AFGHANISTAN': 'AFG',
      'MOROCCO': 'MAR',
      'PERU': 'PER',
      'MALAYSIA': 'MYS',
      'UZBEKISTAN': 'UZB',
      'VENEZUELA': 'VEN',
      'NEPAL': 'NPL',
      'YEMEN': 'YEM',
      'GHANA': 'GHA',
      'MOZAMBIQUE': 'MOZ',
      'TAIWAN': 'TWN',
      'AUSTRALIA': 'AUS',
      'SYRIA': 'SYR',
      'MADAGASCAR': 'MDG',
      'IVORY COAST': 'CIV',
      'CAMEROON': 'CMR',
      'NIGER': 'NER',
      'SRI LANKA': 'LKA',
      'BURKINA FASO': 'BFA',
      'MALI': 'MLI',
      'CHILE': 'CHL',
      'MALAWI': 'MWI',
      'ZAMBIA': 'ZMB',
      'GUATEMALA': 'GTM',
      'ECUADOR': 'ECU',
      'ZIMBABWE': 'ZWE',
      'GUINEA': 'GIN',
      'RWANDA': 'RWA',
      'BENIN': 'BEN',
      'BURUNDI': 'BDI',
      'TUNISIA': 'TUN',
      'BOLIVIA': 'BOL',
      'BELGIUM': 'BEL',
      'HAITI': 'HTI',
      'CUBA': 'CUB',
      'SOUTH SUDAN': 'SSD',
      'DOMINICAN REPUBLIC': 'DOM',
      'CZECH REPUBLIC': 'CZE',
      'GREECE': 'GRC',
      'JORDAN': 'JOR',
      'PORTUGAL': 'PRT',
      'AZERBAIJAN': 'AZE',
      'SWEDEN': 'SWE',
      'HONDURAS': 'HND',
      'UNITED ARAB EMIRATES': 'ARE',
      'HUNGARY': 'HUN',
      'TAJIKISTAN': 'TJK',
      'BELARUS': 'BLR',
      'AUSTRIA': 'AUT',
      'PAPUA NEW GUINEA': 'PNG',
      'SERBIA': 'SRB',
      'ISRAEL': 'ISR',
      'SWITZERLAND': 'CHE',
      'TOGO': 'TGO',
      'SIERRA LEONE': 'SLE',
      'LAOS': 'LAO',
      'NICARAGUA': 'NIC',
      'KYRGYZSTAN': 'KGZ',
      'EL SALVADOR': 'SLV',
      'TURKMENISTAN': 'TKM',
      'DENMARK': 'DNK',
      'SINGAPORE': 'SGP',
      'FINLAND': 'FIN',
      'CONGO': 'COG',
      'SLOVAKIA': 'SVK',
      'NORWAY': 'NOR',
      'OMAN': 'OMN',
      'COSTA RICA': 'CRI',
      'LIBERIA': 'LBR',
      'IRELAND': 'IRL',
      'CENTRAL AFRICAN REPUBLIC': 'CAF',
      'NEW ZEALAND': 'NZL',
      'MAURITANIA': 'MRT',
      'PANAMA': 'PAN',
      'KUWAIT': 'KWT',
      'CROATIA': 'HRV',
      'MOLDOVA': 'MDA',
      'GEORGIA': 'GEO',
      'ERITREA': 'ERI',
      'URUGUAY': 'URY',
      'BOSNIA AND HERZEGOVINA': 'BIH',
      'MONGOLIA': 'MNG',
      'ARMENIA': 'ARM',
      'JAMAICA': 'JAM',
      'QATAR': 'QAT',
      'ALBANIA': 'ALB',
      'PUERTO RICO': 'PRI',
      'LITHUANIA': 'LTU',
      'NAMIBIA': 'NAM',
      'GAMBIA': 'GMB',
      'BOTSWANA': 'BWA',
      'GABON': 'GAB',
      'LESOTHO': 'LSO',
      'NORTH MACEDONIA': 'MKD',
      'SLOVENIA': 'SVN',
      'GUINEA-BISSAU': 'GNB',
      'LATVIA': 'LVA',
      'BAHRAIN': 'BHR',
      'EQUATORIAL GUINEA': 'GNQ',
      'TRINIDAD AND TOBAGO': 'TTO',
      'ESTONIA': 'EST',
      'TIMOR-LESTE': 'TLS',
      'MAURITIUS': 'MUS',
      'CYPRUS': 'CYP',
      'ESWATINI': 'SWZ',
      'DJIBOUTI': 'DJI',
      'FIJI': 'FJI',
      'RÉUNION': 'REU',
      'COMOROS': 'COM',
      'GUYANA': 'GUY',
      'BHUTAN': 'BTN',
      'SOLOMON ISLANDS': 'SLB',
      'MACAO': 'MAC',
      'LUXEMBOURG': 'LUX',
      'MONTENEGRO': 'MNE',
      'WESTERN SAHARA': 'ESH',
      'SURINAME': 'SUR',
      'CABO VERDE': 'CPV',
      'MALDIVES': 'MDV',
      'MALTA': 'MLT',
      'BRUNEI': 'BRN',
      'GUADELOUPE': 'GLP',
      'BELIZE': 'BLZ',
      'BAHAMAS': 'BHS',
      'MARTINIQUE': 'MTQ',
      'ICELAND': 'ISL',
      'VANUATU': 'VUT',
      'FRENCH GUIANA': 'GUF',
      'BARBADOS': 'BRB',
      'NEW CALEDONIA': 'NCL',
      'FRENCH POLYNESIA': 'PYF',
      'MAYOTTE': 'MYT',
      'SAMOA': 'WSM',
      'SAINT LUCIA': 'LCA',
      'GUAM': 'GUM',
      'CURAÇAO': 'CUW',
      'GRENADA': 'GRD',
      'KIRIBATI': 'KIR',
      'MICRONESIA': 'FSM',
      'TONGA': 'TON',
      'SEYCHELLES': 'SYC',
      'ANTIGUA AND BARBUDA': 'ATG',
      'ISLE OF MAN': 'IMN',
      'ANDORRA': 'AND',
      'DOMINICA': 'DMA',
      'CAYMAN ISLANDS': 'CYM',
      'BERMUDA': 'BMU',
      'MARSHALL ISLANDS': 'MHL',
      'NORTHERN MARIANA ISLANDS': 'MNP',
      'GREENLAND': 'GRL',
      'AMERICAN SAMOA': 'ASM',
      'SAINT KITTS AND NEVIS': 'KNA',
      'FAROE ISLANDS': 'FRO',
      'SINT MAARTEN': 'SXM',
      'MONACO': 'MCO',
      'TURKS AND CAICOS ISLANDS': 'TCA',
      'SAINT MARTIN': 'MAF',
      'LIECHTENSTEIN': 'LIE',
      'SAN MARINO': 'SMR',
      'GIBRALTAR': 'GIB',
      'BRITISH VIRGIN ISLANDS': 'VGB',
      'CARIBBEAN NETHERLANDS': 'BES',
      'PALAU': 'PLW',
      'COOK ISLANDS': 'COK',
      'ANGUILLA': 'AIA',
      'TUVALU': 'TUV',
      'WALLIS AND FUTUNA': 'WLF',
      'NAURU': 'NRU',
      'SAINT BARTHÉLEMY': 'BLM',
      'SAINT PIERRE AND MIQUELON': 'SPM',
      'MONTSERRAT': 'MSR',
      'FALKLAND ISLANDS': 'FLK',
      'NIUE': 'NIU',
      'TOKELAU': 'TKL',
      'HOLY SEE': 'VAT',
      'DEM. REP. CONGO': 'COD',
      'DEMOCRATIC REPUBLIC OF THE CONGO': 'COD',
      'TANZANIA': 'TZA',
      'KENYA': 'KEN',
      'UGANDA': 'UGA',
      'ETHIOPIA': 'ETH',
      'ANGOLA': 'AGO',
      'SOMALIA': 'SOM',
      'NIGERIA': 'NGA',
      'CHAD': 'TCD',
      'LIBYA': 'LBY',
      'SENEGAL': 'SEN',
      'MAURITANIA': 'MRT',
      'PAKISTAN': 'PAK',
      'BANGLADESH': 'BGD',
      'MYANMAR': 'MMR',
      'PHILIPPINES': 'PHL',
      'CAMBODIA': 'KHM',
      'NORTH KOREA': 'PRK',
      'KAZAKHSTAN': 'KAZ',
      'MONGOLIA': 'MNG',
      'ROMANIA': 'ROU',
      'BULGARIA': 'BGR',
      'NETHERLANDS': 'NLD',
      'COLOMBIA': 'COL',
      'PARAGUAY': 'PRY'
    };

    // Appliquer les styles à chaque pays
    const paths = svg.querySelectorAll('path[id], g[id], path[class], g[class]');
    
    paths.forEach(element => {
      // Récupérer l'identifiant du pays (id ou class)
      let countryIdentifier = element.id || element.getAttribute('class') || '';
      countryIdentifier = countryIdentifier.toUpperCase();
      
      // Essayer de trouver le code ISO3
      let countryIso3 = iso2ToIso3[countryIdentifier] || nameToIso3[countryIdentifier];
      
      const countryData = countryIso3 ? dataMap[countryIso3] : null;

      if (countryData && countryData.total_population > 0) {
        const color = getColorForValue(
          countryData.total_population,
          stats.min,
          stats.max
        );
        element.style.fill = color;
        element.style.cursor = 'pointer';
      } else {
        element.style.fill = '#e0e0e0';
        element.style.cursor = 'default';
      }

      // Contour discret pour tous les pays
      element.style.stroke = '#fff';
      element.style.strokeWidth = '0.5';

      // Ajouter les événements
      element.addEventListener('mouseenter', (e) => handleMouseEnter(e, countryIso3, countryData));
      element.addEventListener('mousemove', handleMouseMove);
      element.addEventListener('mouseleave', handleMouseLeave);
      element.addEventListener('click', (e) => {
        if (!hasMovedRef.current) {
          handleClick(countryIso3, countryData);
        }
      });
    });

    // Nettoyage
    return () => {
      paths.forEach(element => {
        element.removeEventListener('mouseenter', handleMouseEnter);
        element.removeEventListener('mousemove', handleMouseMove);
        element.removeEventListener('mouseleave', handleMouseLeave);
        element.removeEventListener('click', handleClick);
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [svgContent, data, stats, selectedCountry, iso2ToIso3]);

  const handleMouseEnter = useCallback((e, countryId, countryData) => {
    if (countryData) {
      setHoveredCountry(countryData);
      if (onCountryHover) {
        onCountryHover(countryData);
      }
    }
    e.target.style.opacity = '0.8';
  }, [onCountryHover]);

  const handleMouseMove = useCallback((e) => {
    setTooltipPos({
      x: e.clientX + 10,
      y: e.clientY + 10
    });
  }, []);

  const handleMouseLeave = useCallback((e) => {
    setHoveredCountry(null);
    if (onCountryHover) {
      onCountryHover(null);
    }
    e.target.style.opacity = '1';
  }, [onCountryHover]);

  const handleClick = useCallback((countryId, countryData) => {
    if (countryData && onCountryClick) {
      onCountryClick(countryData);
    }
  }, [onCountryClick]);

  return (
    <div className="world-map-container">
      <div className="zoom-controls">
        <button 
          className="zoom-btn" 
          onClick={handleZoomIn}
          title="Zoom avant"
        >
          +
        </button>
        <button 
          className="zoom-btn" 
          onClick={handleZoomOut}
          title="Zoom arrière"
        >
          −
        </button>
        <button 
          className="zoom-btn" 
          onClick={handleReset}
          title="Réinitialiser"
        >
          ⟲
        </button>
        <span className="zoom-level">{Math.round(zoom * 100)}%</span>
      </div>
      <div 
        ref={mapRef}
        className="world-map"
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
      
      {hoveredCountry && (
        <div 
          className="map-tooltip"
          style={{
            left: `${tooltipPos.x}px`,
            top: `${tooltipPos.y}px`
          }}
        >
          <h4>{hoveredCountry.name}</h4>
          <p>
            <strong>Population:</strong>{' '}
            {new Intl.NumberFormat('fr-FR').format(hoveredCountry.total_population)}
          </p>
          {hoveredCountry.region && (
            <p><strong>Région:</strong> {hoveredCountry.region}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default WorldMap;
