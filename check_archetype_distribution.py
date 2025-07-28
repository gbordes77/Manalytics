#!/usr/bin/env python3
"""
Vérifie la distribution des archétypes dans le cache
"""

import json
from pathlib import Path
from collections import Counter

# Charger le cache
cache_path = Path('data/cache/decklists/2025-07.json')
with open(cache_path, 'r') as f:
    data = json.load(f)

# Compter les archétypes
archetypes = Counter()
total_decks = 0
july_tournaments = 0

for key, tournament in data.items():
    if 'standard' in key.lower() and tournament.get('format', '').lower() == 'standard':
        # Vérifier la date
        date = tournament.get('date', '')
        if '2025-07' in date and int(date[8:10]) <= 21:
            july_tournaments += 1
            for deck in tournament.get('decklists', []):
                arch = deck.get('archetype', 'Unknown')
                if arch != 'Unknown':
                    archetypes[arch] += 1
                    total_decks += 1

print(f'Tournois Standard Juillet 1-21: {july_tournaments}')
print(f'Total decks: {total_decks}')
print(f'\nTop 20 archetypes:')
for arch, count in archetypes.most_common(20):
    pct = (count / total_decks * 100) if total_decks > 0 else 0
    print(f'{arch}: {count} decks ({pct:.1f}%)')

# Vérifier les Unknown
unknown_count = 0
for key, tournament in data.items():
    if 'standard' in key.lower() and tournament.get('format', '').lower() == 'standard':
        date = tournament.get('date', '')
        if '2025-07' in date and int(date[8:10]) <= 21:
            for deck in tournament.get('decklists', []):
                if deck.get('archetype') == 'Unknown' or not deck.get('archetype'):
                    unknown_count += 1

print(f'\nUnknown archetypes: {unknown_count}')