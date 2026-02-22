#!/usr/bin/env python3
"""
Import EIA (Energy Information Administration) data for EG.USE.COMM.FO.ZS
Semantic: Fossil fuels in TOTAL primary energy consumption (not electricity)

EIA API Documentation: https://www.eia.gov/opendata/
Free API key required: https://www.eia.gov/opendata/register.php
"""

import psycopg2
import requests
import json
import time
from datetime import datetime

def connect_db():
    return psycopg2.connect(
        dbname="worlddatavision",
        user="elias",
        password="MaBaseDeDonnee",
        host="localhost"
    )

def get_country_id(cursor, iso3_code):
    """Get country ID from ISO3 code"""
    cursor.execute("SELECT id FROM country WHERE iso3 = %s", (iso3_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_indicator_id(cursor, indicator_code):
    """Get indicator ID"""
    cursor.execute("SELECT id FROM indicator WHERE code = %s", (indicator_code,))
    result = cursor.fetchone()
    return result[0] if result else None

def value_exists(cursor, country_id, indicator_id, year):
    """Check if value already exists"""
    cursor.execute("""
        SELECT value FROM indicator_value 
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (country_id, indicator_id, year))
    return cursor.fetchone()

def insert_or_average(cursor, country_id, indicator_id, year, new_value):
    """Insert new value or average with existing"""
    existing = value_exists(cursor, country_id, indicator_id, year)
    
    if existing:
        avg_value = (existing[0] + new_value) / 2
        cursor.execute("""
            UPDATE indicator_value 
            SET value = %s 
            WHERE country_id = %s AND indicator_id = %s AND year = %s
        """, (avg_value, country_id, indicator_id, year))
        return 'averaged'
    else:
        cursor.execute("""
            INSERT INTO indicator_value (country_id, indicator_id, year, value)
            VALUES (%s, %s, %s, %s)
        """, (country_id, indicator_id, year, new_value))
        return 'new'

def get_eia_fossil_data(api_key):
    """
    Get fossil fuel share from EIA API
    
    EIA provides detailed energy statistics by country
    We need to calculate: (Coal + Oil + Gas) / Total Primary Energy * 100
    """
    
    print("\n📥 Downloading EIA International Energy Data...")
    
    # EIA API endpoint for international data
    base_url = "https://api.eia.gov/v2/international/data/"
    
    # Headers with API key
    headers = {
        'X-Params': json.dumps({
            'api_key': api_key,
            'frequency': 'annual',
            'data': ['value'],
            'facets': {},
            'start': '1980',
            'end': '2023',
            'sort': [{'column': 'period', 'direction': 'desc'}],
            'offset': 0,
            'length': 5000
        })
    }
    
    all_data = []
    
    # We need multiple series:
    # - Total primary energy consumption
    # - Coal consumption
    # - Oil consumption  
    # - Natural gas consumption
    
    product_codes = {
        'INTL.44-1-AFRC-QBTU.A': 'coal',  # Coal consumption
        'INTL.44-1-ASOC-QBTU.A': 'oil',   # Petroleum consumption
        'INTL.44-1-NGRC-QBTU.A': 'gas',   # Natural gas consumption
        'INTL.44-1-TPEC-QBTU.A': 'total'  # Total primary energy
    }
    
    print("   ⚠️  Note: EIA API structure may have changed")
    print("   📝 Alternative: Use EIA bulk data files")
    print("\n   Trying API call...")
    
    try:
        response = requests.get(base_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response received")
            print(f"   Data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            # Save raw response for debugging
            with open('/tmp/eia_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"   💾 Raw response saved to /tmp/eia_response.json")
            
            return data
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def download_eia_bulk_files():
    """
    Alternative: Download EIA bulk data files
    These contain all international energy statistics
    """
    print("\n📥 Downloading EIA International Energy Statistics (Bulk File)...")
    
    # EIA provides bulk downloads of international data
    bulk_url = "https://api.eia.gov/bulk/INTL.zip"
    
    print(f"   URL: {bulk_url}")
    print("   ⚠️  File size: ~50-100 MB")
    print("   This will take a moment...")
    
    try:
        response = requests.get(bulk_url, timeout=60, stream=True)
        
        if response.status_code == 200:
            import zipfile
            import io
            
            # Save to file
            zip_path = '/tmp/eia_intl.zip'
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   ✅ Downloaded to {zip_path}")
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('/tmp/eia_data/')
            
            print(f"   ✅ Extracted to /tmp/eia_data/")
            
            # List files
            import os
            files = os.listdir('/tmp/eia_data/')
            print(f"   📁 Files: {files}")
            
            return True
        else:
            print(f"   ❌ Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_source(cursor, indicator_code, new_source):
    """Update indicator source"""
    cursor.execute("""
        SELECT source FROM indicator WHERE code = %s
    """, (indicator_code,))
    result = cursor.fetchone()
    
    if result:
        current_source = result[0]
        
        # Check if EIA already in source
        if 'EIA' in current_source or 'Energy Information Administration' in current_source:
            print(f"   ℹ️  EIA already in source: {current_source}")
            return current_source
        
        # Add EIA to source
        updated_source = f"{current_source} + {new_source}"
        
        cursor.execute("""
            UPDATE indicator SET source = %s WHERE code = %s
        """, (updated_source, indicator_code))
        
        print(f"   ✅ Source updated:")
        print(f"      Before: {current_source}")
        print(f"      After: {updated_source}")
        
        return updated_source
    
    return None

def main():
    print("="*80)
    print("EIA (US ENERGY INFORMATION ADMINISTRATION) - IMPORT")
    print("Fossil fuels in TOTAL primary energy (not electricity)")
    print("="*80)
    
    print("\n📋 EIA API Key Required")
    print("   1. Go to: https://www.eia.gov/opendata/register.php")
    print("   2. Register (free, instant)")
    print("   3. Get your API key")
    print()
    
    api_key = input("Enter your EIA API key (or 'skip' to try bulk download): ").strip()
    
    if api_key.lower() == 'skip':
        print("\n🔄 Using bulk download method instead...")
        success = download_eia_bulk_files()
        
        if success:
            print("\n✅ EIA data downloaded!")
            print("   📁 Location: /tmp/eia_data/")
            print("\n💡 Next steps:")
            print("   1. Parse the JSON file to extract fossil fuel data")
            print("   2. Calculate fossil % for each country/year")
            print("   3. Import into database")
            print("\n⚠️  This requires custom parsing script (bulk file is complex)")
        else:
            print("\n❌ Bulk download failed")
            print("   Please get an API key from https://www.eia.gov/opendata/register.php")
        
        return
    
    if not api_key or len(api_key) < 10:
        print("❌ Invalid API key")
        return
    
    # Test API key with simple request
    data = get_eia_fossil_data(api_key)
    
    if data:
        print("\n✅ EIA API working!")
        print("\n📊 Next: Parse response and calculate fossil %")
        print("   Check /tmp/eia_response.json for data structure")
        
        # Update source
        conn = connect_db()
        cursor = conn.cursor()
        
        update_source(cursor, 'EG.USE.COMM.FO.ZS', 'EIA (US Energy Information Administration)')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n💡 To complete import:")
        print("   1. Analyze /tmp/eia_response.json structure")
        print("   2. Extract country, year, fossil % data")
        print("   3. Map to database format")
        print("   4. Import values")
    else:
        print("\n❌ EIA API call failed")
        print("   Check your API key")
        print("   Or try bulk download method")

if __name__ == '__main__':
    main()
