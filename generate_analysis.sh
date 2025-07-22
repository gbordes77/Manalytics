#!/bin/bash

# Script pour générer facilement des analyses MTG
# Usage: ./generate_analysis.sh [format] [jours]

# Valeurs par défaut
FORMAT=${1:-standard}
DAYS=${2:-7}

# Calculer les dates
END_DATE=$(date +%Y-%m-%d)
START_DATE=$(date -v-${DAYS}d +%Y-%m-%d)

echo "🃏 Génération d'analyse pour le format $FORMAT"
echo "📅 Période: $START_DATE à $END_DATE ($DAYS jours)"
echo ""

# Exécuter l'orchestrateur
python3 orchestrator.py --format $FORMAT --start-date $START_DATE --end-date $END_DATE --verbose

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo "✅ Analyse générée avec succès!"
else
    echo "❌ Erreur lors de la génération de l'analyse."
    exit 1
fi