import './IndicatorInfo.css';

const IndicatorInfo = ({ indicator }) => {
  if (!indicator) return null;

  // Mapping des codes vers des informations enrichies
  const indicatorDescriptions = {
    'SP.POP.TOTL': {
      description: 'Population totale estimée en milieu d\'année, incluant tous les résidents quelle que soit leur citoyenneté.',
      interpretation: 'Une population croissante peut indiquer un développement économique, tandis qu\'une population décroissante peut signaler des défis démographiques.'
    },
    'SP.DYN.TFRT.IN': {
      description: 'Nombre moyen d\'enfants qu\'une femme aurait au cours de sa vie reproductive.',
      interpretation: 'Un taux < 2.1 indique un vieillissement de la population. Un taux > 3 peut indiquer une population très jeune.'
    },
    'SP.DYN.LE00.IN': {
      description: 'Nombre d\'années qu\'un nouveau-né peut s\'attendre à vivre si les conditions de mortalité actuelles restent constantes.',
      interpretation: 'Un indicateur clé du niveau de santé et de développement d\'un pays.'
    },
    'NY.GDP.PCAP.PP.KD': {
      description: 'PIB par habitant ajusté pour la parité de pouvoir d\'achat (PPA) en dollars internationaux constants.',
      interpretation: 'Mesure le niveau de vie relatif entre les pays en tenant compte des différences de coût de la vie.'
    },
    'EN.ATM.CO2E.PC': {
      description: 'Émissions de CO2 par habitant en tonnes métriques.',
      interpretation: 'Indicateur clé de l\'impact environnemental par personne. Les pays développés ont généralement des émissions plus élevées.'
    },
    'EG.USE.ELEC.KH.PC': {
      description: 'Consommation d\'électricité par habitant en kilowattheures.',
      interpretation: 'Reflète le niveau d\'industrialisation et de développement technologique d\'un pays.'
    },
    'SE.ADT.LITR.ZS': {
      description: 'Pourcentage de la population âgée de 15 ans et plus sachant lire et écrire.',
      interpretation: 'Indicateur fondamental du développement humain et de la capacité économique.'
    }
  };

  const extraInfo = indicatorDescriptions[indicator.code] || {
    description: indicator.description,
    interpretation: 'Cet indicateur fait partie des données de la Banque Mondiale pour le suivi du développement.'
  };

  return (
    <div className="indicator-info">
      <div className="info-header">
        <h3>{indicator.name}</h3>
        <span className="indicator-code">{indicator.code}</span>
      </div>
      
      <div className="info-body">
        <div className="info-section">
          <h4>📋 Description</h4>
          <p>{extraInfo.description}</p>
        </div>

        <div className="info-section">
          <h4>💡 Interprétation</h4>
          <p>{extraInfo.interpretation}</p>
        </div>

        <div className="info-metadata">
          <div className="meta-item">
            <span className="meta-label">Unité:</span>
            <span className="meta-value">{indicator.unit || 'N/A'}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Source:</span>
            <span className="meta-value">{indicator.source}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Pays couverts:</span>
            <span className="meta-value">{indicator.country_count}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Période:</span>
            <span className="meta-value">{indicator.first_year} - {indicator.last_year}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Points de données:</span>
            <span className="meta-value">{indicator.value_count?.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndicatorInfo;
