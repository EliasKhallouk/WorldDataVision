#!/usr/bin/env python3
"""Script wrapper simple pour exécuter l'import et afficher les résultats."""
import subprocess
import sys

try:
    result = subprocess.run(
        ['python3', '/home/elias/PROJECT/WorldDataVision/backend/scripts/import_imf_debt_data.py'],
        cwd='/home/elias/PROJECT/WorldDataVision/backend/scripts',
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    sys.exit(result.returncode)
    
except subprocess.TimeoutExpired:
    print("ERROR: Script timeout after 120 seconds")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
