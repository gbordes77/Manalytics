#!/usr/bin/env python3
"""
Reset complet des données MTGO pour repartir sur de bonnes bases
"""

import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def reset_mtgo_data():
    """Nettoie toutes les données MTGO pour un fresh start"""
    
    logger.info("🧹 RESET COMPLET DES DONNÉES MTGO")
    logger.info("=" * 50)
    
    # 1. Nettoyer les données raw MTGO
    mtgo_raw = Path("data/raw/mtgo")
    if mtgo_raw.exists():
        logger.info(f"🗑️  Suppression de {mtgo_raw}")
        shutil.rmtree(mtgo_raw)
        logger.info("✅ Données raw MTGO supprimées")
    
    # 2. Nettoyer le nouveau dossier mtg_decklistcache
    decklistcache = Path("data/mtg_decklistcache")
    if decklistcache.exists():
        logger.info(f"🗑️  Suppression de {decklistcache}")
        shutil.rmtree(decklistcache)
        logger.info("✅ MTG decklistcache supprimé")
    
    # 3. Nettoyer le cache (juste les tournois MTGO)
    cache_file = Path("data/cache/decklists/2025-07.json")
    if cache_file.exists():
        logger.info("📝 Nettoyage du cache des tournois MTGO...")
        
        import json
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Garder seulement les tournois Melee
        cleaned_cache = {}
        mtgo_count = 0
        
        for key, tournament in cache_data.items():
            if 'melee' in key.lower() or 'TheGathering' in key:
                cleaned_cache[key] = tournament
            else:
                mtgo_count += 1
        
        # Sauvegarder le cache nettoyé
        with open(cache_file, 'w') as f:
            json.dump(cleaned_cache, f, indent=2)
        
        logger.info(f"✅ Supprimé {mtgo_count} tournois MTGO du cache")
        logger.info(f"📊 Conservé {len(cleaned_cache)} tournois Melee")
    
    # 4. Créer les dossiers nécessaires
    mtgo_raw.mkdir(parents=True, exist_ok=True)
    decklistcache.mkdir(parents=True, exist_ok=True)
    
    logger.info("\n✨ Reset terminé!")
    logger.info("Vous pouvez maintenant lancer le nouveau scraper:")
    logger.info("python3 scrape_mtgo_complete.py --start-date 2025-07-01 --end-date 2025-07-21")


if __name__ == "__main__":
    # Confirmation
    print("\n⚠️  ATTENTION: Ceci va supprimer toutes les données MTGO!")
    print("Les données Melee seront conservées.")
    confirm = input("\nContinuer? (y/n): ")
    
    if confirm.lower() == 'y':
        reset_mtgo_data()
    else:
        print("Annulé.")