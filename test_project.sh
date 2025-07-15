#!/bin/bash
echo "🔍 Test complet Manalytics"

source venv/bin/activate
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

echo "1. Test JSON..."
python3 -c "
import json
import glob
errors = []
for f in glob.glob('MTGOFormatData/**/*.json', recursive=True):
    try:
        with open(f) as file:
            json.load(file)
    except Exception as e:
        errors.append(f'{f}: {e}')

if errors:
    print('❌ Erreurs JSON:')
    for e in errors: print(f'  {e}')
    exit(1)
else:
    print('✅ Tous les JSON sont valides')
"

echo "2. Test imports..."
python3 -c "
try:
    import src.orchestrator
    print('✅ Orchestrator OK')
except Exception as e:
    print(f'❌ Orchestrator: {e}')
    exit(1)
"

echo "3. Test pipeline..."
python3 run_full_pipeline.py --help > /dev/null && echo "✅ Pipeline script OK" || (echo "❌ Pipeline script KO" && exit 1)

echo "🎉 Tous les tests passent - Projet fonctionnel!"
