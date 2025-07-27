#!/usr/bin/env python3
"""
Analyze only competitive tournaments, excluding fun/special events
Match Jiliac's methodology more closely
"""

import sys
from pathlib import Path
import json
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))

from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name


def is_competitive_tournament(tournament_name, unknown_rate):
    """Filter out fun/special tournaments"""
    # Exclude tournaments with fun/special names
    exclude_keywords = ['mosh pit', 'dragonstorm', 'creative', 'casual', 'fun']
    name_lower = tournament_name.lower()
    
    for keyword in exclude_keywords:
        if keyword in name_lower:
            return False
    
    # Exclude tournaments with >40% unknown rate
    if unknown_rate > 0.4:
        return False
    
    return True


def main():
    # Get tournaments July 1-20
    db = CacheDatabase()
    all_tournaments = db.get_tournaments_by_format('standard')
    
    tournaments = []
    for t in all_tournaments:
        if 'league' in t.type.lower():
            continue
        date_str = t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d')
        if date_str >= "2025-07-01" and date_str <= "2025-07-20":
            tournaments.append(t)
    
    # Load decklists
    monthly_file = Path("data/cache/decklists/2025-07.json")
    with open(monthly_file, 'r') as f:
        all_decklists = json.load(f)
    
    # First pass: calculate unknown rates per tournament
    tournament_unknown_rates = {}
    
    for tournament in tournaments:
        if tournament.id in all_decklists:
            decklists = all_decklists[tournament.id].get('decklists', [])
            total = len(decklists)
            unknown = sum(1 for d in decklists if not d.get('archetype'))
            
            tournament_unknown_rates[tournament.id] = {
                'name': tournament.name,
                'rate': unknown / total if total > 0 else 0,
                'total': total,
                'unknown': unknown
            }
    
    # Second pass: analyze only competitive tournaments
    archetype_matches = defaultdict(int)
    total_matches_all = 0
    unknown_matches = 0
    excluded_tournaments = []
    included_tournaments = []
    
    for tournament in tournaments:
        if tournament.id not in all_decklists:
            continue
            
        # Check if competitive
        unknown_rate = tournament_unknown_rates[tournament.id]['rate']
        
        if not is_competitive_tournament(tournament.name, unknown_rate):
            excluded_tournaments.append({
                'name': tournament.name,
                'date': tournament.date if isinstance(tournament.date, str) else tournament.date.strftime('%Y-%m-%d'),
                'players': tournament.players,
                'unknown_rate': unknown_rate
            })
            continue
        
        included_tournaments.append(tournament)
        
        # Count matches
        decklists = all_decklists[tournament.id].get('decklists', [])
        for deck in decklists:
            archetype = deck.get('archetype')
            wins = deck.get('wins', 0) or 0
            losses = deck.get('losses', 0) or 0
            matches = wins + losses
            
            if matches > 0:
                if archetype:
                    # Normalize Mono White Caretaker
                    if 'Mono White Caretaker' in archetype:
                        archetype = 'Mono White Caretaker'
                    archetype_matches[archetype] += matches
                else:
                    unknown_matches += matches
                total_matches_all += matches
    
    # Print results
    print("COMPETITIVE TOURNAMENTS ONLY ANALYSIS")
    print("="*80)
    print(f"Total tournaments: {len(tournaments)}")
    print(f"Included (competitive): {len(included_tournaments)}")
    print(f"Excluded (fun/high unknown): {len(excluded_tournaments)}")
    
    if excluded_tournaments:
        print("\nExcluded tournaments:")
        for t in excluded_tournaments:
            print(f"  - {t['date']}: {t['name']} ({t['players']} players, {t['unknown_rate']:.0%} unknown)")
    
    print(f"\nTotal matches analyzed: {total_matches_all}")
    print(f"Unknown matches: {unknown_matches} ({unknown_matches/total_matches_all*100:.1f}%)")
    
    # Calculate percentages
    sorted_archetypes = sorted(archetype_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Apply 1.08% cutoff
    cutoff = total_matches_all * 0.0108
    
    print(f"\nArchetypes above 1.08% cutoff ({cutoff:.0f} matches):")
    print("-"*60)
    print(f"{'Rank':<5} {'Archetype':<30} {'Matches':>8} {'%':>8}")
    print("-"*60)
    
    for i, (arch, matches) in enumerate(sorted_archetypes):
        if matches < cutoff:
            break
        percentage = (matches / total_matches_all) * 100
        print(f"{i+1:<5} {arch:<30} {matches:>8} {percentage:>7.1f}%")
    
    # Compare with Jiliac
    print("\n" + "="*80)
    print("COMPARISON WITH JILIAC (Top 10):")
    print("="*80)
    
    jiliac_data = [
        ("Izzet Cauldron", 19.7),
        ("Dimir Midrange", 18.6),
        ("Golgari Midrange", 5.4),
        ("Mono White Caretaker", 5.1),
        ("Boros Convoke", 4.9),
        ("Gruul Aggro", 4.6),
        ("Mono Green Landfall", 3.1),
        ("Jeskai Control", 2.4),
        ("Izzet Aggro", 2.2),
        ("Izzet Prowess", 2.1)
    ]
    
    our_data = {arch: (matches/total_matches_all*100) for arch, matches in archetype_matches.items()}
    
    print(f"{'Archetype':<30} {'Jiliac %':>10} {'Our %':>10} {'Diff':>10}")
    print("-"*60)
    
    for arch, jiliac_pct in jiliac_data:
        our_pct = our_data.get(arch, 0.0)
        diff = our_pct - jiliac_pct
        color = "✅" if abs(diff) < 1.0 else "⚠️" if abs(diff) < 2.0 else "❌"
        print(f"{arch:<30} {jiliac_pct:>10.1f} {our_pct:>10.1f} {diff:>+10.1f} {color}")
    
    # Summary
    avg_diff = sum(abs(our_data.get(arch, 0.0) - jpct) for arch, jpct in jiliac_data) / len(jiliac_data)
    print(f"\nAverage absolute difference: {avg_diff:.1f}%")
    
    if avg_diff < 1.0:
        print("✅ EXCELLENT MATCH with Jiliac's data!")
    elif avg_diff < 2.0:
        print("⚠️ Good match, minor differences")
    else:
        print("❌ Significant differences remain")


if __name__ == "__main__":
    main()