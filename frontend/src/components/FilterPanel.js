import './FilterPanel.css';

// Mapping des codes de langue vers leurs noms complets en français
const getLanguageName = (code) => {
  const languageNames = {
    'en': 'Anglais',
    'fr': 'Français',
    'es': 'Espagnol',
    'ar': 'Arabe',
    'zh': 'Chinois',
    'ru': 'Russe',
    'pt': 'Portugais',
    'de': 'Allemand',
    'ja': 'Japonais',
    'hi': 'Hindi',
    'it': 'Italien',
    'ko': 'Coréen',
    'tr': 'Turc',
    'pl': 'Polonais',
    'nl': 'Néerlandais',
    'sv': 'Suédois',
    'id': 'Indonésien',
    'fa': 'Persan',
    'th': 'Thaï',
    'vi': 'Vietnamien',
    'ro': 'Roumain',
    'el': 'Grec',
    'hu': 'Hongrois',
    'cs': 'Tchèque',
    'da': 'Danois',
    'fi': 'Finnois',
    'no': 'Norvégien',
    'uk': 'Ukrainien',
    'he': 'Hébreu',
    'bn': 'Bengali',
    'ms': 'Malais',
    'ur': 'Ourdou',
    'ta': 'Tamoul',
    'te': 'Télougou',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Pendjabi',
    'sw': 'Swahili',
    'am': 'Amharique',
    'ha': 'Haoussa',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'zu': 'Zoulou',
    'af': 'Afrikaans',
    'sq': 'Albanais',
    'hy': 'Arménien',
    'az': 'Azéri',
    'eu': 'Basque',
    'be': 'Biélorusse',
    'bs': 'Bosnien',
    'bg': 'Bulgare',
    'ca': 'Catalan',
    'hr': 'Croate',
    'et': 'Estonien',
    'ka': 'Géorgien',
    'is': 'Islandais',
    'lv': 'Letton',
    'lt': 'Lituanien',
    'mk': 'Macédonien',
    'mt': 'Maltais',
    'mn': 'Mongol',
    'sr': 'Serbe',
    'sk': 'Slovaque',
    'sl': 'Slovène',
    'tl': 'Tagalog',
    'cy': 'Gallois',
    'ga': 'Irlandais',
    'gd': 'Gaélique écossais',
    'la': 'Latin',
    'my': 'Birman',
    'km': 'Khmer',
    'lo': 'Lao',
    'ne': 'Népalais',
    'si': 'Cingalais',
    'so': 'Somalien',
    'ti': 'Tigrinya',
    'uz': 'Ouzbek',
    'yi': 'Yiddish'
  };
  
  return languageNames[code] || code.toUpperCase();
};

const FilterPanel = ({ 
  years, 
  sexCategories,
  ageGroups,
  languages,
  selectedYear, 
  selectedSex,
  selectedAgeGroup,
  selectedLanguage,
  onYearChange,
  onSexChange,
  onAgeGroupChange,
  onLanguageChange
}) => {
  return (
    <div className="filter-panel">
      <h3 className="filter-title">Filtres</h3>
      
      <div className="filter-group">
        <label htmlFor="year-select">Année</label>
        <select 
          id="year-select"
          value={selectedYear}
          onChange={(e) => onYearChange(e.target.value)}
          className="filter-select"
        >
          {years.map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="sex-select">Catégorie</label>
        <select 
          id="sex-select"
          value={selectedSex}
          onChange={(e) => onSexChange(e.target.value)}
          className="filter-select"
        >
          {sexCategories.map(sex => (
            <option key={sex.code} value={sex.code}>
              {sex.label}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="age-select">Tranche d'âge</label>
        <select 
          id="age-select"
          value={selectedAgeGroup}
          onChange={(e) => onAgeGroupChange(e.target.value)}
          className="filter-select"
        >
          <option value="ALL">Toutes les tranches</option>
          {ageGroups && ageGroups.filter(ag => ag.label !== 'ALL').map(ageGroup => (
            <option key={ageGroup.id} value={ageGroup.id}>
              {ageGroup.label} ans
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="language-select">Langue</label>
        <select 
          id="language-select"
          value={selectedLanguage}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="filter-select"
        >
          <option value="ALL">Toutes les langues</option>
          {languages && languages.map(language => (
            <option key={language.iso_code} value={language.iso_code}>
              {getLanguageName(language.iso_code)} ({language.country_count})
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterPanel;
