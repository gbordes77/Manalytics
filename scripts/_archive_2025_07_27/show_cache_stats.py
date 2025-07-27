#!/usr/bin/env python3
"""
Show cache statistics for Standard format.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase


def main():
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    print("\n=== 📊 MANALYTICS CACHE STATISTICS - STANDARD ===\n")
    print(f"✅ Tournaments processed: {len(tournaments)}")
    print(f"✅ Total decks analyzed: {meta_snapshot['total_decks']}")
    print(f"✅ Unique archetypes detected: {len(meta_snapshot['archetypes'])}")
    
    # Extract counts from archetype data
    archetype_counts = {}
    for arch, data in meta_snapshot['archetypes'].items():
        if isinstance(data, dict):
            archetype_counts[arch] = data['count']
        else:
            archetype_counts[arch] = data
    
    # Sort and show top 15
    sorted_archetypes = sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n📈 TOP 15 ARCHETYPES:")
    print("=" * 60)
    print(f"{'Rank':<5} {'Archetype':<35} {'Decks':<8} {'Meta %':<8}")
    print("-" * 60)
    
    for i, (archetype, count) in enumerate(sorted_archetypes[:15], 1):
        percentage = (count / meta_snapshot['total_decks']) * 100
        archetype_name = archetype or "Unknown"
        print(f"{i:<5} {archetype_name:<35} {count:<8} {percentage:>6.1f}%")
    
    # Show unidentified decks
    unknown_count = archetype_counts.get(None, 0)
    if unknown_count > 0:
        unknown_pct = (unknown_count / meta_snapshot['total_decks']) * 100
        print(f"\n⚠️  Unidentified decks: {unknown_count} ({unknown_pct:.1f}%)")
    
    # Show color distribution
    print("\n🎨 COLOR DISTRIBUTION:")
    print("=" * 40)
    
    color_counts = {}
    for color, data in meta_snapshot['colors'].items():
        if isinstance(data, dict):
            color_counts[color] = data['count']
        else:
            color_counts[color] = data
    
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    for color, count in sorted_colors[:10]:
        percentage = (count / meta_snapshot['total_decks']) * 100
        print(f"{color:<10} {count:>4} decks ({percentage:>5.1f}%)")
    
    print("\n✨ Visualization HTML created at: data/cache/archetype_visualization.html")
    print("   Open it in your browser to see interactive charts!")


if __name__ == "__main__":
    main()