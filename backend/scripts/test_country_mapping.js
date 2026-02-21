/**
 * Script de test pour vérifier le mapping des pays
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

const pool = new Pool({
    user: 'elias',
    host: 'localhost',
    database: 'worlddatavision',
    password: '',
    port: 5432,
});

async function testMapping() {
    const client = await pool.connect();
    
    try {
        // Lire les premiers pays du fichier IMF
        const csvPath = path.join(__dirname, '../../Data/IRC/imf-dm-export-20260221.csv');
        const content = fs.readFileSync(csvPath, 'utf-8');
        const lines = content.split('\n').slice(2, 12); // 10 premiers pays
        
        console.log('📋 Test de mapping des pays IMF → DB:\n');
        
        // Récupérer tous les pays de la DB
        const result = await client.query('SELECT id, iso3, name FROM country ORDER BY name');
        const dbCountries = result.rows;
        
        console.log(`✅ ${dbCountries.length} pays dans la DB\n`);
        
        // Tester le mapping pour chaque pays IMF
        for (const line of lines) {
            if (!line.trim()) continue;
            
            const parts = line.split(',');
            const imfName = parts[0].trim();
            
            console.log(`🔍 "${imfName}"`);
            
            // Chercher dans la DB
            const found = dbCountries.find(c => 
                c.name.toLowerCase().includes(imfName.toLowerCase()) ||
                imfName.toLowerCase().includes(c.name.toLowerCase())
            );
            
            if (found) {
                console.log(`   ✅ Trouvé: ${found.name} (${found.iso3})`);
            } else {
                console.log(`   ❌ NON TROUVÉ - Nécessite un mapping manuel`);
            }
            console.log('');
        }
        
    } finally {
        client.release();
        await pool.end();
    }
}

testMapping().catch(console.error);
