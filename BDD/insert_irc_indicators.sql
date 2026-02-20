-- =====================================================
-- ÉTAPE 2 : INSERTION DES NOUVEAUX INDICATEURS IRC
-- =====================================================
-- Ce script ajoute les 69 indicateurs manquants à la table indicator
-- sans modifier les 6 qui existent déjà

-- D'abord, vérifier les catégories existantes
-- (elles doivent être dans la table indicator_category)

-- Ajouter les catégories manquantes si nécessaire
INSERT INTO indicator_category (code, name, description) 
VALUES 
    ('agriculture', 'Agriculture', 'Indicateurs agricoles et alimentaires'),
    ('energy', 'Énergie', 'Indicateurs énergétiques'),
    ('technology', 'Technologie', 'Indicateurs technologiques et innovants')
ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- DÉMOGRAPHIE (population et structure)
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('SP.POP.TOTL', 'Population totale', 'Population totale en milieu d''année', 
    'nombre', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.0014.TO.ZS', 'Population 0-14 ans (%)', 'Population âgée de 0 à 14 ans (% de la population totale)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.1564.TO.ZS', 'Population 15-64 ans (%)', 'Population âgée de 15 à 64 ans (% de la population totale)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.65UP.TO.ZS', 'Population 65+ ans (%)', 'Population âgée de 65 ans et plus (% de la population totale)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.AG.MA.NO', 'Âge médian', 'Âge médian de la population (années)', 
    'années', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Calculé'),

('SP.POP.DPND', 'Ratio de dépendance total', 'Ratio de dépendance (% population active)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.DPND.OL', 'Ratio de dépendance des âgés', 'Ratio de dépendance des personnes âgées (% pop 15-64)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.DPND.YG', 'Ratio de dépendance des jeunes', 'Ratio de dépendance des jeunes (% pop 15-64)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.DYN.CBRT.IN', 'Taux de natalité', 'Taux de natalité (naissances pour 1000 habitants)', 
    'pour 1000', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.DYN.CDRT.IN', 'Taux de mortalité', 'Taux de mortalité (décès pour 1000 habitants)', 
    'pour 1000', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.POP.GROW', 'Croissance de la population', 'Taux de croissance annuelle de la population (%)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SM.POP.NETM', 'Solde migratoire net', 'Solde migratoire net (nombre de migrants)', 
    'nombre', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale'),

('SP.URB.TOTL.IN.ZS', 'Population urbaine', 'Population urbaine (% de la population totale)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'demographic'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- AGRICULTURE ET ALIMENTATION
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('AG.LND.AGRI.ZS', 'Terres agricoles', 'Terres agricoles (% de la superficie terrestre)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.LND.ARBL.HA.PC', 'Terres arables par habitant', 'Terres arables (hectares par habitant)', 
    'ha/hab', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.YLD.CREL.KG', 'Rendement des céréales', 'Rendement des cultures céréalières (kg/ha)', 
    'kg/ha', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.PRD.FOOD.XD', 'Indice de production alimentaire', 'Indice de production alimentaire (2004-2006 = 100)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.PRD.CROP.XD', 'Indice de production végétale', 'Indice de production des cultures (2004-2006 = 100)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.PRD.LVSK.XD', 'Indice de production animale', 'Indice de production du bétail (2004-2006 = 100)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('TM.VAL.FOOD.ZS.UN', 'Importations alimentaires', 'Importations alimentaires (% des importations totales)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('TX.VAL.FOOD.ZS.UN', 'Exportations agricoles', 'Exportations agricoles (% des exportations totales)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('ER.H2O.FWST.ZS', 'Stress hydrique', 'Prélèvement d''eau de surface (% des ressources renouvelables)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('ER.H2O.INTR.PC', 'Eau renouvelable par habitant', 'Ressources en eau interne renouvelables (m³/habitant)', 
    'm³/hab', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale'),

('AG.LND.FRST.ZS', 'Superficie forestière', 'Superficie forestière (% de la superficie terrestre)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'agriculture'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- ÉNERGIE
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('EG.ELC.PROD.KH', 'Production d''électricité', 'Production d''électricité (kWh)', 
    'kWh', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.FEC.RNEW.ZS', 'Consommation énergies renouvelables', 'Consommation d''énergies renouvelables (% du total)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.USE.COMM.FO.ZS', 'Consommation combustibles fossiles', 'Consommation de combustibles fossiles (% du total)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.ELC.NUCL.ZS', 'Électricité nucléaire', 'Production d''électricité nucléaire (% du total)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.ELC.HYRO.ZS', 'Électricité hydroélectrique', 'Production d''électricité hydroélectrique (% du total)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.IMP.CONS.ZS', 'Importations nettes d''énergie', 'Importations nettes d''énergie (% de la consommation)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('NY.GDP.PETR.RT.ZS', 'Rente pétrolière', 'Rente pétrolière (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('NY.GDP.NGAS.RT.ZS', 'Rente gazière', 'Rente gazière naturelle (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('NY.GDP.COAL.RT.ZS', 'Rente minière charbon', 'Rente minière du charbon (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.USE.PCAP.KG.OE', 'Consommation énergétique par habitant', 'Consommation d''énergie (kg équivalent pétrole/habitant)', 
    'kg oe/hab', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.ELC.ACCS.ZS', 'Accès à l''électricité', 'Population avec accès à l''électricité (%)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale'),

('EG.USE.ELEC.KH.PC', 'Consommation d''électricité par habitant', 'Consommation d''électricité (kWh par habitant)', 
    'kWh/hab', (SELECT id FROM indicator_category WHERE code = 'energy'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- GOUVERNANCE & FINANCES PUBLIQUES
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('CC.EST', 'Contrôle de la corruption', 'Indice de contrôle de la corruption (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('GE.EST', 'Efficacité gouvernementale', 'Indice d''efficacité gouvernementale (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('PV.EST', 'Stabilité politique', 'Indice de stabilité politique et absence de violence (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('RL.EST', 'État de droit', 'Indice d''état de droit (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('RQ.EST', 'Qualité réglementaire', 'Indice de qualité réglementaire (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('VA.EST', 'Voix et responsabilité', 'Indice de voix et responsabilité (WGI)', 
    'indice', (SELECT id FROM indicator_category WHERE code = 'institutional'), 'World Bank Governance Indicators'),

('DT.DOD.DECT.GN.ZS', 'Dette externe', 'Dette externe (% du RNB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('DT.TDS.DECT.EX.ZS', 'Service de la dette', 'Service de la dette (% des exportations)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('FI.RES.TOTL.MO', 'Réserves de change', 'Réserves de change (mois d''importations)', 
    'mois', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- ÉCONOMIE
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('NY.GDP.MKTP.KD.ZG', 'Croissance du PIB', 'Croissance du PIB (% annuel)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('FP.CPI.TOTL.ZG', 'Inflation', 'Indice des prix à la consommation (% annuel)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('SL.UEM.TOTL.ZS', 'Taux de chômage', 'Taux de chômage (% de la population active)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('BN.CAB.XOKA.GD.ZS', 'Balance courante', 'Balance courante (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('BX.KLT.DINV.WD.GD.ZS', 'Investissements directs étrangers', 'Investissements directs étrangers (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale'),

('MS.MIL.XPND.GD.ZS', 'Dépenses militaires', 'Dépenses militaires (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'economy'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- ÉDUCATION & INNOVATION & TECHNOLOGIE
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('SE.TER.ENRR', 'Scolarisation tertiaire', 'Taux brut de scolarisation dans le supérieur (%)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale'),

('SE.ADT.LITR.ZS', 'Taux d''alphabétisation adultes', 'Taux d''alphabétisation des adultes (%) (%)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale'),

('GB.XPD.RSDV.GD.ZS', 'Dépenses R&D', 'Dépenses en recherche et développement (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('SP.POP.SCIE.RD.P6', 'Chercheurs par million', 'Chercheurs (ETP par million d''habitants)', 
    'par million', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IP.PAT.RESD', 'Demandes de brevets', 'Demandes de brevets déposées par les résidents', 
    'nombre', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IP.JRN.ARTC.SC', 'Articles scientifiques', 'Articles de revues scientifiques et techniques', 
    'nombre', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('TX.VAL.TECH.MF.ZS', 'Exportations haute technologie', 'Exportations de produits de haute technologie (% des exportations manufacturées)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IT.NET.USER.ZS', 'Utilisateurs Internet', 'Utilisateurs d''Internet (% de la population)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IT.CEL.SETS.P2', 'Abonnements mobiles', 'Abonnements à la téléphonie mobile (pour 100 habitants)', 
    'pour 100', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IT.NET.BBND.P2', 'Abonnements haut débit', 'Abonnements au haut débit fixe (pour 100 habitants)', 
    'pour 100', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale'),

('IT.NET.SECR.P6', 'Serveurs sécurisés', 'Serveurs Internet sécurisés (pour 1 million d''habitants)', 
    'pour 1M', (SELECT id FROM indicator_category WHERE code = 'technology'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- ENVIRONNEMENT & SANTÉ
-- =====================================================
INSERT INTO indicator (code, name, description, unit, category_id, source) VALUES

('AG.LND.TOTL.K2', 'Superficie terrestre', 'Superficie terrestre (km²)', 
    'km²', (SELECT id FROM indicator_category WHERE code = 'environment'), 'Banque Mondiale'),

('EN.ATM.CO2E.PC', 'Émissions CO2 par habitant', 'Émissions de dioxyde de carbone (tonnes métriques par habitant)', 
    't/hab', (SELECT id FROM indicator_category WHERE code = 'environment'), 'Banque Mondiale'),

('EN.GHG.CO2.PC.CE.AR5', 'Émissions CO2 (AR5)', 'Émissions de CO2 excluant LULUCF par habitant (t CO2e/capita)', 
    't/hab', (SELECT id FROM indicator_category WHERE code = 'environment'), 'Banque Mondiale'),

('SH.XPD.CHEX.GD.ZS', 'Dépenses de santé', 'Dépenses de santé actuelle (% du PIB)', 
    '%', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale'),

('SH.MED.PHYS.ZS', 'Médecins par 1000', 'Médecins (pour 1000 habitants)', 
    'pour 1000', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale'),

('SH.MED.BEDS.ZS', 'Lits d''hôpital', 'Lits d''hôpital (pour 1000 habitants)', 
    'pour 1000', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale'),

('SP.DYN.IMRT.IN', 'Mortalité infantile', 'Mortalité infantile (pour 1000 naissances vivantes)', 
    'pour 1000', (SELECT id FROM indicator_category WHERE code = 'social'), 'Banque Mondiale')

ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- Vérification
-- =====================================================
SELECT COUNT(*) as total_indicators FROM indicator;
SELECT COUNT(*) as irc_indicators FROM indicator WHERE code IN (
    'SP.POP.TOTL', 'SP.POP.0014.TO.ZS', 'SP.POP.1564.TO.ZS', 'SP.POP.65UP.TO.ZS', 'SP.POP.AG.MA.NO',
    'SP.POP.DPND', 'SP.POP.DPND.OL', 'SP.POP.DPND.YG', 'SP.DYN.CBRT.IN', 'SP.DYN.CDRT.IN',
    'SP.POP.GROW', 'SM.POP.NETM', 'SP.URB.TOTL.IN.ZS', 'AG.LND.AGRI.ZS', 'AG.LND.ARBL.HA.PC',
    'AG.YLD.CREL.KG', 'AG.PRD.FOOD.XD', 'AG.PRD.CROP.XD', 'AG.PRD.LVSK.XD', 'TM.VAL.FOOD.ZS.UN',
    'TX.VAL.FOOD.ZS.UN', 'ER.H2O.FWST.ZS', 'ER.H2O.INTR.PC', 'AG.LND.FRST.ZS', 'EG.ELC.PROD.KH',
    'EG.FEC.RNEW.ZS', 'EG.USE.COMM.FO.ZS', 'EG.ELC.NUCL.ZS', 'EG.ELC.HYRO.ZS', 'EG.IMP.CONS.ZS',
    'NY.GDP.PETR.RT.ZS', 'NY.GDP.NGAS.RT.ZS', 'NY.GDP.COAL.RT.ZS', 'EG.USE.PCAP.KG.OE', 'EG.ELC.ACCS.ZS',
    'EG.USE.ELEC.KH.PC', 'CC.EST', 'GE.EST', 'PV.EST', 'RL.EST', 'RQ.EST', 'VA.EST', 'DT.DOD.DECT.GN.ZS',
    'DT.TDS.DECT.EX.ZS', 'FI.RES.TOTL.MO', 'NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG', 'SL.UEM.TOTL.ZS',
    'BN.CAB.XOKA.GD.ZS', 'BX.KLT.DINV.WD.GD.ZS', 'MS.MIL.XPND.GD.ZS', 'SE.TER.ENRR', 'SE.ADT.LITR.ZS',
    'GB.XPD.RSDV.GD.ZS', 'SP.POP.SCIE.RD.P6', 'IP.PAT.RESD', 'IP.JRN.ARTC.SC', 'TX.VAL.TECH.MF.ZS',
    'IT.NET.USER.ZS', 'IT.CEL.SETS.P2', 'IT.NET.BBND.P2', 'IT.NET.SECR.P6', 'AG.LND.TOTL.K2',
    'EN.ATM.CO2E.PC', 'EN.GHG.CO2.PC.CE.AR5', 'SH.XPD.CHEX.GD.ZS', 'SH.MED.PHYS.ZS', 'SH.MED.BEDS.ZS',
    'SP.DYN.IMRT.IN'
);
