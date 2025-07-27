#!/usr/bin/env python3
"""
Investigate differences between our data and Jiliac's
Focus on understanding why percentages differ
"""

import sys
from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.cache.database import CacheDatabase


def main():
    # Get tournaments July 1-20
    db = CacheDatabase()
    all_tournaments = db.get_tournaments_by_format('standard')
    
    tournaments = []
    mtgo_count = 0
    melee_count = 0
    
    for t in all_tournaments:
        if 'league' in t.type.lower():
            continue
        date_str = t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d')
        if date_str >= "2025-07-01" and date_str <= "2025-07-20":
            tournaments.append(t)
            if t.platform == 'mtgo':
                mtgo_count += 1
            else:
                melee_count += 1
    
    print(f"TOURNAMENT BREAKDOWN (July 1-20):")
    print(f"Total tournaments: {len(tournaments)}")
    print(f"  - MTGO: {mtgo_count}")
    print(f"  - Melee: {melee_count}")
    print()
    
    # Count matches by platform
    monthly_file = Path("data/cache/decklists/2025-07.json")
    with open(monthly_file, 'r') as f:
        all_decklists = json.load(f)
    
    # Analyze by platform
    platform_stats = defaultdict(lambda: {
        'decks': 0,
        'matches': 0,
        'unknown_decks': 0,
        'unknown_matches': 0,
        'archetypes': defaultdict(int)
    })
    
    for tournament in tournaments:
        if tournament.id in all_decklists:
            platform = tournament.platform
            decklists = all_decklists[tournament.id].get('decklists', [])
            
            for deck in decklists:
                archetype = deck.get('archetype')
                wins = deck.get('wins', 0) or 0
                losses = deck.get('losses', 0) or 0
                matches = wins + losses
                
                platform_stats[platform]['decks'] += 1
                
                if matches > 0:
                    platform_stats[platform]['matches'] += matches
                    if archetype:
                        # Normalize Mono White Caretaker
                        if 'Mono White Caretaker' in archetype:
                            archetype = 'Mono White Caretaker'
                        platform_stats[platform]['archetypes'][archetype] += matches
                    else:
                        platform_stats[platform]['unknown_matches'] += matches
                        platform_stats[platform]['unknown_decks'] += 1
                else:
                    if not archetype:
                        platform_stats[platform]['unknown_decks'] += 1
    
    # Print platform analysis
    print("PLATFORM ANALYSIS:")
    print("-" * 80)
    for platform, stats in platform_stats.items():
        total_matches = stats['matches']
        unknown_rate = (stats['unknown_matches'] / total_matches * 100) if total_matches > 0 else 0
        
        print(f"\n{platform.upper()}:")
        print(f"  Decks: {stats['decks']}")
        print(f"  Matches: {stats['matches']}")
        print(f"  Unknown rate: {unknown_rate:.1f}% ({stats['unknown_matches']} matches)")
        
        # Top 5 archetypes for this platform
        sorted_archs = sorted(stats['archetypes'].items(), key=lambda x: x[1], reverse=True)
        print(f"  Top 5 archetypes:")
        for i, (arch, matches) in enumerate(sorted_archs[:5]):
            pct = (matches / total_matches * 100) if total_matches > 0 else 0
            print(f"    {i+1}. {arch}: {pct:.1f}%")
    
    # HYPOTHESIS: Jiliac might weight tournaments differently
    print("\n" + "="*80)
    print("HYPOTHESIS TESTING:")
    print("="*80)
    
    # Test 1: What if Jiliac only uses MTGO?
    print("\n1. MTGO-only analysis:")
    mtgo_archetypes = platform_stats['mtgo']['archetypes']
    mtgo_total = platform_stats['mtgo']['matches']
    
    sorted_mtgo = sorted(mtgo_archetypes.items(), key=lambda x: x[1], reverse=True)
    for i, (arch, matches) in enumerate(sorted_mtgo[:5]):
        pct = (matches / mtgo_total * 100) if mtgo_total > 0 else 0
        print(f"   {arch}: {pct:.1f}%")
    
    # Test 2: Check specific tournament types
    print("\n2. Tournament type breakdown:")
    type_counts = defaultdict(int)
    for t in tournaments:
        type_counts[t.type] += 1
    
    for t_type, count in sorted(type_counts.items()):
        print(f"   {t_type}: {count}")
    
    # Test 3: Check for missing data on specific dates
    print("\n3. Daily deck counts:")
    daily_decks = defaultdict(int)
    daily_unknown = defaultdict(int)
    
    for tournament in tournaments:
        date = tournament.date if isinstance(tournament.date, str) else tournament.date.strftime('%Y-%m-%d')
        if tournament.id in all_decklists:
            decklists = all_decklists[tournament.id].get('decklists', [])
            daily_decks[date] += len(decklists)
            
            for deck in decklists:
                if not deck.get('archetype'):
                    daily_unknown[date] += 1
    
    for date in sorted(daily_decks.keys()):
        unknown_rate = (daily_unknown[date] / daily_decks[date] * 100) if daily_decks[date] > 0 else 0
        print(f"   {date}: {daily_decks[date]} decks ({unknown_rate:.0f}% unknown)")
    
    # Final comparison
    print("\n" + "="*80)
    print("FINAL COMPARISON (All platforms, matches-based):")
    print("="*80)
    
    # Combine all platforms
    all_archetypes = defaultdict(int)
    total_matches = 0
    
    for platform, stats in platform_stats.items():
        total_matches += stats['matches']
        for arch, matches in stats['archetypes'].items():
            all_archetypes[arch] += matches
    
    sorted_all = sorted(all_archetypes.items(), key=lambda x: x[1], reverse=True)
    
    jiliac_top5 = [
        ("Izzet Cauldron", 19.7),
        ("Dimir Midrange", 18.6),
        ("Golgari Midrange", 5.4),
        ("Mono White Caretaker", 5.1),
        ("Boros Convoke", 4.9)
    ]
    
    print(f"{'Archetype':<30} {'Our %':>10} {'Jiliac %':>10} {'Diff':>10}")
    print("-" * 60)
    
    for jiliac_arch, jiliac_pct in jiliac_top5:
        our_matches = all_archetypes.get(jiliac_arch, 0)
        our_pct = (our_matches / total_matches * 100) if total_matches > 0 else 0
        diff = our_pct - jiliac_pct
        print(f"{jiliac_arch:<30} {our_pct:>10.1f} {jiliac_pct:>10.1f} {diff:>+10.1f}")
    
    print(f"\nTotal matches in our data: {total_matches}")
    print(f"Unknown match rate: {sum(s['unknown_matches'] for s in platform_stats.values()) / total_matches * 100:.1f}%")


if __name__ == "__main__":
    main()