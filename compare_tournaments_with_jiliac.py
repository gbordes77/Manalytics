#!/usr/bin/env python3
"""
Compare les tournois utilisés par Jiliac vs notre analyse
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import re

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase

def extract_tournament_id(text: str) -> str:
    """Extraire l'ID numérique du tournoi"""
    match = re.search(r'(\d{8})(?:\D|$)', str(text))
    if match:
        return match.group(1)
    return None

# Liste des tournois Jiliac
jiliac_tournaments = [
    ("Standard Challenge 64 2025-07-01", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0112801190"),
    ("TheGathering.gg Standard Post-BNR Celebration 2025-07-02", "https://melee.gg/Decklist/View/b83b2fe7-a076-4ecc-b36b-b30e00ef7b58"),
    ("TheGathering.gg Standard Post-BNR Celebration #2 2025-07-02", "https://melee.gg/Decklist/View/78b3f54c-2c49-4a44-b8e3-b30e014c64c4"),
    ("Standard Challenge 32 2025-07-03", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0312801623"),
    ("Standard Challenge 32 2025-07-04", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0412801637"),
    ("Standard Challenge 32 2025-07-05", "https://www.mtgo.com/decklist/standard-challenge-32-2025-05-2512801654"),
    ("第2回シングルスター杯　サブイベント 2025-07-06", "https://melee.gg/Decklist/View/58391bb8-9d9a-4c34-98af-b31100d6d6ea"),
    ("Jaffer's Tarkir Dragonstorm Mosh Pit 2025-07-06", "https://melee.gg/Decklist/View/ddae0ba9-a4d7-4708-9e0b-b2cc003d55e2"),
    ("F2F Tour Red Deer - Sunday Super Qualifier 2025-07-06", "https://melee.gg/Decklist/View/f9fbb177-1238-4e17-8146-b31201842d46"),
    ("Standard Challenge 32 2025-07-06", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0612801677"),
    ("Standard Challenge 64 2025-07-07", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0712801688"),
    ("Standard Challenge 64 2025-07-08", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0812801696"),
    ("Standard Challenge 32 2025-07-10", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1012802771"),
    ("Standard Challenge 32 2025-07-11", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1112802789"),
    ("Standard RC Qualifier 2025-07-11", "https://www.mtgo.com/decklist/standard-rc-qualifier-2025-07-1112802761"),
    ("Standard Challenge 32 2025-07-12", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1212802811"),
    ("Valley Dasher's Bishkek Classic #1 2025-07-12", "https://melee.gg/Decklist/View/d11c46a4-4cdb-4603-bf82-b317008faa42"),
    ("Jaffer's Final Fantasy Mosh Pit 2025-07-13", "https://melee.gg/Decklist/View/07f0edf6-0180-447c-b258-b3190103047b"),
    ("Standard Challenge 32 2025-07-13", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1312802841"),
    ("Standard Challenge 64 2025-07-14", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1412802856"),
    ("Standard Challenge 64 2025-07-15", "https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1512802868"),
    ("Standard Challenge 32 2025-07-17", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1712803657"),
    ("Standard Challenge 32 2025-07-18", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1812803671"),
    ("Standard Challenge 32 2025-07-19", "https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1912803688"),
    ("Boa Qualifier #2 2025 (standard) 2025-07-19", "https://melee.gg/Decklist/View/e87b4ce1-7121-44ad-a9be-b31f00927479"),
]

# Extraire les IDs MTGO de Jiliac
jiliac_mtgo_ids = set()
jiliac_melee_count = 0
for name, url in jiliac_tournaments:
    if "mtgo.com" in url:
        id_match = extract_tournament_id(url)
        if id_match:
            jiliac_mtgo_ids.add(id_match)
    else:
        jiliac_melee_count += 1

print(f"📊 COMPARAISON AVEC JILIAC")
print(f"=========================")
print(f"Jiliac a utilisé {len(jiliac_tournaments)} tournois :")
print(f"- {len(jiliac_mtgo_ids)} tournois MTGO")
print(f"- {jiliac_melee_count} tournois Melee")

# Charger nos données listener
listener_data = {}
mtgo_path = Path("data/MTGOData/2025/07")
for day in range(1, 22):
    day_folder = mtgo_path / f"{day:02d}"
    if day_folder.exists():
        for file in day_folder.glob("*standard*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                tournament_id = str(data['Tournament']['Id'])
                listener_data[tournament_id] = {
                    'date': datetime.strptime(data['Tournament']['Date'][:10], '%Y-%m-%d'),
                    'name': data['Tournament']['Name'],
                }
            except:
                pass

our_mtgo_ids = set(listener_data.keys())

print(f"\nNotre analyse :")
print(f"- {len(our_mtgo_ids)} tournois MTGO dans le listener")

# Comparer
common_ids = jiliac_mtgo_ids.intersection(our_mtgo_ids)
jiliac_only = jiliac_mtgo_ids - our_mtgo_ids
our_only = our_mtgo_ids - jiliac_mtgo_ids

print(f"\n📊 RÉSULTATS DE LA COMPARAISON :")
print(f"- IDs en commun : {len(common_ids)}")
print(f"- IDs Jiliac seulement : {len(jiliac_only)}")
print(f"- IDs nous seulement : {len(our_only)}")

if jiliac_only:
    print(f"\n⚠️ Tournois MTGO manquants dans notre listener :")
    for tid in sorted(jiliac_only):
        # Trouver le nom du tournoi
        for name, url in jiliac_tournaments:
            if tid in url:
                print(f"  - {tid}: {name}")
                break

if our_only:
    print(f"\n📋 Tournois supplémentaires dans notre listener :")
    for tid in sorted(list(our_only)[:10]):
        if tid in listener_data:
            print(f"  - {tid}: {listener_data[tid]['name']} ({listener_data[tid]['date'].strftime('%Y-%m-%d')})")

# Vérifier notre cache aussi
print(f"\n🔍 Vérification du cache...")
cache_json_path = Path("data/cache/decklists/2025-07.json")
tournament_cache_data = {}
if cache_json_path.exists():
    with open(cache_json_path, 'r') as f:
        month_data = json.load(f)
    
    for key, data in month_data.items():
        if data.get('format', '').lower() == 'standard' or 'standard' in key.lower():
            tournament_id = extract_tournament_id(key)
            if tournament_id:
                tournament_cache_data[tournament_id] = {
                    'key': key,
                    'name': data.get('name', 'Unknown')
                }

print(f"Cache contient {len(tournament_cache_data)} tournois Standard avec IDs")

# Vérifier si les IDs manquants sont dans le cache
missing_but_in_cache = jiliac_only.intersection(set(tournament_cache_data.keys()))
print(f"\n✅ IDs Jiliac manquants mais présents dans le cache : {len(missing_but_in_cache)}")
if missing_but_in_cache:
    for tid in sorted(missing_but_in_cache):
        print(f"  - {tid}: {tournament_cache_data[tid]['name']}")