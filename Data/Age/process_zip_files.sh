#!/bin/bash

# Script pour traiter les fichiers ZIP dans le dossier Age
# 1. Dézippe chaque fichier .zip
# 2. Supprime le fichier indicator
# 3. Renomme le fichier metadata en POP.[XXXX].[XX]_Metadata.csv
# 4. Renomme le fichier API en POP.[XXXX].[XX].csv

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
processed=0
errors=0

echo -e "${YELLOW}Début du traitement des fichiers ZIP...${NC}\n"

# Parcourir tous les fichiers .zip dans le répertoire courant
for zipfile in *.zip; do
    # Vérifier si des fichiers .zip existent
    if [ ! -f "$zipfile" ]; then
        echo -e "${RED}Aucun fichier ZIP trouvé${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Traitement de: $zipfile${NC}"
    
    # Extraire le code de la tranche d'âge et le genre depuis le nom du fichier
    # Format attendu: API_SP.POP.0509.FE.5Y_DS2_fr_csv_v2_*.zip
    # On extrait 0509 et FE
    if [[ $zipfile =~ API_SP\.POP\.([0-9]{4})\.(FE|MA)\.5Y ]]; then
        age_code="${BASH_REMATCH[1]}"
        gender_code="${BASH_REMATCH[2]}"
        
        echo "  Code âge: $age_code, Genre: $gender_code"
        
        # Créer un dossier temporaire pour l'extraction
        temp_dir="temp_${age_code}_${gender_code}"
        mkdir -p "$temp_dir"
        
        # Dézipper dans le dossier temporaire
        echo "  Décompression..."
        unzip -q "$zipfile" -d "$temp_dir"
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}  Erreur lors de la décompression${NC}"
            rm -rf "$temp_dir"
            ((errors++))
            continue
        fi
        
        # Supprimer le fichier indicator
        echo "  Suppression des fichiers indicator..."
        find "$temp_dir" -type f -name "*Indicator*" -delete
        find "$temp_dir" -type f -name "*indicator*" -delete
        
        # Renommer le fichier metadata
        metadata_file=$(find "$temp_dir" -type f -name "*Metadata*" -o -name "*metadata*" | head -n 1)
        if [ -n "$metadata_file" ]; then
            new_metadata_name="POP.${age_code}.${gender_code}_Metadata.csv"
            mv "$metadata_file" "$new_metadata_name"
            echo -e "  ${GREEN}Créé: $new_metadata_name${NC}"
        else
            echo -e "  ${RED}Fichier metadata non trouvé${NC}"
        fi
        
        # Renommer le fichier API
        api_file=$(find "$temp_dir" -type f -name "API_*.csv" | head -n 1)
        if [ -n "$api_file" ]; then
            new_api_name="POP.${age_code}.${gender_code}.csv"
            mv "$api_file" "$new_api_name"
            echo -e "  ${GREEN}Créé: $new_api_name${NC}"
        else
            echo -e "  ${RED}Fichier API non trouvé${NC}"
        fi
        
        # Nettoyer le dossier temporaire
        rm -rf "$temp_dir"
        
        # Optionnel : supprimer le fichier ZIP après traitement
        # Décommentez la ligne suivante si vous voulez supprimer les ZIP
        # rm "$zipfile"
        
        ((processed++))
        echo -e "${GREEN}  ✓ Traitement terminé${NC}\n"
        
    else
        echo -e "${RED}  Format de nom de fichier non reconnu${NC}\n"
        ((errors++))
    fi
done

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${GREEN}Fichiers traités avec succès: $processed${NC}"
if [ $errors -gt 0 ]; then
    echo -e "${RED}Erreurs rencontrées: $errors${NC}"
fi
echo -e "${YELLOW}========================================${NC}"
