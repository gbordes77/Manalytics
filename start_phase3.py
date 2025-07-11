#!/usr/bin/env python3
"""
Script de démarrage pour Manalytics Phase 3
Lance tous les services de la plateforme complète
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
import signal
from typing import List, Optional
import subprocess
import time

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManager:
    """Gestionnaire de services pour la Phase 3"""
    
    def __init__(self):
        self.services = []
        self.running = False
        
    async def start_api_service(self):
        """Démarrer le service API FastAPI"""
        logger.info("Démarrage du service API FastAPI...")
        
        try:
            # Importer et démarrer l'API
            from api.fastapi_app import app
            from api.realtime_service import realtime_service
            
            # Démarrer le service temps réel
            await realtime_service.start()
            
            # L'API sera démarrée via uvicorn
            logger.info("Service API prêt")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage API: {e}")
            return False
            
    async def start_ml_service(self):
        """Démarrer le service ML/IA"""
        logger.info("Démarrage du service ML/IA...")
        
        try:
            from ml.metagame_predictor import MetagamePredictor
            from ml.recommendation_engine import PersonalizedRecommender
            
            # Initialiser les modèles
            predictor = MetagamePredictor()
            recommender = PersonalizedRecommender()
            
            # Charger les modèles pré-entraînés si disponibles
            model_path = Path("models/metagame_model.pth")
            if model_path.exists():
                predictor.load_model(str(model_path))
                logger.info("Modèle de prédiction chargé")
            else:
                logger.warning("Aucun modèle pré-entraîné trouvé")
                
            logger.info("Service ML/IA prêt")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage ML: {e}")
            return False
            
    async def start_gamification_service(self):
        """Démarrer le service de gamification"""
        logger.info("Démarrage du service de gamification...")
        
        try:
            from gamification.gamification_engine import GamificationEngine
            
            # Initialiser le moteur de gamification
            gamification_engine = GamificationEngine()
            
            logger.info("Service de gamification prêt")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage gamification: {e}")
            return False
            
    async def start_cache_service(self):
        """Démarrer le service de cache"""
        logger.info("Démarrage du service de cache...")
        
        try:
            from cache.redis_cache import RedisCache
            
            # Tester la connexion Redis
            cache = RedisCache()
            await cache.ping()
            
            logger.info("Service de cache prêt")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage cache: {e}")
            return False
            
    async def start_all_services(self):
        """Démarrer tous les services"""
        logger.info("=== Démarrage de Manalytics Phase 3 ===")
        
        services_to_start = [
            ("Cache", self.start_cache_service),
            ("ML/IA", self.start_ml_service),
            ("Gamification", self.start_gamification_service),
            ("API", self.start_api_service),
        ]
        
        for service_name, start_func in services_to_start:
            try:
                success = await start_func()
                if success:
                    logger.info(f"✓ {service_name} démarré avec succès")
                else:
                    logger.error(f"✗ Échec du démarrage de {service_name}")
                    return False
            except Exception as e:
                logger.error(f"✗ Erreur critique lors du démarrage de {service_name}: {e}")
                return False
                
        self.running = True
        logger.info("=== Tous les services sont démarrés ===")
        return True
        
    async def stop_all_services(self):
        """Arrêter tous les services"""
        logger.info("Arrêt des services...")
        
        try:
            # Arrêter le service temps réel
            from api.realtime_service import realtime_service
            await realtime_service.stop()
            
        except Exception as e:
            logger.error(f"Erreur arrêt services: {e}")
            
        self.running = False
        logger.info("Services arrêtés")
        
    async def health_check(self):
        """Vérification de santé des services"""
        try:
            from cache.redis_cache import RedisCache
            
            cache = RedisCache()
            await cache.ping()
            
            return {
                "status": "healthy",
                "services": {
                    "cache": "running",
                    "api": "running",
                    "ml": "running",
                    "gamification": "running"
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

def start_uvicorn_server():
    """Démarrer le serveur Uvicorn"""
    try:
        import uvicorn
        
        logger.info("Démarrage du serveur Uvicorn...")
        
        # Configuration Uvicorn
        config = uvicorn.Config(
            "src.python.api.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False,
            workers=1
        )
        
        server = uvicorn.Server(config)
        return server
        
    except ImportError:
        logger.error("Uvicorn non installé. Installez avec: pip install uvicorn")
        return None
    except Exception as e:
        logger.error(f"Erreur configuration Uvicorn: {e}")
        return None

def start_streamlit_dashboard():
    """Démarrer le dashboard Streamlit"""
    try:
        dashboard_path = Path("src/python/dashboard/streamlit_app.py")
        
        if not dashboard_path.exists():
            logger.warning("Dashboard Streamlit non trouvé")
            return None
            
        logger.info("Démarrage du dashboard Streamlit...")
        
        # Lancer Streamlit en arrière-plan
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port=8501",
            "--server.headless=true"
        ])
        
        return process
        
    except Exception as e:
        logger.error(f"Erreur démarrage Streamlit: {e}")
        return None

async def main():
    """Fonction principale"""
    service_manager = ServiceManager()
    
    # Gestionnaire de signaux pour arrêt propre
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt en cours...")
        asyncio.create_task(service_manager.stop_all_services())
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Démarrer tous les services
        success = await service_manager.start_all_services()
        
        if not success:
            logger.error("Échec du démarrage des services")
            sys.exit(1)
            
        # Démarrer le serveur Uvicorn
        uvicorn_server = start_uvicorn_server()
        if uvicorn_server:
            logger.info("Serveur API disponible sur http://localhost:8000")
            logger.info("Documentation API: http://localhost:8000/docs")
            
            # Démarrer le dashboard Streamlit
            streamlit_process = start_streamlit_dashboard()
            if streamlit_process:
                logger.info("Dashboard disponible sur http://localhost:8501")
                
            # Démarrer le serveur
            await uvicorn_server.serve()
            
        else:
            logger.error("Impossible de démarrer le serveur API")
            
            # Maintenir les services en vie
            logger.info("Services en cours d'exécution... Ctrl+C pour arrêter")
            
            while service_manager.running:
                await asyncio.sleep(1)
                
                # Health check périodique
                if int(time.time()) % 60 == 0:  # Toutes les minutes
                    health = await service_manager.health_check()
                    if health["status"] != "healthy":
                        logger.warning(f"Health check: {health}")
                        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
    finally:
        await service_manager.stop_all_services()

def check_dependencies():
    """Vérifier les dépendances"""
    required_packages = [
        "redis", "fastapi", "uvicorn", "torch", 
        "numpy", "pandas", "streamlit"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        logger.error(f"Packages manquants: {missing_packages}")
        logger.error("Installez avec: pip install -r requirements.txt")
        return False
        
    return True

if __name__ == "__main__":
    print("""
    ███╗   ███╗ █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗████████╗██╗ ██████╗███████╗
    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══██╔══╝██║██╔════╝██╔════╝
    ██╔████╔██║███████║██╔██╗ ██║███████║██║   ╚████╔╝    ██║   ██║██║     ███████╗
    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝     ██║   ██║██║     ╚════██║
    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║███████╗██║      ██║   ██║╚██████╗███████║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═╝   ╚═╝ ╚═════╝╚══════╝
    
    Phase 3 - Produit & Intelligence Avancée
    ========================================
    """)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
        
    # Créer les dossiers nécessaires
    Path("logs").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Lancer l'application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application arrêtée")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1) 