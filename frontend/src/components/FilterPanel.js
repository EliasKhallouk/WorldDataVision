import './FilterPanel.css';

const FilterPanel = ({ 
  years, 
  sexCategories,
  ageGroups,
  selectedYear, 
  selectedSex,
  selectedAgeGroup,
  onYearChange,
  onSexChange,
  onAgeGroupChange
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
    </div>
  );
};

export default FilterPanel;
