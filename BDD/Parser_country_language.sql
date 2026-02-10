-- =====================================================
-- 0️⃣ Supprimer si existait pour repartir à zéro
-- =====================================================
DROP TABLE IF EXISTS country_language;
DROP TABLE IF EXISTS language;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS country_staging;

-- =====================================================
-- 1️⃣ Table country
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
-- 2️⃣ Table language
-- =====================================================
CREATE TABLE language (
    id SERIAL PRIMARY KEY,
    iso_code VARCHAR(10) UNIQUE,
    name VARCHAR(100),
    group_name VARCHAR(100)
);

-- =====================================================
-- 3️⃣ Table country_language (N:M)
-- =====================================================
CREATE TABLE country_language (
    country_id INT NOT NULL REFERENCES country(id),
    language_id INT NOT NULL REFERENCES language(id),
    PRIMARY KEY (country_id, language_id)
);

-- =====================================================
-- 4️⃣ Table staging pour lire le CSV
-- =====================================================
CREATE TEMP TABLE country_staging (
    iso3 TEXT,
    iso2 TEXT,
    name TEXT,
    region TEXT,
    capital TEXT,
    languages TEXT,
    currency_name TEXT,
    lldc TEXT,
    sids TEXT,
    ldc TEXT,
    is_independent TEXT
);

-- =====================================================
-- 5️⃣ Importer le CSV
-- =====================================================
-- Remplacer /home/elias/Data/country.csv par le chemin réel
\copy country_staging(iso3, iso2, name, region, capital, languages, currency_name, lldc, sids, ldc, is_independent) 
FROM 'Data/country-codes.csv' CSV HEADER;

-- =====================================================
-- 6️⃣ Insérer dans country
-- =====================================================
INSERT INTO country (iso2, iso3, name, region, capital, currency_name, lldc, sids, ldc, is_independent)
SELECT
    iso2,
    iso3,
    name,
    region,
    capital,
    currency_name,
    CASE WHEN lldc='True' THEN TRUE ELSE FALSE END,
    CASE WHEN sids='True' THEN TRUE ELSE FALSE END,
    CASE WHEN ldc='True' THEN TRUE ELSE FALSE END,
    CASE WHEN is_independent='True' THEN TRUE ELSE FALSE END
FROM country_staging;

-- =====================================================
-- 7️⃣ Insérer dans language
-- =====================================================
INSERT INTO language (iso_code, name)
SELECT DISTINCT TRIM(lang) AS iso_code, TRIM(lang) AS name
FROM country_staging, unnest(string_to_array(languages, ',')) AS lang
ON CONFLICT (iso_code) DO NOTHING;

-- =====================================================
-- 8️⃣ Insérer dans country_language
-- =====================================================
INSERT INTO country_language (country_id, language_id)
SELECT c.id AS country_id, l.id AS language_id
FROM country_staging cs
JOIN country c ON cs.iso2 = c.iso2
CROSS JOIN LATERAL unnest(string_to_array(cs.languages, ',')) AS lang(code)
JOIN language l ON l.iso_code = TRIM(lang.code);
