#!/usr/bin/env python3
"""
Reprocess all tournaments to update archetype names with full color names.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import shutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.processor import CacheProcessor
from src.cache.database import CacheDatabase


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('reprocess.log')
        ]
    )


def main():
    """Reprocess all data with full color names"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Reprocessing with Full Color Names ===")
    
    # Backup current cache
    cache_dir = Path("data/cache")
    backup_dir = Path("data/cache_backup")
    
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    logger.info("Creating backup of current cache...")
    shutil.copytree(cache_dir, backup_dir)
    
    # Clear current cache
    logger.info("Clearing current cache...")
    db_file = cache_dir / "tournaments.db"
    if db_file.exists():
        db_file.unlink()
    
    for subdir in ["decklists", "archetypes", "meta_snapshots"]:
        dir_path = cache_dir / subdir
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(exist_ok=True)
    
    # Reprocess all tournaments
    processor = CacheProcessor()
    
    start_time = datetime.now()
    processor.process_all_new()
    end_time = datetime.now()
    
    logger.info(f"Reprocessing completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Show sample results
    logger.info("\n=== Sample Results ===")
    
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    logger.info(f"Total tournaments: {len(tournaments)}")
    
    # Show a few archetype names to verify
    from src.cache.reader import CacheReader
    reader = CacheReader()
    meta = reader.get_meta_snapshot("standard", datetime.now())
    
    logger.info("\nSample archetype names:")
    archetypes = []
    for arch, data in meta['archetypes'].items():
        if isinstance(data, dict):
            archetypes.append((arch, data['count']))
        else:
            archetypes.append((arch, data))
    
    archetypes.sort(key=lambda x: x[1], reverse=True)
    
    for arch, count in archetypes[:10]:
        logger.info(f"  - {arch}: {count} decks")
    
    logger.info("\n✅ Reprocessing complete! Check the visualization to see full color names.")


if __name__ == "__main__":
    main()