#!/usr/bin/env python3
"""
Analyze raw tournament data excluding leagues
"""
import json
from pathlib import Path
from collections import Counter
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.archetype_parser import ArchetypeParser
from src.parsers.color_detector import ColorDetector

# Initialize parsers
archetype_parser = ArchetypeParser()
color_parser = ColorDetector()

# Count decks excluding leagues
total_decks = 0
total_tournaments = 0
archetype_counts = Counter()
all_decks = []

# MTGO - Only challenges and qualifiers
mtgo_path = Path('data/raw/mtgo/standard')
challenges = list(mtgo_path.glob('challenge/*.json'))
qualifiers = [f for f in mtgo_path.glob('*.json') if 'qualifier' in f.name.lower() and 'league' not in f.name.lower()]
mtgo_files = challenges + qualifiers

print(f'Processing {len(challenges)} MTGO Challenges...')
print(f'Processing {len(qualifiers)} MTGO Qualifiers...')

for f in mtgo_files:
    try:
        with open(f, 'r') as file:
            data = json.load(file)
            if 'decks' in data:
                total_tournaments += 1
                for deck in data['decks']:
                    total_decks += 1
                    
                    # Extract cards from mainboard
                    cards = []
                    for card in deck.get('mainboard', []):
                        cards.extend([card['card_name']] * card['count'])
                    
                    # Detect archetype
                    archetype = archetype_parser.detect_archetype(cards, 'standard')
                    if not archetype:
                        # Use color identity as fallback
                        colors = color_parser.get_deck_colors(cards)
                        archetype = color_parser.get_color_identity_name(colors)
                    
                    archetype_counts[archetype] += 1
                    all_decks.append({
                        'archetype': archetype,
                        'player': deck.get('player', 'Unknown'),
                        'result': deck.get('result', ''),
                        'tournament': data.get('name', '')
                    })
    except Exception as e:
        print(f'Error processing {f.name}: {e}')

# Melee - All tournaments  
melee_path = Path('data/raw/melee/standard')
melee_files = list(melee_path.glob('*.json'))
print(f'\\nProcessing {len(melee_files)} Melee Tournaments...')

for f in melee_files:
    try:
        with open(f, 'r') as file:
            data = json.load(file)
            if 'decks' in data:
                total_tournaments += 1
                for deck in data['decks']:
                    total_decks += 1
                    
                    # Extract cards from mainboard
                    cards = []
                    for card in deck.get('mainboard', []):
                        cards.extend([card['card_name']] * card['count'])
                    
                    # Detect archetype
                    archetype = archetype_parser.detect_archetype(cards, 'standard')
                    if not archetype:
                        # Use color identity as fallback
                        colors = color_parser.get_deck_colors(cards)
                        archetype = color_parser.get_color_identity_name(colors)
                    
                    archetype_counts[archetype] += 1
                    all_decks.append({
                        'archetype': archetype,
                        'player': deck.get('player', 'Unknown'),
                        'result': deck.get('result', ''),
                        'tournament': data.get('name', '')
                    })
    except Exception as e:
        print(f'Error processing {f.name}: {e}')

unique_archetypes = len(archetype_counts)

print(f'\\n=== RESULTS (EXCLUDING LEAGUES) ===')
print(f'TOTAL TOURNAMENTS: {total_tournaments}')
print(f'TOTAL DECKS: {total_decks}')
print(f'UNIQUE ARCHETYPES: {unique_archetypes}')
print(f'\\nTop 30 Archetypes:')

# Export data for visualization
data_for_viz = []
for arch, count in archetype_counts.most_common():
    percentage = (count / total_decks) * 100 if total_decks > 0 else 0
    print(f'{arch}: {count} decks ({percentage:.2f}%)')
    data_for_viz.append({
        'name': arch,
        'decks': count,
        'percentage': round(percentage, 2)
    })

# Save to JSON for visualization
with open('archetype_data_no_leagues.json', 'w') as f:
    json.dump({
        'total_tournaments': total_tournaments,
        'total_decks': total_decks,
        'unique_archetypes': unique_archetypes,
        'archetypes': data_for_viz
    }, f, indent=2)

print(f"\\nData saved to archetype_data_no_leagues.json")