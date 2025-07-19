#!/bin/bash
# Créer un raccourci clavier pour Manalytics

echo "⌨️  Configuration raccourci clavier macOS..."

# Créer un script AppleScript
cat > /tmp/manalytics_shortcut.scpt << 'EOF'
tell application "Terminal"
    activate
    do script "cd /Volumes/DataDisk/_Projects/Manalytics && python3 run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-15"
end tell
EOF

# Compiler le script
osacompile -o ~/Desktop/Manalytics.app /tmp/manalytics_shortcut.scpt

echo "✅ Application créée sur le Bureau : Manalytics.app"
echo "🎯 UTILISATION :"
echo "  1. Double-clic sur Manalytics.app"
echo "  2. Ou glisser dans le Dock"
echo "  3. Ou assigner un raccourci clavier dans Préférences Système"
