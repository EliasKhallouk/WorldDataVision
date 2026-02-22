#!/bin/bash
"""
Script pour télécharger automatiquement les datasets Our World in Data
nécessaires pour compléter les indicateurs IRC.
"""

# Créer le dossier OWID
OWID_DIR="/home/elias/PROJECT/WorldDataVision/Data/IRC/OWID"
mkdir -p "$OWID_DIR"

echo "📥 Téléchargement des datasets Our World in Data..."
echo "Dossier de destination: $OWID_DIR"
echo ""

# URL de base GitHub OWID
OWID_BASE="https://raw.githubusercontent.com/owid/owid-datasets/master/datasets"

# Liste des datasets à télécharger
# Format: "nom_du_dataset|nom_fichier_csv|description"
DATASETS=(
    "Literacy rates - World Bank (2015)|literacy-rates-among-adults.csv|Taux d'alphabétisation adultes"
    "Researchers in R&D - World Bank|researchers-in-rd-per-million-people.csv|Chercheurs en R&D"
    "Research and development expenditure - World Bank|research-and-development-expenditure-of-gdp.csv|Dépenses R&D"
    "Electricity consumption - BP Statistical Review|per-capita-electricity-use.csv|Consommation électricité"
    "Primary energy consumption - BP Statistical Review|per-capita-energy-use.csv|Consommation énergétique"
    "Cereal yield - FAO|cereal-yield.csv|Rendement céréales"
    "Water stress - FAO AQUASTAT|water-stress.csv|Stress hydrique"
    "Military expenditure - SIPRI|military-expenditure-as-a-share-of-gdp.csv|Dépenses militaires"
    "Energy imports - World Bank|energy-imports-as-a-share-of-energy-use.csv|Importations énergie"
    "Fossil fuels - BP Statistical Review|fossil-fuels-share-energy.csv|Combustibles fossiles"
    "Patent applications - World Bank|patent-applications-by-residents.csv|Brevets résidents"
    "Tax revenues - ICTD|total-tax-revenue-gdp.csv|Revenus fiscaux"
)

download_count=0
error_count=0

for dataset in "${DATASETS[@]}"; do
    IFS='|' read -r folder filename description <<< "$dataset"
    
    # Essayer plusieurs URL possibles
    urls=(
        "$OWID_BASE/$folder/datapoints/datapoints.csv"
        "$OWID_BASE/$folder/$filename"
        "https://catalog.ourworldindata.org/explorers/wb/latest/world_bank_pip/$filename"
    )
    
    echo "📊 $description ($filename)..."
    
    downloaded=false
    for url in "${urls[@]}"; do
        if curl -f -s -L "$url" -o "$OWID_DIR/$filename" 2>/dev/null; then
            # Vérifier que le fichier n'est pas vide et contient des données
            if [ -s "$OWID_DIR/$filename" ] && head -1 "$OWID_DIR/$filename" | grep -q "Entity\|Code\|Year"; then
                file_size=$(du -h "$OWID_DIR/$filename" | cut -f1)
                echo "   ✅ Téléchargé ($file_size)"
                ((download_count++))
                downloaded=true
                break
            fi
        fi
    done
    
    if [ "$downloaded" = false ]; then
        echo "   ⚠️ Échec du téléchargement - À télécharger manuellement"
        echo "      URL: https://ourworldindata.org/grapher/$filename"
        ((error_count++))
    fi
done

echo ""
echo "="================================================================
echo "📊 RÉSUMÉ DU TÉLÉCHARGEMENT"
echo "================================================================="
echo "✅ Fichiers téléchargés: $download_count"
echo "⚠️ Fichiers à télécharger manuellement: $error_count"
echo ""

if [ $error_count -gt 0 ]; then
    echo "⚠️ Certains fichiers n'ont pas pu être téléchargés automatiquement."
    echo "Veuillez les télécharger manuellement depuis:"
    echo "https://ourworldindata.org/charts"
    echo ""
    echo "Pour chaque dataset:"
    echo "1. Rechercher l'indicateur sur ourworldindata.org"
    echo "2. Cliquer sur 'Download' → 'Full data (CSV)'"
    echo "3. Sauvegarder dans: $OWID_DIR"
fi

echo ""
echo "📁 Fichiers dans $OWID_DIR:"
ls -lh "$OWID_DIR" 2>/dev/null || echo "   (vide)"
