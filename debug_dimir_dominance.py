#!/usr/bin/env python3
"""
Debug pourquoi Dimir Midrange domine à 50%
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

# Charger listener data
listener_data = {}
mtgo_path = Path("data/MTGOData/2025/07")

print("🔍 ANALYSE DE LA DOMINANCE DIMIR")
print("="*50)

# Charger quelques tournois listener
tournament_count = 0
for day in range(1, 22):
    day_folder = mtgo_path / f"{day:02d}"
    if day_folder.exists():
        for file in day_folder.glob("*standard*.json"):
            if tournament_count < 5:  # Analyser 5 tournois
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    tournament_id = str(data['Tournament']['Id'])
                    tournament_name = data['Tournament']['Name']
                    
                    # Compter les joueurs
                    players = set()
                    for round_data in data.get('Rounds', []):
                        for match in round_data.get('Matches', []):
                            players.add(match['Player1'])
                            if match['Player2'] != "BYE":
                                players.add(match['Player2'])
                    
                    print(f"\n📋 Tournoi: {tournament_name}")
                    print(f"   ID: {tournament_id}")
                    print(f"   Joueurs uniques: {len(players)}")
                    
                    tournament_count += 1
                    
                except Exception as e:
                    print(f"Erreur: {e}")

# Maintenant vérifier le cache
print("\n" + "="*50)
print("📦 ANALYSE DU CACHE")

cache_path = Path("data/cache/decklists/2025-07.json")
with open(cache_path, 'r') as f:
    cache_data = json.load(f)

# Analyser quelques tournois
analyzed = 0
archetype_examples = defaultdict(list)

for key, tournament in cache_data.items():
    if 'standard' in key.lower() and analyzed < 5:
        date = tournament.get('date', '')
        if '2025-07' in date and int(date[8:10]) <= 21:
            print(f"\n🎯 Cache: {key}")
            print(f"   Decks: {len(tournament.get('decklists', []))}")
            
            # Compter les archétypes
            arch_count = Counter()
            for deck in tournament.get('decklists', []):
                arch = deck.get('archetype')
                arch_count[arch] += 1
                
                # Garder des exemples de joueurs par archétype
                if arch and len(archetype_examples[arch]) < 3:
                    archetype_examples[arch].append({
                        'player': deck.get('player'),
                        'tournament': key
                    })
            
            print("   Distribution:")
            for arch, count in arch_count.most_common():
                pct = (count / len(tournament.get('decklists', [])) * 100)
                print(f"     - {arch}: {count} ({pct:.1f}%)")
            
            analyzed += 1

# Afficher des exemples de joueurs Dimir
print("\n" + "="*50)
print("🎴 EXEMPLES DE JOUEURS DIMIR MIDRANGE:")
for example in archetype_examples.get('Dimir Midrange', [])[:5]:
    print(f"  - {example['player']} dans {example['tournament']}")

# Vérifier si c'est un problème de détection
print("\n" + "="*50)
print("💡 HYPOTHÈSES:")
print("1. Bug dans la détection d'archétypes (trop de decks classés Dimir)")
print("2. Données corrompues ou mal parsées")
print("3. Vraiment 50% du meta (très improbable!)")

# Compter TOUS les archétypes sur juillet 1-21
total_arch_count = Counter()
total_decks = 0

for key, tournament in cache_data.items():
    if 'standard' in key.lower():
        date = tournament.get('date', '')
        if '2025-07' in date and int(date[8:10]) <= 21:
            for deck in tournament.get('decklists', []):
                arch = deck.get('archetype')
                if arch and arch != 'Unknown':
                    total_arch_count[arch] += 1
                    total_decks += 1

print(f"\n📊 DISTRIBUTION GLOBALE (tous les decks avec archétype connu):")
print(f"Total: {total_decks} decks")
for arch, count in total_arch_count.most_common(15):
    pct = (count / total_decks * 100) if total_decks > 0 else 0
    print(f"  - {arch}: {count} ({pct:.1f}%)")