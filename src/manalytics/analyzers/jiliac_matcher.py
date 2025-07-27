#!/usr/bin/env python3
"""
Analyze data exactly like Jiliac does:
- Based on number of MATCHES (not decks)
- Include Unknown in total
- Cutoff at 1.08%
"""

import sys
from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name


def analyze_like_jiliac():
    """Analyze July 1-20 data like Jiliac"""
    
    # Get tournaments
    db = CacheDatabase()
    all_tournaments = db.get_tournaments_by_format("standard")
    
    tournaments = []
    for t in all_tournaments:
        # EXCLUDING leagues like we do
        if 'league' in t.type.lower():
            continue
        date_str = t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d')
        if date_str >= "2025-07-01" and date_str <= "2025-07-20":
            tournaments.append(t)
    
    print(f"Analyzing {len(tournaments)} tournaments (July 1-20, excluding leagues)")
    
    # Count by MATCHES
    archetype_matches = defaultdict(int)
    total_matches_all = 0
    unknown_matches = 0
    total_decks_all = 0
    unknown_decks = 0
    
    # Load decklists
    monthly_file = Path("data/cache/decklists/2025-07.json")
    with open(monthly_file, 'r') as f:
        all_decklists = json.load(f)
    
    for tournament in tournaments:
        if tournament.id in all_decklists:
            decklists = all_decklists[tournament.id].get('decklists', [])
            for deck in decklists:
                archetype = deck.get('archetype')
                wins = deck.get('wins', 0) or 0
                losses = deck.get('losses', 0) or 0
                matches = wins + losses
                
                total_decks_all += 1
                
                if matches > 0:
                    if archetype:
                        archetype_matches[archetype] += matches
                    else:
                        unknown_matches += matches
                        unknown_decks += 1
                    total_matches_all += matches
                elif not archetype:
                    unknown_decks += 1
    
    print(f"\nTotal decks: {total_decks_all}")
    print(f"Unknown decks: {unknown_decks} ({unknown_decks/total_decks_all*100:.1f}%)")
    print(f"\nTotal matches: {total_matches_all}")
    print(f"Unknown matches: {unknown_matches} ({unknown_matches/total_matches_all*100:.1f}%)")
    
    # Sort by matches
    sorted_archetypes = sorted(archetype_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Apply 1.08% cutoff
    cutoff = total_matches_all * 0.0108
    print(f"\n1.08% cutoff = {cutoff:.0f} matches")
    
    print("\nArchetypes above 1.08% (based on matches):")
    print("-" * 60)
    
    for i, (arch, matches) in enumerate(sorted_archetypes):
        if matches < cutoff:
            break
        percentage = (matches / total_matches_all) * 100
        clean_name = format_archetype_name(arch)
        print(f"{i+1:2d}. {clean_name:<30} {matches:4d} matches ({percentage:5.1f}%)")
    
    # Compare with Jiliac's data
    print("\n" + "="*60)
    print("COMPARISON WITH JILIAC'S DATA:")
    print("="*60)
    
    jiliac_data = {
        "Izzet Cauldron": 19.7,
        "Dimir Midrange": 18.6,
        "Golgari Midrange": 5.4,
        "Mono White Caretaker": 5.1,
        "Boros Convoke": 4.9,
        "Gruul Aggro": 4.6,
        "Mono Green Landfall": 3.1,
        "Jeskai Control": 2.4,
        "Izzet Aggro": 2.2,
        "Izzet Prowess": 2.1,
        "Azorius Control": 1.9,
        "Jeskai Convoke": 1.8,
        "Naya Yuna": 1.7,
        "Mono Red Aggro": 1.7,
        "Jeskai Oculus": 1.5
    }
    
    our_data = {}
    for arch, matches in sorted_archetypes:
        clean_name = format_archetype_name(arch)
        percentage = (matches / total_matches_all) * 100
        our_data[clean_name] = percentage
    
    print(f"{'Archetype':<30} {'Jiliac %':>10} {'Our %':>10} {'Diff':>10}")
    print("-" * 60)
    
    for arch, jiliac_pct in jiliac_data.items():
        our_pct = our_data.get(arch, 0.0)
        diff = our_pct - jiliac_pct
        print(f"{arch:<30} {jiliac_pct:>10.1f} {our_pct:>10.1f} {diff:>+10.1f}")
    
    # Summary statistics
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY:")
    print("="*60)
    print(f"Our top 2: {format_archetype_name(sorted_archetypes[0][0])} ({our_data.get(format_archetype_name(sorted_archetypes[0][0]), 0):.1f}%), "
          f"{format_archetype_name(sorted_archetypes[1][0])} ({our_data.get(format_archetype_name(sorted_archetypes[1][0]), 0):.1f}%)")
    print(f"Jiliac's top 2: Izzet Cauldron (19.7%), Dimir Midrange (18.6%)")
    
    # Check for missing data
    print("\nPossible reasons for differences:")
    print("1. Jiliac might include league data we don't have")
    print("2. Different archetype detection rules") 
    print("3. Different tournament inclusion criteria")
    print(f"4. Our Unknown rate: {unknown_matches/total_matches_all*100:.1f}% of matches")


if __name__ == "__main__":
    analyze_like_jiliac()