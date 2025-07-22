"""
Manalytics Phase 3 - API Layer
Backend FastAPI avec WebSocket pour temps réel
"""

# Import seulement les modules qui existent réellement
try:
    from .fastapi_app_full import app
except ImportError:
    try:
        from .fastapi_app import app
    except ImportError:
        app = None

__all__ = ["app"]
