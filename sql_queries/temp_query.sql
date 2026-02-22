SELECT ps.id, c.name, c.iso3, ps.year, s.code as sex, ps.population_count, ps.age_group_id 
FROM population_stat ps 
JOIN country c ON ps.country_id = c.id 
JOIN sex s ON ps.sex_id = s.id 
WHERE ps.country_id=511 AND ps.year=1960 
ORDER BY ps.id ASC;