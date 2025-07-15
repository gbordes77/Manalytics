#!/bin/bash
echo "🚀 Activation environnement Manalytics"
source venv/bin/activate
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "✅ Environnement configuré"
echo "Usage: python3 run_full_pipeline.py --format Standard --start-date 2025-07-01 --end-date 2025-07-07"
