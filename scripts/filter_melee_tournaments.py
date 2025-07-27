#!/usr/bin/env python3
"""
Filter Melee tournaments to exclude unreliable data.

RULES:
1. Exclude tournaments with less than 16 players (too small for reliable meta analysis)
2. Exclude tournaments with suspicious names (non-standard characters, casual events)

This improves archetype detection accuracy by removing low-quality data sources.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# Minimum player count for a tournament to be considered reliable
MIN_PLAYERS = 16

# Patterns in tournament names that indicate casual/unreliable events
EXCLUDED_NAME_PATTERNS = [
    "Mosh Pit",  # Casual format
    "Creative",  # Custom format
    "Летняя Лига",  # Non-standard (Cyrillic) tournaments
    "David's magic time",  # Personal/casual tournaments
    "Стандарт",  # Russian tournaments (often small/casual)
    "F2F Tour Toronto - Standard SQ",  # Often has < 16 players
]

def should_exclude_tournament(data: dict, filename: str) -> tuple[bool, str]:
    """
    Determine if a tournament should be excluded.
    
    Returns: (should_exclude, reason)
    """
    # Check player count
    if "Players" in data:
        player_count = len(data["Players"])
        if player_count < MIN_PLAYERS:
            return True, f"Only {player_count} players (minimum: {MIN_PLAYERS})"
    
    # Check tournament name
    if "TournamentName" in data:
        name = data["TournamentName"]
        for pattern in EXCLUDED_NAME_PATTERNS:
            if pattern in name:
                return True, f"Excluded pattern: '{pattern}'"
    
    # Check filename for non-ASCII characters (often unreliable tournaments)
    try:
        filename.encode('ascii')
    except UnicodeEncodeError:
        # Non-ASCII characters in filename
        if not any(reliable in filename for reliable in ["F2F", "Qualifier", "Championship"]):
            return True, "Non-standard tournament name"
    
    return False, ""

def filter_melee_tournaments(dry_run: bool = False):
    """Filter Melee tournaments based on reliability criteria."""
    
    melee_dir = Path("/Volumes/DataDisk/_Projects/Manalytics/data/raw/melee/standard")
    excluded_dir = melee_dir / "excluded"
    
    if not dry_run:
        excluded_dir.mkdir(exist_ok=True)
    
    stats = {
        "total": 0,
        "excluded": 0,
        "kept": 0,
        "reasons": {}
    }
    
    print(f"\n{'='*60}")
    print(f"FILTERING MELEE TOURNAMENTS - MIN PLAYERS: {MIN_PLAYERS}")
    print(f"{'='*60}\n")
    
    for json_file in melee_dir.glob("*.json"):
        stats["total"] += 1
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            should_exclude, reason = should_exclude_tournament(data, json_file.name)
            
            if should_exclude:
                stats["excluded"] += 1
                stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1
                
                print(f"❌ EXCLUDE: {json_file.name}")
                print(f"   Reason: {reason}")
                
                if "Players" in data:
                    print(f"   Players: {len(data['Players'])}")
                
                if not dry_run:
                    # Move to excluded directory
                    shutil.move(str(json_file), str(excluded_dir / json_file.name))
                    print(f"   → Moved to excluded/")
                
            else:
                stats["kept"] += 1
                print(f"✅ KEEP: {json_file.name}")
                if "Players" in data:
                    print(f"   Players: {len(data['Players'])}")
            
            print()
            
        except Exception as e:
            print(f"⚠️  ERROR processing {json_file.name}: {e}")
            print()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total tournaments: {stats['total']}")
    print(f"Excluded: {stats['excluded']}")
    print(f"Kept: {stats['kept']}")
    
    if stats["reasons"]:
        print("\nExclusion reasons:")
        for reason, count in sorted(stats["reasons"].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {reason}: {count}")
    
    print(f"\n{'='*60}\n")
    
    return stats

def clean_cache():
    """Clean the cache to force reprocessing without excluded tournaments."""
    cache_file = Path("/Volumes/DataDisk/_Projects/Manalytics/data/cache/tournaments.db")
    
    if cache_file.exists():
        # Backup before cleaning
        backup_name = f"tournaments_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = cache_file.parent / backup_name
        shutil.copy(cache_file, backup_path)
        print(f"✅ Cache backed up to: {backup_path}")
        
        # Remove cache
        cache_file.unlink()
        print(f"✅ Cache removed: {cache_file}")
        print("   → Next processing will exclude unreliable tournaments")
    else:
        print("ℹ️  No cache file found")

if __name__ == "__main__":
    import sys
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be moved\n")
    
    # Filter tournaments
    stats = filter_melee_tournaments(dry_run=dry_run)
    
    if not dry_run and stats["excluded"] > 0:
        print("\nCleaning cache to force reprocessing...")
        clean_cache()
        
        print("\n✅ FILTERING COMPLETE!")
        print(f"   - {stats['excluded']} unreliable tournaments moved to excluded/")
        print("   - Cache cleaned")
        print("   - Run process_all_standard_data.py to rebuild with clean data")
    elif dry_run:
        print("\n📋 To apply these changes, run without --dry-run flag:")
        print("   python3 scripts/filter_melee_tournaments.py")