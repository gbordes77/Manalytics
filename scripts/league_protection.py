#!/usr/bin/env python3
"""
LEAGUE PROTECTION SYSTEM
========================
This script automatically removes any leagues that might have been scraped
and provides a warning system.

Run this AFTER any scraping operation to ensure leagues are never included.
"""

import sys
import os
from pathlib import Path
import shutil
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def scan_for_leagues(base_path: Path) -> list:
    """Find all league files in the data directory"""
    league_files = []
    
    # Find all files with 'league' in the name
    for file_path in base_path.rglob("*league*"):
        if file_path.is_file() and file_path.suffix == ".json":
            league_files.append(file_path)
    
    # Find all files in 'leagues' directories
    for league_dir in base_path.rglob("leagues"):
        if league_dir.is_dir():
            for file_path in league_dir.glob("*.json"):
                if file_path not in league_files:
                    league_files.append(file_path)
    
    return league_files

def remove_leagues(league_files: list, backup: bool = True) -> int:
    """Remove league files, optionally backing them up first"""
    removed_count = 0
    
    if backup and league_files:
        # Create backup directory
        backup_dir = Path("data/backup/removed_leagues") / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 Backing up to: {backup_dir}")
    
    for file_path in league_files:
        try:
            if backup:
                # Preserve directory structure in backup
                relative_path = file_path.relative_to(Path("data/raw"))
                backup_path = backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
            
            # Remove the file
            file_path.unlink()
            removed_count += 1
            print(f"❌ Removed: {file_path}")
        except Exception as e:
            print(f"⚠️  Error removing {file_path}: {e}")
    
    # Remove empty leagues directories
    for league_dir in Path("data/raw").rglob("leagues"):
        if league_dir.is_dir() and not any(league_dir.iterdir()):
            league_dir.rmdir()
            print(f"📁 Removed empty directory: {league_dir}")
    
    return removed_count

def check_database_for_leagues():
    """Check if any leagues made it into the database"""
    try:
        import sqlite3
        
        db_path = Path("data/cache/tournaments.db")
        if not db_path.exists():
            return 0
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count leagues in database
        cursor.execute("SELECT COUNT(*) FROM tournaments WHERE name LIKE '%league%'")
        league_count = cursor.fetchone()[0]
        
        if league_count > 0:
            print(f"\n⚠️  WARNING: Found {league_count} leagues in the database!")
            print("   Run: rm -f data/cache/tournaments.db && python3 scripts/process_all_standard_data.py")
        
        conn.close()
        return league_count
    except Exception as e:
        print(f"Could not check database: {e}")
        return 0

def main():
    """Main protection routine"""
    print("🛡️  LEAGUE PROTECTION SYSTEM")
    print("=" * 50)
    
    # Check for leagues in raw data
    raw_path = Path("data/raw")
    if not raw_path.exists():
        print("✅ No data/raw directory found - nothing to check")
        return
    
    print("\n🔍 Scanning for leagues...")
    league_files = scan_for_leagues(raw_path)
    
    if not league_files:
        print("✅ No leagues found in raw data - system is clean!")
    else:
        print(f"\n⚠️  Found {len(league_files)} league files:")
        for f in league_files[:10]:  # Show first 10
            print(f"   - {f}")
        if len(league_files) > 10:
            print(f"   ... and {len(league_files) - 10} more")
        
        # Remove them
        print("\n🧹 Removing leagues...")
        removed = remove_leagues(league_files, backup=True)
        print(f"\n✅ Removed {removed} league files")
    
    # Check database
    print("\n🔍 Checking database...")
    db_leagues = check_database_for_leagues()
    
    # Final status
    print("\n" + "=" * 50)
    if league_files or db_leagues > 0:
        print("⚠️  LEAGUES WERE FOUND AND REMOVED")
        print("   Please rebuild the cache to ensure clean data")
    else:
        print("✅ SYSTEM IS CLEAN - No leagues found!")
    
    # Create marker file to indicate last check
    marker = Path("data/.league_check")
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(f"Last checked: {datetime.now()}\nLeagues found: {len(league_files)}\n")

if __name__ == "__main__":
    main()