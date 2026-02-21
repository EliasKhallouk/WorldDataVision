#!/bin/bash
# Script simple pour relancer l'import et afficher le résultat

cd /home/elias/PROJECT/WorldDataVision/backend/scripts

echo "🔄 Relancement de l'import IMF avec mapping amélioré..."
echo ""

python3 import_imf_debt_data.py

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 Résultat dans la base de données:"
echo "═══════════════════════════════════════════════════════════"

psql -U elias -d worlddatavision -c "
SELECT 
    COUNT(DISTINCT country_id) as nb_pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as total_valeurs
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS';"
