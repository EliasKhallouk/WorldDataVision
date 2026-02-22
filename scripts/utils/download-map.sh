#!/bin/bash

# Script pour télécharger la carte SVG du monde
# Ce script est appelé automatiquement par setup.sh

echo "📥 Téléchargement de la carte SVG du monde..."

# Créer le dossier si nécessaire
mkdir -p frontend/public

# Télécharger la carte
curl -L -o frontend/public/world-map.svg \
  "https://raw.githubusercontent.com/raphaellepuschitz/SVG-World-Map/master/world.svg" \
  2>/dev/null

if [ $? -eq 0 ] && [ -f "frontend/public/world-map.svg" ]; then
  echo "✅ Carte SVG téléchargée avec succès !"
  
  # Afficher quelques infos sur le fichier
  FILE_SIZE=$(du -h frontend/public/world-map.svg | cut -f1)
  echo "   Taille du fichier: $FILE_SIZE"
  
  # Vérifier que c'est un fichier SVG valide
  if head -n 1 frontend/public/world-map.svg | grep -q "svg"; then
    echo "   Format: SVG valide ✓"
  else
    echo "   ⚠️  Le fichier pourrait ne pas être un SVG valide"
  fi
else
  echo "❌ Échec du téléchargement"
  echo ""
  echo "📝 Téléchargement manuel requis:"
  echo "1. Visitez: https://github.com/raphaellepuschitz/SVG-World-Map"
  echo "2. Téléchargez le fichier 'world.svg'"
  echo "3. Placez-le dans: frontend/public/world-map.svg"
  exit 1
fi
