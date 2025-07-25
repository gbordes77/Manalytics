import time
import httpx
import logging
from typing import Dict, Optional, Any
from config.settings import settings
from src.utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ScryfallClient:
    """Client for Scryfall API interactions using httpx."""

    BASE_URL = "https://api.scryfall.com"

    def __init__(self):
        self.client = httpx.Client(base_url=self.BASE_URL, timeout=10.0)
        self.cache = CacheManager()
        self.last_request_time = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        wait_time = (1 / settings.SCRYFALL_RATE_LIMIT) - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def get_card_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        cache_key = f"scryfall:card:{name}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        self._rate_limit()
        try:
            response = self.client.get("/cards/named", params={"fuzzy": name})
            response.raise_for_status()
            data = response.json()
            self.cache.set(cache_key, data, ttl=3600 * 24 * 7) # Cache for 7 days
            return data
        except httpx.RequestError as e:
            logger.error(f"Scryfall API error for card '{name}': {e}")
            return None