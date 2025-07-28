#!/usr/bin/env python3
"""
Import MTGO tournament data from Jiliac's MTG_decklistcache into our cache.
Focuses on Standard format for July 1-21, 2025.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.cache.processor import CacheProcessor
from src.cache.database import CacheDatabase


def import_jiliac_data():
    """Import MTGO data from Jiliac cache"""
    print("🔄 Importing MTGO data from Jiliac cache...")
    
    # Paths
    jiliac_path = Path("jiliac_pipeline/MTG_decklistcache/Tournaments/MTGO/2025/07")
    our_raw_path = Path("data/raw/mtgo/standard")
    
    # Ensure output directory exists
    our_raw_path.mkdir(parents=True, exist_ok=True)
    
    imported_count = 0
    
    # Process each day in July 1-21
    for day in range(1, 22):
        day_folder = jiliac_path / f"{day:02d}"
        if not day_folder.exists():
            continue
            
        # Find Standard tournaments (excluding leagues)
        for json_file in day_folder.glob("standard-*.json"):
            # Skip leagues
            if "league" in json_file.name:
                print(f"⚠️  Skipping league: {json_file.name}")
                continue
                
            # Read the file
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Convert to our format
            tournament = data.get('Tournament', {})
            date = tournament.get('Date', '')
            name = tournament.get('Name', '')
            
            # Extract tournament ID from filename
            # Format: standard-challenge-32-2025-07-0312801623.json
            parts = json_file.stem.split('-')
            if len(parts) >= 4 and parts[-1].isdigit():
                tournament_id = parts[-1]
            else:
                tournament_id = json_file.stem
            
            # Convert to our format
            our_format = {
                'tournament_id': tournament_id,
                'name': name,
                'format': 'standard',
                'date': date,
                'tournament_type': 'challenge' if 'challenge' in name.lower() else 'qualifier',
                'total_players': len(data.get('Decks', [])),
                'decks': []
            }
            
            # Convert decks
            for deck_data in data.get('Decks', []):
                deck = {
                    'player': deck_data.get('Player', ''),
                    'result': deck_data.get('Result', ''),
                    'rank': extract_rank(deck_data.get('Result', '')),
                    'mainboard': [
                        {
                            'count': card['Count'],
                            'card_name': card['CardName']
                        }
                        for card in deck_data.get('Mainboard', [])
                    ],
                    'sideboard': [
                        {
                            'count': card['Count'],
                            'card_name': card['CardName']
                        }
                        for card in deck_data.get('Sideboard', [])
                    ]
                }
                our_format['decks'].append(deck)
            
            # Save to our raw directory
            output_file = our_raw_path / f"{name.lower().replace(' ', '-')}-{tournament_id}-{date}.json"
            with open(output_file, 'w') as f:
                json.dump(our_format, f, indent=2)
            
            print(f"✅ Imported: {json_file.name} → {output_file.name}")
            imported_count += 1
    
    print(f"\n✅ Total imported: {imported_count} tournaments")
    
    # Now process through our cache system
    print("\n📊 Processing imported data through cache...")
    processor = CacheProcessor()
    processor.process_all_new()
    
    # Verify
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard", 
                                               datetime(2025, 7, 1), 
                                               datetime(2025, 7, 21, 23, 59, 59))
    mtgo_tournaments = [t for t in tournaments if t.platform == 'mtgo']
    print(f"\n✅ MTGO Standard tournaments in cache: {len(mtgo_tournaments)}")
    

def extract_rank(result: str) -> int:
    """Extract numeric rank from result string"""
    if 'Place' in result:
        try:
            return int(result.split()[0].rstrip('stndrh'))
        except:
            pass
    return 0


if __name__ == "__main__":
    import_jiliac_data()