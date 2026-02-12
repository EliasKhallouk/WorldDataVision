-- =====================================================
-- TABLE : country
-- =====================================================
CREATE TABLE country (
    id SERIAL PRIMARY KEY,
    iso2 CHAR(2) UNIQUE NOT NULL,
    iso3 CHAR(3) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    region VARCHAR(100),
    capital VARCHAR(100),
    currency_name VARCHAR(100),
    lldc BOOLEAN,
    sids BOOLEAN,
    ldc BOOLEAN,
    is_independent BOOLEAN
);

-- =====================================================
-- TABLE : age_group
-- =====================================================
DROP TABLE IF EXISTS age_group;

CREATE TABLE age_group (
    id SERIAL PRIMARY KEY,
    label VARCHAR(20),
    age_min SMALLINT NOT NULL,
    age_max SMALLINT NOT NULL
);

-- Exemple d’insertion
INSERT INTO age_group(label, age_min, age_max) VALUES
('0-4', 0, 4),
('5-9', 5, 9),
('10-14', 10, 14),
('15-19', 15, 19),
('20-24', 20, 24),
('25-29', 25, 29),
('30-34', 30, 34),
('35-39', 35, 39),
('40-44', 40, 44),
('45-49', 45, 49),
('50-54', 50, 54),
('55-59', 55, 59),
('60-64', 60, 64),
('65-69', 65, 69),
('70-74', 70, 74),
('75-79', 75, 79),
('80-84', 80, 84),
('85-89', 85, 89),
('90-94', 90, 94),
('95+', 95, 120);

INSERT INTO age_group(label, age_min, age_max)
VALUES ('ALL', 0, 120);


-- =====================================================
-- TABLE : sex
-- =====================================================
DROP TABLE IF EXISTS sex;

CREATE TABLE sex (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    label VARCHAR(50)
);

-- Insérer les valeurs de base
INSERT INTO sex (code, label) VALUES
('male', 'Homme'),
('female', 'Femme'),
('total', 'Total');


-- =====================================================
-- TABLE : language
-- =====================================================
CREATE TABLE language (
    id SERIAL PRIMARY KEY,
    iso_code VARCHAR(10),
    name VARCHAR(100),
    group_name VARCHAR(100)
);

-- =====================================================
-- TABLE : country_language (relation N:M)
-- =====================================================
CREATE TABLE country_language (
    country_id INT NOT NULL REFERENCES country(id),
    language_id INT NOT NULL REFERENCES language(id),
    PRIMARY KEY (country_id, language_id)
);

-- =====================================================
-- TABLE : year_table
-- =====================================================
DROP TABLE IF EXISTS year_table;

CREATE TABLE year_table (
    value SMALLINT PRIMARY KEY
);

-- Insérer les années
INSERT INTO year_table(value)
SELECT generate_series(1950, 2035);


-- =====================================================
-- TABLE : population_stat
-- =====================================================
CREATE TABLE population_stat (
    id BIGSERIAL PRIMARY KEY,
    country_id INT NOT NULL REFERENCES country(id),
    age_group_id INT NOT NULL REFERENCES age_group(id),
    sex_id INT NOT NULL REFERENCES sex(id),
    language_id INT REFERENCES language(id),
    year SMALLINT NOT NULL REFERENCES year_table(value),
    population_count BIGINT NOT NULL,
    source VARCHAR(150),
    confidence_level SMALLINT,
    UNIQUE (country_id, age_group_id, sex_id, language_id, year)
);

-- =====================================================
-- INDEXES POUR PERFORMANCE
-- =====================================================
CREATE INDEX idx_population_country ON population_stat(country_id);
CREATE INDEX idx_population_filters ON population_stat(age_group_id, sex_id, language_id, year);

