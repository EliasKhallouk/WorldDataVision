#!/bin/bash
# Script wrapper pour exécuter l'import IMF et capturer les logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/imf_import_$(date +%Y%m%d_%H%M%S).log"

echo "🚀 Lancement de l'import des données IMF..."
echo "📝 Log file: $LOG_FILE"
echo ""

cd "$SCRIPT_DIR"

# Exécuter le script Python avec capture des logs
python3 import_imf_debt_data.py 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Import terminé avec succès!"
else
    echo "❌ Erreur lors de l'import (code: $EXIT_CODE)"
fi
echo "📝 Logs sauvegardés dans: $LOG_FILE"
echo "════════════════════════════════════════"

exit $EXIT_CODE
