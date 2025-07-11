"""
Manalytics Phase 3 - API Layer
Backend FastAPI avec WebSocket pour temps réel
"""

from .realtime_service import RealtimeMetagameService
from .fastapi_app import app
from .websocket_handler import WebSocketHandler

__all__ = [
    'RealtimeMetagameService',
    'app',
    'WebSocketHandler'
] 