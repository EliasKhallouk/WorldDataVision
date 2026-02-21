#!/usr/bin/env python3
"""
Script de test simple : affiche les premières lignes du CSV IMF
"""

import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '../../Data/IRC/imf-dm-export-20260221.csv')
    
    print(f"📂 Fichier: {csv_path}")
    print(f"📏 Taille: {os.path.getsize(csv_path):,} octets\n")
    
    print("═" * 80)
    print("📊 Premières 5 lignes du fichier CSV :")
    print("═" * 80)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            
            # Tronquer si trop long
            if len(line) > 200:
                print(f"Ligne {i+1}: {line[:200]}...")
            else:
                print(f"Ligne {i+1}: {line.rstrip()}")
    
    print("═" * 80)
    
    # Compter le nombre total de lignes
    with open(csv_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"\n📈 Total de lignes dans le fichier: {total_lines}")
    print(f"📍 Pays attendus: {total_lines - 2} (en soustrayant header et ligne vide)")

if __name__ == '__main__':
    main()
