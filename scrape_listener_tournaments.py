#!/usr/bin/env python3
"""
Scrape tous les tournois Standard référencés dans les données listener de juillet.
"""

import json
from pathlib import Path
import subprocess
import time

def get_listener_tournament_ids():
    """Récupère tous les IDs de tournois Standard du listener"""
    listener_path = Path("jiliaclistener")
    tournament_ids = []
    
    for day_folder in listener_path.iterdir():
        if day_folder.is_dir() and day_folder.name.isdigit():
            day = int(day_folder.name)
            if 1 <= day <= 21:  # Juillet 1-21
                for file in day_folder.glob("*standard*.json"):
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    tournament_id = data['Tournament']['Id']
                    tournament_ids.append(tournament_id)
    
    return sorted(set(tournament_ids))

def check_existing_tournaments():
    """Vérifie quels tournois sont déjà scrapés"""
    existing = set()
    
    raw_path = Path("data/raw/mtgo/standard")
    if raw_path.exists():
        for file in raw_path.glob("*.json"):
            # Extract ID from filename
            if "(" in file.name and ")" in file.name:
                id_str = file.name.split("(")[1].split(")")[0]
                try:
                    existing.add(int(id_str))
                except:
                    pass
    
    return existing

def scrape_tournament(tournament_id: int):
    """Scrape un tournoi spécifique"""
    print(f"\n📥 Scraping tournament {tournament_id}...")
    
    # Use the standalone scraper
    cmd = [
        "python3", "scrape_mtgo_standalone.py",
        "--tournament-id", str(tournament_id),
        "--format", "standard"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Tournoi {tournament_id} scrapé avec succès")
            return True
        else:
            print(f"❌ Erreur pour tournoi {tournament_id}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception pour tournoi {tournament_id}: {e}")
        return False

def main():
    print("🎯 Scraping des tournois Standard du listener...")
    
    # Get all tournament IDs from listener
    listener_ids = get_listener_tournament_ids()
    print(f"\n📊 Trouvé {len(listener_ids)} tournois dans le listener")
    
    # Check what we already have
    existing_ids = check_existing_tournaments()
    print(f"✅ Déjà scrapés: {len(existing_ids)} tournois")
    
    # Find missing tournaments
    missing_ids = [tid for tid in listener_ids if tid not in existing_ids]
    print(f"❌ Manquants: {len(missing_ids)} tournois")
    
    if missing_ids:
        print(f"\n🚀 Scraping des {len(missing_ids)} tournois manquants...")
        print(f"IDs: {missing_ids}")
        
        success_count = 0
        for i, tid in enumerate(missing_ids, 1):
            print(f"\n[{i}/{len(missing_ids)}] Tournament ID: {tid}")
            
            if scrape_tournament(tid):
                success_count += 1
            
            # Small delay to avoid rate limiting
            if i < len(missing_ids):
                time.sleep(2)
        
        print(f"\n✅ Terminé! {success_count}/{len(missing_ids)} tournois scrapés avec succès")
    else:
        print("\n✅ Tous les tournois sont déjà scrapés!")

if __name__ == "__main__":
    main()