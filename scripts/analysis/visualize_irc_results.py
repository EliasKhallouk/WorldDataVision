#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualisation des résultats IRC
Version 1.0 - 28 février 2026

Ce script génère des visualisations et des rapports sur les résultats IRC :
- Carte mondiale IRC
- Distribution des scores
- Analyse par pilier
- Comparaisons régionales
- Top/Bottom pays
"""

import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 11


def connect_db():
    """Connexion à la base de données"""
    return psycopg2.connect(dbname='worlddatavision', user='elias')


def load_irc_results(conn, year=2020):
    """Charge les résultats IRC depuis la base"""
    query = """
    SELECT 
        c.iso3,
        c.name,
        c.region,
        ir.irc_score,
        ir.irc_rank,
        ir.demographie_score,
        ir.economie_score,
        ir.gouvernance_score,
        ir.capital_humain_score,
        ir.souverainete_materielle_score,
        ir.innovation_score,
        ir.environnement_score
    FROM irc_results ir
    JOIN country c ON ir.country_id = c.id
    WHERE ir.year = %s
    ORDER BY ir.irc_rank;
    """
    
    df = pd.read_sql(query, conn, params=(year,))
    print(f"✅ {len(df)} pays chargés pour l'année {year}")
    return df


def plot_irc_distribution(df):
    """Histogramme de distribution des scores IRC"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Histogramme
    ax1.hist(df['irc_score'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(df['irc_score'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Moyenne: {df["irc_score"].mean():.2f}')
    ax1.axvline(df['irc_score'].median(), color='green', linestyle='--', 
                linewidth=2, label=f'Médiane: {df["irc_score"].median():.2f}')
    ax1.set_xlabel('Score IRC (/100)')
    ax1.set_ylabel('Nombre de pays')
    ax1.set_title('Distribution des Scores IRC 2020', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Boxplot par région
    regions_data = df.groupby('region')['irc_score'].apply(list).to_dict()
    regions_sorted = sorted(regions_data.items(), key=lambda x: np.median(x[1]), reverse=True)
    
    ax2.boxplot([x[1] for x in regions_sorted], labels=[x[0][:15] for x in regions_sorted])
    ax2.set_xlabel('Région')
    ax2.set_ylabel('Score IRC (/100)')
    ax2.set_title('Distribution IRC par Région', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/elias/PROJECT/WorldDataVision/irc_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique sauvegardé : irc_distribution.png")
    plt.show()


def plot_pillars_analysis(df):
    """Analyse des piliers IRC"""
    # Préparer les données
    pillars = ['demographie_score', 'economie_score', 'gouvernance_score', 
               'capital_humain_score', 'souverainete_materielle_score', 
               'innovation_score', 'environnement_score']
    pillar_names = ['Démographie', 'Économie', 'Gouvernance', 'Capital Humain',
                    'Souveraineté Mat.', 'Innovation', 'Environnement']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    # Radar chart pour le top 5
    top5 = df.nlargest(5, 'irc_score')
    
    angles = np.linspace(0, 2 * np.pi, len(pillars), endpoint=False).tolist()
    angles += angles[:1]  # Fermer le cercle
    
    ax1 = plt.subplot(121, projection='polar')
    colors = plt.cm.Set2(range(5))
    
    for idx, (_, country) in enumerate(top5.iterrows()):
        values = [country[p] for p in pillars]
        values += values[:1]  # Fermer le cercle
        ax1.plot(angles, values, 'o-', linewidth=2, label=country['name'], color=colors[idx])
        ax1.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(pillar_names, size=10)
    ax1.set_ylim(0, 100)
    ax1.set_title('Profils des 5 Premiers Pays IRC 2020', fontsize=14, fontweight='bold', pad=20)
    ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax1.grid(True)
    
    # Heatmap des corrélations piliers
    ax2 = plt.subplot(122)
    corr_matrix = df[pillars].corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                xticklabels=pillar_names, yticklabels=pillar_names,
                center=0, vmin=-1, vmax=1, ax=ax2, cbar_kws={'label': 'Corrélation'})
    ax2.set_title('Corrélations entre Piliers IRC', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/elias/PROJECT/WorldDataVision/irc_pillars.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique sauvegardé : irc_pillars.png")
    plt.show()


def plot_top_bottom(df):
    """Graphiques top et bottom pays"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Top 20
    top20 = df.nlargest(20, 'irc_score')
    colors_top = plt.cm.Greens(np.linspace(0.4, 0.9, 20))
    ax1.barh(range(20), top20['irc_score'].values, color=colors_top, edgecolor='black')
    ax1.set_yticks(range(20))
    ax1.set_yticklabels(top20['name'].values, fontsize=9)
    ax1.set_xlabel('Score IRC (/100)', fontsize=12)
    ax1.set_title('TOP 20 - Index de Résilience Civilisationnelle 2020', 
                  fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    ax1.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(top20['irc_score'].values):
        ax1.text(v + 0.5, i, f'{v:.1f}', va='center', fontsize=8)
    
    # Bottom 20
    bottom20 = df.nsmallest(20, 'irc_score')
    colors_bottom = plt.cm.Reds(np.linspace(0.4, 0.9, 20))
    ax2.barh(range(20), bottom20['irc_score'].values, color=colors_bottom, edgecolor='black')
    ax2.set_yticks(range(20))
    ax2.set_yticklabels(bottom20['name'].values, fontsize=9)
    ax2.set_xlabel('Score IRC (/100)', fontsize=12)
    ax2.set_title('BOTTOM 20 - Index de Résilience Civilisationnelle 2020', 
                  fontsize=14, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(bottom20['irc_score'].values):
        ax2.text(v + 0.5, i, f'{v:.1f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('/home/elias/PROJECT/WorldDataVision/irc_top_bottom.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique sauvegardé : irc_top_bottom.png")
    plt.show()


def generate_summary_report(df):
    """Génère un rapport résumé en texte"""
    report = f"""
═══════════════════════════════════════════════════════════════════
    INDEX DE RÉSILIENCE CIVILISATIONNELLE (IRC) - RAPPORT 2020
═══════════════════════════════════════════════════════════════════

📊 STATISTIQUES GLOBALES
───────────────────────────────────────────────────────────────────
  • Pays analysés : {len(df)}
  • Score moyen : {df['irc_score'].mean():.2f}/100
  • Score médian : {df['irc_score'].median():.2f}/100
  • Écart-type : {df['irc_score'].std():.2f}
  • Score minimum : {df['irc_score'].min():.2f}/100 ({df.loc[df['irc_score'].idxmin(), 'name']})
  • Score maximum : {df['irc_score'].max():.2f}/100 ({df.loc[df['irc_score'].idxmax(), 'name']})

🏆 TOP 10 PAYS
───────────────────────────────────────────────────────────────────
"""
    
    for i, (_, row) in enumerate(df.nlargest(10, 'irc_score').iterrows(), 1):
        report += f"  {i:2d}. {row['name']:<30s} {row['irc_score']:6.2f}/100\n"
    
    report += f"""
⚠️  BOTTOM 10 PAYS
───────────────────────────────────────────────────────────────────
"""
    
    for i, (_, row) in enumerate(df.nsmallest(10, 'irc_score').iterrows(), 1):
        report += f"  {i:2d}. {row['name']:<30s} {row['irc_score']:6.2f}/100\n"
    
    report += f"""
📈 ANALYSE PAR PILIER (moyennes)
───────────────────────────────────────────────────────────────────
  • Démographie : {df['demographie_score'].mean():.2f}/100
  • Économie : {df['economie_score'].mean():.2f}/100
  • Gouvernance : {df['gouvernance_score'].mean():.2f}/100
  • Capital Humain : {df['capital_humain_score'].mean():.2f}/100
  • Souveraineté Matérielle : {df['souverainete_materielle_score'].mean():.2f}/100
  • Innovation : {df['innovation_score'].mean():.2f}/100
  • Environnement : {df['environnement_score'].mean():.2f}/100

🌍 DISTRIBUTION PAR RÉGION
───────────────────────────────────────────────────────────────────
"""
    
    for region in df.groupby('region')['irc_score'].mean().sort_values(ascending=False).index:
        region_data = df[df['region'] == region]
        report += f"  • {region:<40s} : {region_data['irc_score'].mean():6.2f}/100 ({len(region_data)} pays)\n"
    
    report += f"""
═══════════════════════════════════════════════════════════════════
Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
═══════════════════════════════════════════════════════════════════
"""
    
    # Sauvegarder
    with open('/home/elias/PROJECT/WorldDataVision/IRC_RAPPORT_2020.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print("\n✅ Rapport sauvegardé : IRC_RAPPORT_2020.txt")


def main():
    """Fonction principale"""
    print("=" * 70)
    print("VISUALISATION DES RÉSULTATS IRC 2020")
    print("=" * 70)
    
    # Connexion
    conn = connect_db()
    
    # Charger les données
    df = load_irc_results(conn, 2020)
    
    # Générer les visualisations
    print("\n📊 Génération des visualisations...")
    plot_irc_distribution(df)
    plot_pillars_analysis(df)
    plot_top_bottom(df)
    
    # Générer le rapport
    print("\n📝 Génération du rapport...")
    generate_summary_report(df)
    
    print("\n✅ Visualisations et rapport terminés !")
    
    conn.close()


if __name__ == "__main__":
    main()
