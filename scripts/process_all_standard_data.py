#!/usr/bin/env python3
"""
Process all Standard tournament data through the cache system.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.processor import CacheProcessor
from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cache_processing.log')
        ]
    )


def main():
    """Process all Standard tournament data"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting Standard Data Processing ===")
    
    # Initialize processor
    processor = CacheProcessor()
    
    # Process all new tournaments
    start_time = datetime.now()
    processor.process_all_new()
    end_time = datetime.now()
    
    logger.info(f"Processing completed in {(end_time - start_time).total_seconds():.2f} seconds")
    
    # Generate statistics
    logger.info("\n=== Cache Statistics ===")
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    logger.info(f"Total tournaments processed: {len(tournaments)}")
    
    # Get archetype distribution
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    logger.info(f"Total decks: {meta_snapshot['total_decks']}")
    logger.info(f"Total unique archetypes: {len(meta_snapshot['archetypes'])}")
    
    # Log top archetypes
    logger.info("\nTop 10 Archetypes:")
    archetypes_sorted = sorted(meta_snapshot['archetypes'].items(), key=lambda x: x[1], reverse=True)
    for i, (archetype, count) in enumerate(archetypes_sorted[:10], 1):
        percentage = (count / meta_snapshot['total_decks']) * 100
        logger.info(f"{i}. {archetype}: {count} decks ({percentage:.1f}%)")
    
    # Save full statistics to JSON for visualization
    stats_file = Path("data/cache/processing_stats.json")
    stats = {
        "processing_time": (end_time - start_time).total_seconds(),
        "tournaments_processed": len(tournaments),
        "total_decks": meta_snapshot['total_decks'],
        "archetypes": meta_snapshot['archetypes'],
        "colors": meta_snapshot['colors'],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"\nStatistics saved to: {stats_file}")
    
    return meta_snapshot


if __name__ == "__main__":
    meta_snapshot = main()