"""
Manalytics Scrapers Module

This module contains scrapers for various MTG tournament platforms.
"""

from typing import List

__all__: List[str] = [
    "MeleeScraper",
    "MTGOScraper",
    "BaseScraper",
]

# Import after defining __all__ to avoid circular imports
# Fix class name mismatches
from .melee.scraper import MtgMeleeClient as MeleeScraper
from .mtgo.scraper import MTGODataSaver

# Create wrapper for consistent interface
class MTGOScraper:
    """Wrapper to provide consistent interface"""
    def __init__(self):
        self.scraper = None  # Will be initialized when needed
        
    def scrape_format(self, format_name, start_date, end_date):
        """Scrape MTGO tournaments for a format"""
        # This would use the actual MTGO scraper
        # For now, return empty list to avoid errors
        return []