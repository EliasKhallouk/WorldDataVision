const https = require('https');
const http = require('http');
const fs = require('fs');

function httpGet(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function checkMissingCountries() {
  try {
    // 1. Charger le mapping ISO2->ISO3
    const mappingResponse = await httpGet('http://localhost:5000/api/countries/mapping/iso2-to-iso3');
    const mapping = mappingResponse.data;
    
    // 2. Lire le SVG et extraire tous les IDs
    const svgContent = fs.readFileSync('/home/elias/PROJECT/WorldDataVision/frontend/public/world-map.svg', 'utf8');
    const idMatches = svgContent.match(/id="[A-Z]{2}"/g);
    const svgCountries = [...new Set(idMatches.map(m => m.match(/id="([A-Z]{2})"/)[1]))];
    
    // 3. Charger les données de population pour l'année 2023
    const popResponse = await httpGet('http://localhost:5000/api/population/summary?year=2023');
    const popData = popResponse.data;
    const popByISO3 = {};
    popData.forEach(c => {
      popByISO3[c.iso3] = c.total_population;
    });
    
    console.log('\n=== ANALYSE DES PAYS SVG ===\n');
    console.log(`Pays dans le SVG: ${svgCountries.length}`);
    console.log(`Pays dans le mapping: ${Object.keys(mapping).length}`);
    
    // 4. Trouver les pays du SVG qui ne sont pas dans le mapping
    const missingInMapping = svgCountries.filter(iso2 => !mapping[iso2]);
    console.log(`\n❌ Pays du SVG sans mapping (${missingInMapping.length}):`);
    missingInMapping.forEach(iso2 => {
      console.log(`  ${iso2}`);
    });
    
    // 5. Trouver les pays du SVG avec mapping mais sans données
    const withoutData = svgCountries.filter(iso2 => {
      const iso3 = mapping[iso2];
      return iso3 && !popByISO3[iso3];
    });
    console.log(`\n⚠️  Pays avec mapping mais sans données de population (${withoutData.length}):`);
    withoutData.forEach(iso2 => {
      const iso3 = mapping[iso2];
      console.log(`  ${iso2} -> ${iso3}`);
    });
    
    // 6. Pays avec tout OK
    const withData = svgCountries.filter(iso2 => {
      const iso3 = mapping[iso2];
      return iso3 && popByISO3[iso3];
    });
    console.log(`\n✅ Pays fonctionnels (mapping + données) (${withData.length}):`);
    console.log(`  Exemples: ${withData.slice(0, 10).join(', ')}`);
    
  } catch (error) {
    console.error('Erreur:', error.message);
  }
}

checkMissingCountries();
