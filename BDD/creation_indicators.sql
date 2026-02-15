-- =====================================================
-- TABLES POUR LES INDICATEURS ÉCONOMIQUES, SOCIAUX ET INSTITUTIONNELS
-- =====================================================

-- =====================================================
-- TABLE : indicator_category
-- =====================================================
DROP TABLE IF EXISTS indicator_category CASCADE;

CREATE TABLE indicator_category (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT
);

INSERT INTO indicator_category (code, name, description) VALUES
('economy', 'Économie', 'Indicateurs économiques et financiers'),
('social', 'Social', 'Indicateurs sociaux et de développement humain'),
('demographic', 'Démographie', 'Indicateurs démographiques'),
('institutional', 'Institutionnel', 'Indicateurs institutionnels et gouvernementaux'),
('environment', 'Environnement', 'Indicateurs environnementaux');

-- =====================================================
-- TABLE : indicator
-- =====================================================
DROP TABLE IF EXISTS indicator CASCADE;

CREATE TABLE indicator (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(250) NOT NULL,
    description TEXT,
    unit VARCHAR(100),
    category_id INT REFERENCES indicator_category(id),
    source VARCHAR(150)
);

-- Insertion des indicateurs
INSERT INTO indicator (code, name, unit, category_id, source) VALUES
-- Économie
('NY.GDP.PCAP.PP.KD', 'PIB par habitant (PPA, $ internationaux constants de 2011)', '$ internationaux constants 2011', 
    (SELECT id FROM indicator_category WHERE code = 'economy'), 
    'Indicateurs du développement dans le monde'),

-- Social
('SP.DYN.LE00.IN', 'Espérance de vie à la naissance (années)', 'années', 
    (SELECT id FROM indicator_category WHERE code = 'social'), 
    'Indicateurs du développement dans le monde'),
('SE.XPD.TOTL.GD.ZS', 'Dépenses publiques en éducation (% du PIB)', '% du PIB', 
    (SELECT id FROM indicator_category WHERE code = 'social'), 
    'Indicateurs du développement dans le monde'),

-- Démographie
('SP.DYN.TFRT.IN', 'Taux de fertilité (naissances par femme)', 'naissances par femme', 
    (SELECT id FROM indicator_category WHERE code = 'demographic'), 
    'Indicateurs du développement dans le monde'),

-- Institutionnel
('GC.DOD.TOTL.GD.ZS', 'Dette du gouvernement central (% du PIB)', '% du PIB', 
    (SELECT id FROM indicator_category WHERE code = 'institutional'), 
    'Indicateurs du développement dans le monde'),
('GC.TAX.TOTL.GD.ZS', 'Revenus fiscaux (% du PIB)', '% du PIB', 
    (SELECT id FROM indicator_category WHERE code = 'institutional'), 
    'Indicateurs du développement dans le monde');

-- =====================================================
-- TABLE : indicator_value
-- =====================================================
DROP TABLE IF EXISTS indicator_value CASCADE;

CREATE TABLE indicator_value (
    id BIGSERIAL PRIMARY KEY,
    country_id INT NOT NULL REFERENCES country(id),
    indicator_id INT NOT NULL REFERENCES indicator(id),
    year SMALLINT NOT NULL REFERENCES year_table(value),
    value DOUBLE PRECISION,
    UNIQUE (country_id, indicator_id, year)
);

-- =====================================================
-- INDEXES POUR PERFORMANCE
-- =====================================================
CREATE INDEX idx_indicator_value_country ON indicator_value(country_id);
CREATE INDEX idx_indicator_value_indicator ON indicator_value(indicator_id);
CREATE INDEX idx_indicator_value_year ON indicator_value(year);
CREATE INDEX idx_indicator_value_composite ON indicator_value(country_id, indicator_id, year);
