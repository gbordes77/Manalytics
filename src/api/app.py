from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from config.settings import settings
from src.api.routes import decks, archetypes, analysis, auth, visualizations
from src.api.metrics import metrics_middleware, metrics_endpoint
from src.api.auth import get_current_active_user
from database.db_pool import get_db_connection

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add metrics middleware
app.middleware("http")(metrics_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    return await metrics_endpoint()

# Include API routers
# Authentication routes (public)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Protected routes - require authentication
app.include_router(
    decks.router, 
    prefix="/api/decks", 
    tags=["Decks"],
    dependencies=[Depends(get_current_active_user)]
)

# Public routes
app.include_router(archetypes.router, prefix="/api/archetypes", tags=["Archetypes"])
app.include_router(analysis.router)
app.include_router(visualizations.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        # Test Redis connection
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

# Remove the redirections - FastAPI handles trailing slashes automatically
# The 307 redirects are expected behavior when calling without trailing slash

def main():
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)