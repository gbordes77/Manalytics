#!/bin/bash
# Auto-refresh du pipeline toutes les heures

echo "🔄 Auto-refresh Manalytics démarré..."
echo "📅 Période : 1-15 juillet 2025"
echo "⏰ Refresh toutes les heures"
echo "🛑 Ctrl+C pour arrêter"

while true; do
    echo "🚀 $(date): Lancement pipeline..."
    python3 run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-15

    if [ $? -eq 0 ]; then
        echo "✅ $(date): Pipeline terminé avec succès"
        # Ouvrir automatiquement le résultat
        open Analyses/standard_analysis_2025-07-01_2025-07-15/standard_2025-07-01_2025-07-15.html
    else
        echo "❌ $(date): Erreur dans le pipeline"
    fi

    echo "😴 Attente 1 heure..."
    sleep 3600  # 1 heure
done
