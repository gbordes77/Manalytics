# src/utils/metrics_helper.py - Helper functions for metrics collection

import time
from contextlib import contextmanager
from functools import wraps
from src.api.metrics import (
    archetype_detection_duration_seconds,
    scraper_runs_total,
    tournaments_scraped_total,
    cache_hits_total,
    cache_misses_total,
    db_connections_active
)

@contextmanager
def track_archetype_detection():
    """Context manager to track archetype detection duration."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        archetype_detection_duration_seconds.observe(duration)

def track_scraper_run(source: str, format_name: str):
    """Decorator to track scraper runs."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                scraper_runs_total.labels(
                    source=source,
                    format=format_name,
                    status="success"
                ).inc()
                
                # Count tournaments
                if isinstance(result, list):
                    tournaments_scraped_total.labels(
                        source=source,
                        format=format_name
                    ).inc(len(result))
                
                return result
            except Exception as e:
                scraper_runs_total.labels(
                    source=source,
                    format=format_name,
                    status="error"
                ).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                scraper_runs_total.labels(
                    source=source,
                    format=format_name,
                    status="success"
                ).inc()
                
                # Count tournaments
                if isinstance(result, list):
                    tournaments_scraped_total.labels(
                        source=source,
                        format=format_name
                    ).inc(len(result))
                
                return result
            except Exception as e:
                scraper_runs_total.labels(
                    source=source,
                    format=format_name,
                    status="error"
                ).inc()
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def record_cache_hit(cache_type: str):
    """Record a cache hit."""
    cache_hits_total.labels(cache_type=cache_type).inc()

def record_cache_miss(cache_type: str):
    """Record a cache miss."""
    cache_misses_total.labels(cache_type=cache_type).inc()

@contextmanager
def track_db_connection():
    """Context manager to track active database connections."""
    db_connections_active.inc()
    try:
        yield
    finally:
        db_connections_active.dec()