#!/usr/bin/env python3
"""
Analyse du 1er au 21 juillet 2025 pour comparaison avec Jiliac.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name


def analyze_july_1_to_21():
    """Analyse les tournois du 1er au 21 juillet uniquement"""
    
    print("\n" + "="*80)
    print("📊 ANALYSE MANALYTICS - 1er au 21 JUILLET 2025")
    print("="*80)
    
    # Get database connection
    db = CacheDatabase()
    reader = CacheReader()
    
    # Date range: July 1-21, 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21, 23, 59, 59)
    
    # Get tournaments in date range
    all_tournaments = db.get_tournaments_by_format("standard", start_date, end_date)
    
    # Filter out leagues and non-competitive
    competitive_tournaments = []
    excluded_count = 0
    
    EXCLUDED_PATTERNS = [
        "mosh pit", "creative", "летняя лига", "league",
        "casual", "fun", "test", "practice"
    ]
    
    for t in all_tournaments:
        # Check tournament name
        name_lower = t.name.lower() if t.name else ""
        
        # Skip if matches excluded pattern
        if any(pattern in name_lower for pattern in EXCLUDED_PATTERNS):
            print(f"❌ Excluded: {t.name} (non-competitive)")
            excluded_count += 1
            continue
            
        # Skip leagues
        if 'league' in t.type.lower():
            print(f"❌ Excluded: {t.name} (league)")
            excluded_count += 1
            continue
            
        competitive_tournaments.append(t)
    
    print(f"\n📈 Tournois trouvés: {len(all_tournaments)}")
    print(f"❌ Tournois exclus: {excluded_count}")
    print(f"✅ Tournois compétitifs: {len(competitive_tournaments)}")
    
    # Calculate matches (not just decks)
    total_matches = 0
    archetype_matches = {}
    
    # Load decklists for each tournament
    for tournament in competitive_tournaments:
        # Load tournament data
        month_key = tournament.date.strftime("%Y-%m")
        decklists_file = Path(f"data/cache/decklists/{month_key}.json")
        
        if decklists_file.exists():
            with open(decklists_file, 'r') as f:
                month_data = json.load(f)
            
            if tournament.id in month_data:
                decklists = month_data[tournament.id].get('decklists', [])
                
                for deck in decklists:
                    wins = deck.get('wins') or 0
                    losses = deck.get('losses') or 0
                    matches_played = wins + losses
                    
                    if matches_played > 0:
                        archetype = deck.get('archetype', 'Unknown')
                        
                        if archetype not in archetype_matches:
                            archetype_matches[archetype] = 0
                        
                        archetype_matches[archetype] += matches_played
                        total_matches += matches_played
    
    # Sort by matches
    sorted_archetypes = sorted(archetype_matches.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📊 RÉSULTATS (Méthode Jiliac - Par MATCHES):")
    print(f"Total matches analysés: {total_matches}")
    print(f"\nTop 20 Archétypes:")
    print("-" * 60)
    print(f"{'Rang':<6} {'Archétype':<35} {'Matches':<10} {'%':<8}")
    print("-" * 60)
    
    for i, (archetype, matches) in enumerate(sorted_archetypes[:20], 1):
        percentage = (matches / total_matches * 100) if total_matches > 0 else 0
        archetype_name = archetype if archetype else "Unknown"
        print(f"{i:<6} {archetype_name:<35} {matches:<10} {percentage:>6.1f}%")
    
    # Summary for comparison with Jiliac
    print("\n" + "="*80)
    print("📋 RÉSUMÉ POUR COMPARAISON AVEC JILIAC:")
    print("="*80)
    
    print(f"\nPériode: 1-21 Juillet 2025")
    print(f"Tournois compétitifs: {len(competitive_tournaments)}")
    print(f"Matches totaux: {total_matches}")
    print(f"\nTop 5 (pour comparaison directe):")
    
    for i, (archetype, matches) in enumerate(sorted_archetypes[:5], 1):
        percentage = (matches / total_matches * 100) if total_matches > 0 else 0
        print(f"{i}. {archetype} - {percentage:.1f}% ({matches} matches)")
    
    return sorted_archetypes, total_matches


if __name__ == "__main__":
    analyze_july_1_to_21()