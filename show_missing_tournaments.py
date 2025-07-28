#!/usr/bin/env python3
"""
Montre EXACTEMENT quels tournois ont des matchs mais PAS de decklists
"""

import json
from pathlib import Path
from datetime import datetime

print("🔍 TOURNOIS AVEC MATCHS MAIS SANS DECKLISTS")
print("="*60)

# 1. Charger tous les tournois du listener
listener_tournaments = {}
mtgo_path = Path("data/MTGOData/2025/07")

for day in range(1, 22):
    day_folder = mtgo_path / f"{day:02d}"
    if day_folder.exists():
        for file in day_folder.glob("*standard*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                tournament_id = str(data['Tournament']['Id'])
                match_count = sum(len(r.get('Matches', [])) for r in data.get('Rounds', []))
                
                listener_tournaments[tournament_id] = {
                    'name': data['Tournament']['Name'],
                    'date': data['Tournament']['Date'][:10],
                    'matches': match_count,
                    'file': file.name
                }
            except:
                pass

print(f"✅ Trouvé {len(listener_tournaments)} tournois dans le listener avec des matchs")

# 2. Charger le cache
cache_path = Path("data/cache/decklists/2025-07.json")
with open(cache_path, 'r') as f:
    cache_data = json.load(f)

# 3. Vérifier quels tournois ont des decklists
tournaments_with_decklists = set()
for key, tournament in cache_data.items():
    if 'standard' in key.lower():
        # Extraire l'ID
        import re
        match = re.search(r'(\d{8})(?:\D|$)', str(key))
        if match:
            tid = match.group(1)
            if tid in listener_tournaments:
                deck_count = len(tournament.get('decklists', []))
                if deck_count > 0:
                    tournaments_with_decklists.add(tid)

# 4. Identifier les tournois SANS decklists
missing_decklists = []
for tid, info in listener_tournaments.items():
    if tid not in tournaments_with_decklists:
        missing_decklists.append((tid, info))

# Trier par date
missing_decklists.sort(key=lambda x: x[1]['date'])

print(f"\n❌ TOURNOIS AVEC MATCHS MAIS SANS DECKLISTS: {len(missing_decklists)}")
print("="*60)

for tid, info in missing_decklists:
    print(f"\n📋 {info['name']}")
    print(f"   Date: {info['date']}")
    print(f"   ID: {tid}")
    print(f"   Matchs: {info['matches']}")
    print(f"   URL MTGO: https://www.mtgo.com/decklist/{info['name'].lower().replace(' ', '-')}-{info['date']}{tid}")

# Calculer le total de matchs perdus
total_missing_matches = sum(info['matches'] for tid, info in missing_decklists)
print(f"\n⚠️ TOTAL MATCHS SANS DECKLISTS: {total_missing_matches}")
print(f"   Ça représente {total_missing_matches / 1167 * 100:.1f}% de matchs en plus!")

# Montrer aussi ceux qui ONT des decklists pour comparer
print(f"\n✅ TOURNOIS AVEC DECKLISTS: {len(tournaments_with_decklists)}")
for tid in list(tournaments_with_decklists)[:5]:
    if tid in listener_tournaments:
        info = listener_tournaments[tid]
        print(f"   - {info['name']} ({info['date']})")