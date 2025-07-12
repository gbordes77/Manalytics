"""
Application FastAPI principale avec WebSocket
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

from .realtime_service import realtime_service
from ..cache.redis_cache import RedisCache
from ..metrics.business_metrics import BusinessMetrics

logger = logging.getLogger(__name__)

# Configuration
app = FastAPI(
    title="Manalytics API",
    description="API avancée pour l'analyse du métagame Magic: The Gathering",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
cache = RedisCache()
business_metrics = BusinessMetrics()

@app.on_event("startup")
async def startup_event():
    """Démarrage de l'application"""
    logger.info("Démarrage de l'API Manalytics")
    await realtime_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Arrêt de l'application"""
    logger.info("Arrêt de l'API Manalytics")
    await realtime_service.stop()

# Routes WebSocket
@app.websocket("/ws/metagame/{format}")
async def websocket_metagame(websocket: WebSocket, format: str):
    """WebSocket pour mises à jour temps réel du métagame"""
    try:
        await realtime_service.add_connection(websocket, format)
        
        while True:
            # Maintenir la connexion active
            try:
                data = await websocket.receive_text()
                # Traiter les messages du client si nécessaire
                message = json.loads(data)
                
                if message.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong'})
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Erreur WebSocket: {e}")
                break
                
    except Exception as e:
        logger.error(f"Erreur connexion WebSocket: {e}")
    finally:
        realtime_service.remove_connection(websocket)

@app.websocket("/ws/tournament/{tournament_id}")
async def websocket_tournament(websocket: WebSocket, tournament_id: str):
    """WebSocket pour suivi temps réel d'un tournoi"""
    try:
        await websocket.accept()
        
        # Envoyer l'état initial
        tournament_state = await get_tournament_state(tournament_id)
        await websocket.send_json({
            'type': 'tournament_state',
            'tournament_id': tournament_id,
            'data': tournament_state
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'subscribe_round':
                    # S'abonner aux mises à jour des rondes
                    await subscribe_tournament_updates(websocket, tournament_id)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Erreur WebSocket tournoi: {e}")
                break
                
    except Exception as e:
        logger.error(f"Erreur connexion WebSocket tournoi: {e}")

# Routes REST API
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Manalytics API v3.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Vérification de santé"""
    try:
        # Vérifier Redis
        await cache.ping()
        
        # Vérifier les connexions actives
        connections = sum(
            len(conns) for conns in realtime_service.connection_manager.active_connections.values()
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": "connected",
                "websocket": "active",
                "active_connections": connections
            }
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/metagame/{format}")
async def get_metagame(format: str, date: Optional[str] = None):
    """Récupérer le métagame pour un format"""
    try:
        metagame_data = await realtime_service.get_current_metagame(format)
        
        if not metagame_data:
            raise HTTPException(status_code=404, detail=f"Métagame non trouvé pour {format}")
            
        return {
            "format": format,
            "data": metagame_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération métagame: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.get("/metagame/{format}/trends")
async def get_metagame_trends(format: str, days: int = 7):
    """Récupérer les tendances du métagame"""
    try:
        trends = await business_metrics.calculate_trends(format, days)
        
        return {
            "format": format,
            "period_days": days,
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération tendances: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.get("/archetype/{archetype_name}")
async def get_archetype_details(archetype_name: str, format: str):
    """Détails d'un archétype"""
    try:
        details = await get_archetype_analysis(archetype_name, format)
        
        return {
            "archetype": archetype_name,
            "format": format,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération archétype: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.post("/tournament/{tournament_id}/complete")
async def complete_tournament(tournament_id: str, results: Dict):
    """Marquer un tournoi comme terminé et traiter les résultats"""
    try:
        format = results.get('format', 'unknown')
        
        # Traiter les résultats
        await realtime_service.tournament_completed(tournament_id, format, results)
        
        return {
            "tournament_id": tournament_id,
            "status": "processed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur traitement tournoi: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.get("/stats/realtime")
async def get_realtime_stats():
    """Statistiques temps réel"""
    try:
        connections = sum(
            len(conns) for conns in realtime_service.connection_manager.active_connections.values()
        )
        
        # Récupérer les métriques depuis Redis
        updates_count = await cache.get('realtime:updates:tournament_completed') or "0"
        
        return {
            "active_connections": connections,
            "formats_monitored": len(realtime_service.connection_manager.active_connections),
            "total_updates": int(updates_count),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur stats temps réel: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

# Fonctions utilitaires
async def get_tournament_state(tournament_id: str) -> Dict:
    """Récupérer l'état d'un tournoi"""
    try:
        # Récupérer depuis le cache
        cached_state = await cache.get(f"tournament:{tournament_id}")
        if cached_state:
            return json.loads(cached_state)
            
        # État par défaut
        return {
            "tournament_id": tournament_id,
            "status": "unknown",
            "rounds": [],
            "standings": []
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération état tournoi: {e}")
        return {}

async def subscribe_tournament_updates(websocket: WebSocket, tournament_id: str):
    """S'abonner aux mises à jour d'un tournoi"""
    # Logique d'abonnement aux mises à jour
    pass

async def get_archetype_analysis(archetype_name: str, format: str) -> Dict:
    """Analyser un archétype"""
    try:
        # Récupérer les données de l'archétype
        analysis = await business_metrics.analyze_archetype(archetype_name, format)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Erreur analyse archétype: {e}")
        return {}

# Gestionnaire d'erreurs
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'erreurs"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 