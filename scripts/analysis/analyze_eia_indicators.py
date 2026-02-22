#!/usr/bin/env python3
"""
Identifier les indicateurs IRC qui peuvent être complétés avec les données EIA
"""

import psycopg2
import json
import re
from collections import defaultdict

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_all_indicators():
    """Récupérer tous les indicateurs IRC avec leur couverture actuelle"""
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        i.code,
        i.name,
        i.category_id,
        COUNT(DISTINCT iv.country_id) as country_count
    FROM indicator i
    LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
    WHERE i.code != 'EN.ATM.CO2E.PC'
    GROUP BY i.id, i.code, i.name, i.category_id
    ORDER BY country_count ASC, i.category_id, i.code;
    """
    
    cursor.execute(query)
    indicators = []
    
    for row in cursor.fetchall():
        indicators.append({
            'code': row[0],
            'name': row[1],
            'category': row[2],
            'coverage': row[3]
        })
    
    cursor.close()
    conn.close()
    
    return indicators

def analyze_eia_bulk_series():
    """Analyser le fichier bulk EIA pour identifier les séries disponibles"""
    
    print("\n📊 Analyzing EIA bulk file...")
    print("   Looking for energy-related series...\n")
    
    # Categories we're interested in
    energy_keywords = {
        'electricity': ['electricity', 'electric'],
        'renewable': ['renewable', 'solar', 'wind', 'hydro', 'geothermal', 'biomass'],
        'nuclear': ['nuclear'],
        'coal': ['coal'],
        'oil': ['petroleum', 'oil'],
        'gas': ['natural gas', 'gas'],
        'energy': ['energy consumption', 'energy production', 'energy supply'],
        'emissions': ['carbon', 'co2', 'emissions'],
        'efficiency': ['efficiency', 'intensity']
    }
    
    series_catalog = defaultdict(list)
    unique_names = set()
    
    with open('/tmp/INTL.txt', 'r') as f:
        for i, line in enumerate(f):
            if i % 100000 == 0 and i > 0:
                print(f"      Processed {i:,} lines...")
            
            try:
                series = json.loads(line)
                series_id = series.get('series_id', '')
                name = series.get('name', '').lower()
                
                # Only annual data in standard units
                if not series_id.endswith('.A'):
                    continue
                
                # Skip regional aggregations
                if any(x in series_id for x in ['WORL', 'OECD', 'OPEC', 'EURO', 'AFRC', 'ASOC', 'MIDE', 'CSAM', 'NOAM']):
                    continue
                
                # Categorize by keywords
                for category, keywords in energy_keywords.items():
                    if any(kw in name for kw in keywords):
                        if name not in unique_names:
                            series_catalog[category].append({
                                'id': series_id,
                                'name': series.get('name', ''),
                                'unit': series.get('units', ''),
                                'geography': series.get('geography', '')
                            })
                            unique_names.add(name)
                        break
            
            except json.JSONDecodeError:
                continue
    
    print(f"\n   ✅ Found {len(unique_names):,} unique energy series\n")
    
    return series_catalog

def map_irc_to_eia(indicators, eia_catalog):
    """Mapper les indicateurs IRC aux séries EIA disponibles"""
    
    print("="*80)
    print("MAPPING IRC INDICATORS TO EIA DATA")
    print("="*80)
    
    mappings = []
    
    # Define manual mappings based on IRC indicators
    irc_eia_map = {
        # Category 7 - Energy
        'EG.ELC.PROD.KH': {
            'keywords': ['electricity generation', 'electricity production', 'net generation'],
            'category': 'electricity'
        },
        'EG.ELC.HYRO.ZS': {
            'keywords': ['hydroelectric', 'hydro'],
            'category': 'renewable'
        },
        'EG.ELC.NUCL.ZS': {
            'keywords': ['nuclear'],
            'category': 'nuclear'
        },
        'EG.ELC.COAL.ZS': {
            'keywords': ['coal electricity', 'coal generation'],
            'category': 'coal'
        },
        'EG.ELC.NGAS.ZS': {
            'keywords': ['natural gas electricity', 'gas generation'],
            'category': 'gas'
        },
        'EG.ELC.PETR.ZS': {
            'keywords': ['petroleum electricity', 'oil generation'],
            'category': 'oil'
        },
        'EG.FEC.RNEW.ZS': {
            'keywords': ['renewable'],
            'category': 'renewable'
        },
        'EG.USE.ELEC.KH.PC': {
            'keywords': ['electricity consumption per capita', 'electricity demand per capita'],
            'category': 'electricity'
        },
        'EG.USE.PCAP.KG.OE': {
            'keywords': ['energy use per capita', 'energy consumption per capita'],
            'category': 'energy'
        },
        'EG.IMP.CONS.ZS': {
            'keywords': ['energy imports', 'net energy imports'],
            'category': 'energy'
        },
        'EG.ELC.RNEW.ZS': {
            'keywords': ['renewable electricity'],
            'category': 'renewable'
        },
        'EG.ELC.FOSL.ZS': {
            'keywords': ['fossil electricity', 'fossil fuel electricity'],
            'category': 'electricity'
        }
    }
    
    for indicator in indicators:
        code = indicator['code']
        name = indicator['name'].lower()
        coverage = indicator['coverage']
        
        # Check if we have a mapping
        if code in irc_eia_map:
            mapping_info = irc_eia_map[code]
            category = mapping_info['category']
            
            if category in eia_catalog:
                # Find matching series
                matches = []
                for series in eia_catalog[category]:
                    series_name = series['name'].lower()
                    if any(kw in series_name for kw in mapping_info['keywords']):
                        matches.append(series)
                
                if matches:
                    mappings.append({
                        'irc_code': code,
                        'irc_name': indicator['name'],
                        'current_coverage': coverage,
                        'category': indicator['category'],
                        'eia_matches': len(matches),
                        'sample_series': matches[0]['id'] if matches else None,
                        'sample_name': matches[0]['name'] if matches else None
                    })
    
    return mappings

def display_results(mappings, indicators):
    """Afficher les résultats"""
    
    print(f"\n{'='*80}")
    print("INDICATEURS IRC AVEC DONNÉES EIA DISPONIBLES")
    print(f"{'='*80}\n")
    
    # Group by category
    by_category = defaultdict(list)
    for m in mappings:
        by_category[m['category']].append(m)
    
    total_improvable = 0
    
    for cat_id in sorted(by_category.keys()):
        cat_mappings = by_category[cat_id]
        print(f"\n📊 Catégorie {cat_id}:")
        print("-" * 80)
        
        for m in cat_mappings:
            status = "✅ COMPLETE" if m['current_coverage'] >= 200 else "⚠️  FAIBLE"
            if m['current_coverage'] < 200:
                total_improvable += 1
            
            print(f"\n{m['irc_code']:20s} | {status}")
            print(f"   Nom: {m['irc_name'][:60]}")
            print(f"   Couverture actuelle: {m['current_coverage']} pays")
            print(f"   EIA matches: {m['eia_matches']} series")
            if m['sample_series']:
                print(f"   Sample: {m['sample_series']}")
                print(f"           {m['sample_name'][:70]}")
    
    print(f"\n{'='*80}")
    print(f"RÉSUMÉ")
    print(f"{'='*80}")
    print(f"Total indicateurs mappables: {len(mappings)}")
    print(f"Indicateurs améliorables (<200 pays): {total_improvable}")
    print(f"Indicateurs déjà excellents (≥200): {len(mappings) - total_improvable}")
    
    # Show weakest indicators without EIA match
    print(f"\n{'='*80}")
    print("INDICATEURS FAIBLES SANS CORRESPONDANCE EIA")
    print(f"{'='*80}\n")
    
    mapped_codes = {m['irc_code'] for m in mappings}
    weak_indicators = [ind for ind in indicators if ind['code'] not in mapped_codes and ind['coverage'] < 150]
    
    for ind in weak_indicators[:15]:
        print(f"{ind['code']:20s} | Cat {ind['category']} | {ind['coverage']:3d} pays | {ind['name'][:50]}")
    
    if len(weak_indicators) > 15:
        print(f"\n... et {len(weak_indicators) - 15} autres indicateurs faibles")

def main():
    print("="*80)
    print("ANALYSE EIA - IDENTIFICATION DES INDICATEURS IRC AMÉLIORABLES")
    print("="*80)
    
    # Get IRC indicators
    print("\n📋 Loading IRC indicators...")
    indicators = get_all_indicators()
    print(f"   ✅ {len(indicators)} indicators loaded")
    
    # Analyze EIA catalog
    eia_catalog = analyze_eia_bulk_series()
    
    print(f"\n📊 EIA Series by category:")
    for category, series_list in sorted(eia_catalog.items()):
        print(f"   {category:12s}: {len(series_list):4d} series")
    
    # Map IRC to EIA
    mappings = map_irc_to_eia(indicators, eia_catalog)
    
    # Display results
    display_results(mappings, indicators)
    
    print(f"\n💡 Recommandation:")
    print("   Priorité 1: Indicateurs avec <150 pays ET données EIA disponibles")
    print("   Priorité 2: Indicateurs catégorie 1 (Économie) - dette à 121 pays")

if __name__ == '__main__':
    main()
