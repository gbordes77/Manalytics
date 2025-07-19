#!/bin/bash
# Script pour configurer les alias Manalytics

echo "🚀 Configuration des alias Manalytics..."

# Ajouter les alias au .zshrc
cat >> ~/.zshrc << 'EOF'

# === MANALYTICS ALIASES ===
alias mana-test="cd /Volumes/DataDisk/_Projects/Manalytics && python3 run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-15"
alias mana-quick="cd /Volumes/DataDisk/_Projects/Manalytics && python3 run_full_pipeline.py --format Standard --start-date 2025-07-14 --end-date 2025-07-15"
alias mana-full="cd /Volumes/DataDisk/_Projects/Manalytics && python3 run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-15 && open Analyses/standard_analysis_2025-07-01_2025-07-15/standard_2025-07-01_2025-07-15.html"
alias mana-cd="cd /Volumes/DataDisk/_Projects/Manalytics"
alias mana-logs="cd /Volumes/DataDisk/_Projects/Manalytics && tail -f pipeline.log"

EOF

echo "✅ Alias ajoutés à ~/.zshrc"
echo "🔄 Rechargement du shell..."
source ~/.zshrc

echo "🎯 UTILISATION :"
echo "  mana-test   : Test rapide période de référence"
echo "  mana-quick  : Test ultra-rapide (2 jours)"
echo "  mana-full   : Analyse complète + ouverture auto"
echo "  mana-cd     : Aller dans le dossier projet"
echo "  mana-logs   : Voir les logs en temps réel"
