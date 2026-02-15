-- Script pour ajouter les nouvelles colonnes à la table country

-- Informations de base
ALTER TABLE country ADD COLUMN IF NOT EXISTS name_local VARCHAR(255);
ALTER TABLE country ADD COLUMN IF NOT EXISTS area_sq_km NUMERIC;
ALTER TABLE country ADD COLUMN IF NOT EXISTS continent VARCHAR(50);

-- Capitale (détails)
ALTER TABLE country ADD COLUMN IF NOT EXISTS capital_latitude NUMERIC(10, 8);
ALTER TABLE country ADD COLUMN IF NOT EXISTS capital_longitude NUMERIC(11, 8);

-- Devise (détails complets)
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_local VARCHAR(150);
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_code VARCHAR(10);
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_symbol VARCHAR(10);
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_numeric INTEGER;
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_subunit_value INTEGER;
ALTER TABLE country ADD COLUMN IF NOT EXISTS currency_subunit_name VARCHAR(50);

-- Informations culturelles
ALTER TABLE country ADD COLUMN IF NOT EXISTS flag VARCHAR(10);
ALTER TABLE country ADD COLUMN IF NOT EXISTS timezones TEXT[]; -- Array de fuseaux horaires
ALTER TABLE country ADD COLUMN IF NOT EXISTS borders TEXT[]; -- Array de codes pays frontaliers

-- Commentaire sur la table
COMMENT ON COLUMN country.name_local IS 'Nom du pays dans sa langue locale';
COMMENT ON COLUMN country.area_sq_km IS 'Superficie en kilomètres carrés';
COMMENT ON COLUMN country.continent IS 'Continent du pays';
COMMENT ON COLUMN country.capital_latitude IS 'Latitude de la capitale';
COMMENT ON COLUMN country.capital_longitude IS 'Longitude de la capitale';
COMMENT ON COLUMN country.currency_local IS 'Nom de la devise en langue locale';
COMMENT ON COLUMN country.currency_code IS 'Code ISO 4217 de la devise';
COMMENT ON COLUMN country.currency_symbol IS 'Symbole de la devise';
COMMENT ON COLUMN country.currency_numeric IS 'Code numérique ISO 4217';
COMMENT ON COLUMN country.currency_subunit_value IS 'Valeur de la sous-unité (ex: 100 pour cents)';
COMMENT ON COLUMN country.currency_subunit_name IS 'Nom de la sous-unité (ex: cents, centimes)';
COMMENT ON COLUMN country.flag IS 'Emoji du drapeau';
COMMENT ON COLUMN country.timezones IS 'Liste des fuseaux horaires du pays';
COMMENT ON COLUMN country.borders IS 'Liste des codes ISO2 des pays frontaliers';

-- Afficher les colonnes après modification
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'country' 
ORDER BY ordinal_position;
