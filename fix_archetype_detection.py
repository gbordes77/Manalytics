#!/usr/bin/env python3
"""
Comprendre et corriger le problème de détection d'archétypes
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

print("🔧 DIAGNOSTIC COMPLET DU PROBLÈME")
print("="*50)

# 1. Vérifier combien de tournois ont des decklists
cache_path = Path("data/cache/decklists/2025-07.json")
with open(cache_path, 'r') as f:
    cache_data = json.load(f)

mtgo_with_decks = 0
melee_with_decks = 0
total_standard_july = 0

for key, tournament in cache_data.items():
    if 'standard' in key.lower():
        date = tournament.get('date', '')
        if '2025-07' in date and date[8:10] and int(date[8:10]) <= 21:
            total_standard_july += 1
            deck_count = len(tournament.get('decklists', []))
            
            if deck_count > 0:
                if 'melee' in key.lower() or 'TheGathering' in key:
                    melee_with_decks += 1
                else:
                    mtgo_with_decks += 1

print(f"📊 TOURNOIS STANDARD JUILLET 1-21:")
print(f"  - Total dans le cache: {total_standard_july}")
print(f"  - MTGO avec decklists: {mtgo_with_decks}")
print(f"  - Melee avec decklists: {melee_with_decks}")
print(f"  - Sans decklists: {total_standard_july - mtgo_with_decks - melee_with_decks}")

# 2. Analyser pourquoi les tournois MTGO n'ont pas de decks
print("\n🔍 TOURNOIS MTGO SANS DECKS:")
empty_mtgo = []
for key, tournament in cache_data.items():
    if 'standard' in key.lower() and 'challenge' in key.lower():
        date = tournament.get('date', '')
        if '2025-07' in date and date[8:10] and int(date[8:10]) <= 21:
            if len(tournament.get('decklists', [])) == 0:
                empty_mtgo.append(key)

for key in empty_mtgo[:5]:
    print(f"  - {key}")

# 3. Le VRAI problème : on analyse les MATCHS pas les DECKS
print("\n⚠️ LE VRAI PROBLÈME:")
print("Notre analyse compte les MATCHS, pas les DECKS!")
print("Si Dimir a joué plus de rounds/matchs, il sera surreprésenté")

# 4. Calculer la vraie distribution par DECKS UNIQUES
print("\n📊 VRAIE DISTRIBUTION (par DECKS, pas MATCHS):")

deck_archetypes = Counter()
player_archetypes = {}  # Pour éviter les doublons

for key, tournament in cache_data.items():
    if 'standard' in key.lower():
        date = tournament.get('date', '')
        if '2025-07' in date and date[8:10] and int(date[8:10]) <= 21:
            for deck in tournament.get('decklists', []):
                player = deck.get('player')
                arch = deck.get('archetype')
                
                if player and arch and arch not in ['Unknown', 'None', None, '']:
                    # Un joueur = un deck (éviter les doublons)
                    if player not in player_archetypes:
                        player_archetypes[player] = arch
                        deck_archetypes[arch] += 1

total_unique_decks = sum(deck_archetypes.values())
print(f"\nTotal decks uniques avec archétype: {total_unique_decks}")
print("\nDistribution réelle:")
for arch, count in deck_archetypes.most_common(15):
    pct = (count / total_unique_decks * 100) if total_unique_decks > 0 else 0
    print(f"  - {arch}: {count} decks ({pct:.1f}%)")

# 5. Recommandations
print("\n💡 RECOMMANDATIONS:")
print("1. Scraper TOUS les tournois MTGO (pas seulement Melee)")
print("2. S'assurer que le cache contient les decklists")
print("3. Améliorer la détection d'archétypes (trop de None)")
print("4. Pour l'analyse du meta, utiliser les DECKS pas les MATCHS")