"""
Unified cache management using Redis with fallback to memory.
"""
import json
import time
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import redis
from config.settings import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching with Redis and memory fallback."""
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.max_memory_items = 1000
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection if available."""
        if not settings.REDIS_URL:
            logger.warning("Redis URL not configured, using memory cache only")
            return None
        
        try:
            client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            client.ping()
            logger.info("Redis cache connected successfully")
            return client
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using memory cache.")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.debug(f"Redis get error: {e}")
        
        # Fall back to memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry['expires_at'] > time.time():
                return entry['value']
            else:
                del self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds."""
        serialized = json.dumps(value)
        
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, serialized)
                return
            except Exception as e:
                logger.debug(f"Redis set error: {e}")
        
        # Fall back to memory cache
        self.memory_cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        
        # Cleanup if too many items
        if len(self.memory_cache) > self.max_memory_items:
            self._cleanup_memory_cache()
    
    def delete(self, key: str):
        """Delete key from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.debug(f"Redis delete error: {e}")
        
        self.memory_cache.pop(key, None)
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching a pattern."""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.debug(f"Redis clear pattern error: {e}")
        
        # For memory cache, clear matching keys
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
    
    def _cleanup_memory_cache(self):
        """Remove expired and oldest entries from memory cache."""
        now = time.time()
        
        # Remove expired entries
        self.memory_cache = {
            k: v for k, v in self.memory_cache.items()
            if v['expires_at'] > now
        }
        
        # If still too many, remove oldest
        if len(self.memory_cache) > self.max_memory_items * 0.8:
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]['expires_at']
            )
            
            # Keep only the newest 80%
            keep_count = int(self.max_memory_items * 0.8)
            self.memory_cache = dict(sorted_items[-keep_count:])