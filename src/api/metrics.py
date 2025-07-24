# src/api/metrics.py - Prometheus metrics for the API

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time
from typing import Callable

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_active_requests',
    'Number of active HTTP requests'
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

archetype_detection_duration_seconds = Histogram(
    'archetype_detection_duration_seconds',
    'Time spent detecting archetypes'
)

scraper_runs_total = Counter(
    'scraper_runs_total',
    'Total scraper runs',
    ['source', 'format', 'status']
)

tournaments_scraped_total = Counter(
    'tournaments_scraped_total',
    'Total tournaments scraped',
    ['source', 'format']
)

cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Middleware for request metrics
async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware to collect request metrics."""
    # Skip metrics endpoint to avoid recursion
    if request.url.path == "/metrics":
        return await call_next(request)
    
    # Track active requests
    active_requests.inc()
    
    # Track request duration
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    finally:
        active_requests.dec()

# Metrics endpoint
async def metrics_endpoint():
    """Endpoint to expose metrics for Prometheus."""
    return Response(content=generate_latest(), media_type="text/plain")