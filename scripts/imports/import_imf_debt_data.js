/**
 * Script d'import des données de dette publique du FMI
 * Source: IMF - Central Government Debt (Percent of GDP)
 * Fichier: Data/IRC/imf-dm-export-20260221.csv
 * 
 * Fonctionnalités:
 * - Conversion format large → format long
 * - Mapping noms de pays (anglais) → codes ISO3
 * - Fusion avec données existantes (moyenne si dupliqué)
 * - Mise à jour des métadonnées de l'indicateur
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

// Configuration de la base de données
const pool = new Pool({
    user: process.env.DB_USER || 'elias',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'worlddatavision',
    password: process.env.DB_PASSWORD || 'MaBaseDeDonnee',
    port: process.env.DB_PORT || 5432,
});

// Mapping manuel des noms de pays IMF → codes ISO3
// Cas spéciaux où le nom IMF diffère significativement
const COUNTRY_NAME_MAPPING = {
    "Bahamas, The": "BHS",
    "Congo, Dem. Rep.": "COD",
    "Congo, Rep.": "COG",
    "Egypt, Arab Rep.": "EGY",
    "Gambia, The": "GMB",
    "Iran, Islamic Rep.": "IRN",
    "Korea, Rep.": "KOR",
    "Kyrgyz Republic": "KGZ",
    "Lao PDR": "LAO",
    "Micronesia, Fed. Sts.": "FSM",
    "Russian Federation": "RUS",
    "São Tomé and Príncipe": "STP",
    "Slovak Republic": "SVK",
    "Syrian Arab Republic": "SYR",
    "Venezuela, RB": "VEN",
    "Yemen, Rep.": "YEM",
    "Türkiye": "TUR",
    "Türkiye, Republic of": "TUR",
    "West Bank and Gaza": "PSE",
};

// Mapping français → anglais pour correspondance
const FRENCH_TO_ENGLISH = {
    "Andorre": "Andorra",
    "Argentine": "Argentina",
    "Éthiopie": "Ethiopia",
    "Bahreïn": "Bahrain",
    "Bélarus": "Belarus",
    "Bénin": "Benin",
    "Bosnie-Herzégovine": "Bosnia and Herzegovina",
    "Brunéi Darussalam": "Brunei Darussalam",
    "États-Unis": "United States",
    "Côte d'Ivoire": "Côte d'Ivoire",
};

/**
 * Lit le fichier CSV IMF et retourne les données parsées
 */
function readIMFCSV(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    if (lines.length < 3) {
        throw new Error('Fichier CSV invalide: pas assez de lignes');
    }
    
    // Ligne 1: En-tête avec les années
    const headerLine = lines[0];
    const headers = headerLine.split(',');
    const years = headers.slice(1).map(h => parseInt(h.trim()));
    
    console.log(`📅 Plage temporelle: ${years[0]} - ${years[years.length - 1]}`);
    console.log(`📊 Nombre d'années: ${years.length}`);
    
    // Ligne 2 est vide, on commence à la ligne 3
    const dataLines = lines.slice(2);
    console.log(`🌍 Nombre de pays: ${dataLines.length}`);
    
    return { years, dataLines };
}

/**
 * Parse une ligne de données et retourne les enregistrements
 */
function parseDataLine(line, years) {
    const parts = line.split(',');
    const countryName = parts[0].trim();
    const values = parts.slice(1);
    
    const records = [];
    
    for (let i = 0; i < years.length; i++) {
        const valueStr = values[i] ? values[i].trim() : '';
        
        if (valueStr && valueStr !== 'no data' && valueStr !== '') {
            // Remplacer la virgule par un point pour la conversion numérique
            const value = parseFloat(valueStr.replace(',', '.'));
            
            if (!isNaN(value)) {
                records.push({
                    country: countryName,
                    year: years[i],
                    value: value
                });
            }
        }
    }
    
    return records;
}

/**
 * Récupère le mapping des pays depuis la base de données
 * Retourne un Map avec les noms en clé et les infos en valeur
 */
async function getCountryMapping(client) {
    const result = await client.query(`
        SELECT id, iso3, name 
        FROM country 
        ORDER BY name
    `);
    
    const mapping = new Map();
    
    // Créer un index par nom (insensible à la casse et aux accents)
    for (const row of result.rows) {
        // Normaliser le nom (lowercase, sans accents)
        const normalizedName = row.name
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
        
        mapping.set(normalizedName, {
            id: row.id,
            iso3: row.iso3,
            originalName: row.name
        });
    }
    
    return mapping;
}

/**
 * Trouve le country_id pour un nom de pays IMF
 */
function findCountryId(imfName, countryMapping) {
    // 1. Vérifier le mapping manuel
    if (COUNTRY_NAME_MAPPING[imfName]) {
        const iso3 = COUNTRY_NAME_MAPPING[imfName];
        for (const [_, info] of countryMapping) {
            if (info.iso3 === iso3) {
                return info.id;
            }
        }
    }
    
    // 2. Recherche par nom normalisé
    const normalizedIMF = imfName
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/,/g, '')
        .trim();
    
    // Recherche exacte
    if (countryMapping.has(normalizedIMF)) {
        return countryMapping.get(normalizedIMF).id;
    }
    
    // 3. Recherche partielle (contient)
    for (const [name, info] of countryMapping) {
        if (name.includes(normalizedIMF) || normalizedIMF.includes(name)) {
            return info.id;
        }
    }
    
    return null;
}

/**
 * Récupère l'ID de l'indicateur GC.DOD.TOTL.GD.ZS
 */
async function getIndicatorId(client) {
    const result = await client.query(`
        SELECT id FROM indicator WHERE code = 'GC.DOD.TOTL.GD.ZS'
    `);
    
    if (result.rows.length === 0) {
        throw new Error("Indicateur GC.DOD.TOTL.GD.ZS non trouvé dans la base");
    }
    
    return result.rows[0].id;
}

/**
 * Met à jour la source de l'indicateur
 */
async function updateIndicatorSource(client, indicatorId) {
    await client.query(`
        UPDATE indicator 
        SET source = 'World Bank + IMF (Central Government Debt)'
        WHERE id = $1
    `, [indicatorId]);
    
    console.log('✅ Source de l\'indicateur mise à jour');
}

/**
 * Insère ou met à jour les valeurs avec fusion (moyenne)
 */
async function upsertValues(client, indicatorId, records) {
    let inserted = 0;
    let updated = 0;
    let skipped = 0;
    
    const countryMapping = await getCountryMapping(client);
    
    for (const record of records) {
        const countryId = findCountryId(record.country, countryMapping);
        
        if (!countryId) {
            console.warn(`⚠️  Pays non trouvé: ${record.country}`);
            skipped++;
            continue;
        }
        
        // Vérifier si la valeur existe déjà
        const existingResult = await client.query(`
            SELECT value FROM indicator_value
            WHERE country_id = $1 AND indicator_id = $2 AND year = $3
        `, [countryId, indicatorId, record.year]);
        
        if (existingResult.rows.length > 0) {
            // Calculer la moyenne
            const existingValue = existingResult.rows[0].value;
            const newValue = (existingValue + record.value) / 2;
            
            await client.query(`
                UPDATE indicator_value
                SET value = $1
                WHERE country_id = $2 AND indicator_id = $3 AND year = $4
            `, [newValue, countryId, indicatorId, record.year]);
            
            updated++;
        } else {
            // Insérer la nouvelle valeur
            await client.query(`
                INSERT INTO indicator_value (country_id, indicator_id, year, value)
                VALUES ($1, $2, $3, $4)
            `, [countryId, indicatorId, record.year, record.value]);
            
            inserted++;
        }
    }
    
    return { inserted, updated, skipped };
}

/**
 * Fonction principale
 */
async function main() {
    const client = await pool.connect();
    
    try {
        console.log('🚀 Début de l\'import des données IMF de dette publique\n');
        
        // 1. Lire le fichier CSV
        const csvPath = path.join(__dirname, '../../Data/IRC/imf-dm-export-20260221.csv');
        console.log(`📂 Lecture du fichier: ${csvPath}`);
        
        const { years, dataLines } = readIMFCSV(csvPath);
        
        // 2. Parser toutes les lignes
        console.log('\n📊 Parsing des données...');
        const allRecords = [];
        
        for (const line of dataLines) {
            const records = parseDataLine(line, years);
            allRecords.push(...records);
        }
        
        console.log(`✅ ${allRecords.length} valeurs parsées`);
        
        // 3. Récupérer l'ID de l'indicateur
        const indicatorId = await getIndicatorId(client);
        console.log(`\n🎯 Indicateur ID: ${indicatorId}`);
        
        // 4. Commencer la transaction
        await client.query('BEGIN');
        
        // 5. Insérer/mettre à jour les valeurs
        console.log('\n💾 Import des valeurs dans la base...');
        const stats = await upsertValues(client, indicatorId, allRecords);
        
        // 6. Mettre à jour la source
        await updateIndicatorSource(client, indicatorId);
        
        // 7. Commit
        await client.query('COMMIT');
        
        console.log('\n✅ Import terminé avec succès!');
        console.log(`   📥 Nouvelles valeurs insérées: ${stats.inserted}`);
        console.log(`   🔄 Valeurs mises à jour (moyenne): ${stats.updated}`);
        console.log(`   ⏭️  Valeurs ignorées (pays non trouvé): ${stats.skipped}`);
        
    } catch (error) {
        await client.query('ROLLBACK');
        console.error('❌ Erreur lors de l\'import:', error);
        throw error;
    } finally {
        client.release();
        await pool.end();
    }
}

// Exécution
if (require.main === module) {
    main().catch(error => {
        console.error('Erreur fatale:', error);
        process.exit(1);
    });
}

module.exports = { main };
