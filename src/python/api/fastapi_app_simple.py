"""
FastAPI application simple pour Manalytics
Version simplifiée qui évite les problèmes d'import
"""

import os
import sys
import json
import uvicorn
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import asyncio
import glob

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configuration du logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de l'application
app = FastAPI(
    title="Manalytics API",
    description="API pour l'analyse du métagame Magic: The Gathering",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin vers les données
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
REAL_DATA_PATH = PROJECT_ROOT / "real_data"

def load_real_data() -> Dict[str, Any]:
    """Charge les vraies données du dataset."""
    try:
        data_file = REAL_DATA_PATH / "complete_dataset.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Fichier de données non trouvé: {data_file}")
            return {}
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        return {}

def get_data_info() -> Dict[str, Any]:
    """Retourne les informations sur les données disponibles."""
    data = load_real_data()
    if not data:
        return {"error": "Aucune donnée disponible"}
    
    # Les données sont un array direct de decks
    decks = data if isinstance(data, list) else []
    
    # Récupérer les tournois uniques
    tournaments = set()
    for deck in decks:
        tournament_id = deck.get('tournament_id')
        if tournament_id:
            tournaments.add(tournament_id)
    
    # Statistiques par archétype
    archetype_stats = {}
    for deck in decks:
        archetype = deck.get('archetype', 'Unknown')
        if archetype not in archetype_stats:
            archetype_stats[archetype] = 0
        archetype_stats[archetype] += 1
    
    # Calcul des pourcentages
    total_decks = len(decks)
    archetype_percentages = {}
    for archetype, count in archetype_stats.items():
        percentage = (count / total_decks * 100) if total_decks > 0 else 0
        archetype_percentages[archetype] = {
            'count': count,
            'percentage': round(percentage, 2)
        }
    
    return {
        'total_tournaments': len(tournaments),
        'total_decks': total_decks,
        'archetype_distribution': archetype_percentages,
        'data_loaded': True
    }

@app.get("/")
async def root():
    """Endpoint principal de l'API."""
    return {
        "message": "Bienvenue sur l'API Manalytics",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état du système."""
    data_info = get_data_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_status": "loaded" if data_info.get('data_loaded') else "error",
        "total_decks": data_info.get('total_decks', 0)
    }

@app.get("/metagame")
async def get_metagame_data(
    format: Optional[str] = Query(None, description="Format de jeu"),
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)")
):
    """Retourne les données du métagame."""
    data = load_real_data()
    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible")
    
    # Les données sont un array direct de decks
    decks = data if isinstance(data, list) else []
    
    # Récupérer les tournois uniques
    tournaments = set()
    for deck in decks:
        tournament_id = deck.get('tournament_id')
        if tournament_id:
            tournaments.add(tournament_id)
    
    if format:
        # Filtrer par format si disponible dans les données
        filtered_decks = [deck for deck in decks if deck.get('tournament_format', '').lower() == format.lower()]
        if filtered_decks:
            decks = filtered_decks
    
    # Analyse des archétypes
    archetype_stats = {}
    for deck in decks:
        archetype = deck.get('archetype', 'Unknown')
        if archetype not in archetype_stats:
            archetype_stats[archetype] = {
                'count': 0,
                'wins': 0,
                'losses': 0,
                'decks': []
            }
        
        archetype_stats[archetype]['count'] += 1
        archetype_stats[archetype]['wins'] += deck.get('wins', 0)
        archetype_stats[archetype]['losses'] += deck.get('losses', 0)
        archetype_stats[archetype]['decks'].append(deck)
    
    # Calcul des pourcentages et winrates
    total_decks = len(decks)
    metagame_analysis = {}
    
    for archetype, stats in archetype_stats.items():
        total_games = stats['wins'] + stats['losses']
        winrate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
        meta_share = (stats['count'] / total_decks * 100) if total_decks > 0 else 0
        
        metagame_analysis[archetype] = {
            'deck_count': stats['count'],
            'meta_share': round(meta_share, 2),
            'wins': stats['wins'],
            'losses': stats['losses'],
            'winrate': round(winrate, 2),
            'total_games': total_games
        }
    
    return {
        'format': format or 'All',
        'total_decks': total_decks,
        'total_tournaments': len(tournaments),
        'archetype_analysis': metagame_analysis,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/real-data")
async def get_real_data_info():
    """Retourne les informations sur les données réelles."""
    return get_data_info()

@app.post("/generate-analysis")
async def generate_analysis(request: Request):
    """Endpoint pour générer une analyse de métagame."""
    try:
        # Récupérer les données JSON du body
        data = await request.json()
        format = data.get('format')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not format or not start_date or not end_date:
            raise HTTPException(status_code=400, detail="Format, start_date et end_date sont requis")

        # Vérifier si les dates sont valides
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")

        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin.")

        # Construire la commande
        command = f"python analyze_real_standard_data.py"
        
        # Changer vers le répertoire du projet
        project_dir = "/Volumes/DataDisk/_Projects/Manalytics"
        
        # Exécuter la commande
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_dir
        )

        stdout, stderr = await process.communicate()
        exit_code = process.returncode

        if exit_code != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'exécution de la commande: {stderr.decode('utf-8')}"
            )

        # Vérifier les fichiers générés dans le dossier avec les dates
        
        # Chercher le dossier standard_analysis_* le plus récent
        pattern = os.path.join(project_dir, "standard_analysis_*")
        analysis_dirs = glob.glob(pattern)
        
        if analysis_dirs:
            # Prendre le plus récent
            analysis_dir = max(analysis_dirs, key=os.path.getctime)
            generated_files = []
            
            for root, dirs, files in os.walk(analysis_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_dir)
                    generated_files.append(rel_path)
        else:
            analysis_dir = None
            generated_files = []
        
        return {
            "message": "Analyse générée avec succès",
            "command": command,
            "stdout": stdout.decode('utf-8'),
            "stderr": stderr.decode('utf-8'),
            "generated_files": generated_files,
            "analysis_dir": analysis_dir
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'analyse: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {e}")

@app.get("/files/{file_path:path}")
async def serve_generated_file(file_path: str):
    """Servir les fichiers générés."""
    full_path = os.path.join("/Volumes/DataDisk/_Projects/Manalytics", file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    # Déterminer le type de contenu
    if file_path.endswith('.html'):
        media_type = 'text/html'
    elif file_path.endswith('.json'):
        media_type = 'application/json'
    elif file_path.endswith('.png'):
        media_type = 'image/png'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(full_path, media_type=media_type)

@app.post("/open-finder")
async def open_finder(request: Request):
    """Ouvre le Finder sur macOS avec le chemin spécifié."""
    try:
        data = await request.json()
        path = data.get('path')
        
        if not path or not os.path.exists(path):
            return {"success": False, "error": "Chemin invalide"}
        
        # Commande pour ouvrir le Finder sur macOS
        process = await asyncio.create_subprocess_shell(
            f"open '{path}'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {"success": True, "message": "Finder ouvert avec succès"}
        else:
            return {"success": False, "error": stderr.decode('utf-8')}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Interface web avec timeline chronologique."""
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manalytics - Analyse Métagame Magic</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            
            .container {
                display: flex;
                min-height: 100vh;
            }
            
            /* Timeline Sidebar */
            .timeline-sidebar {
                width: 320px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(255, 255, 255, 0.2);
                padding: 20px;
                overflow-y: auto;
                max-height: 100vh;
            }
            
            .timeline-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                text-align: center;
                color: #fff;
            }
            
            .timeline-item {
                display: flex;
                align-items: center;
                margin: 15px 0;
                padding: 12px;
                border-radius: 8px;
                transition: all 0.3s ease;
                cursor: default;
            }
            
            .timeline-item.ban {
                background: rgba(255, 107, 107, 0.1);
                border-left: 4px solid #ff6b6b;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
            }
            
            .timeline-item.ban:hover {
                background: rgba(255, 107, 107, 0.2);
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
            }
            
            .timeline-item.release {
                background: rgba(81, 207, 102, 0.1);
                border-left: 4px solid #51cf66;
            }
            
            .timeline-item.release:hover {
                background: rgba(81, 207, 102, 0.15);
                transform: translateX(3px);
            }
            
            .timeline-item.future {
                border-left-color: #2196F3;
                opacity: 0.8;
            }
            
            .timeline-icon {
                font-size: 20px;
                margin-right: 12px;
                min-width: 24px;
            }
            
            .timeline-content {
                flex: 1;
            }
            
            .timeline-date {
                font-size: 12px;
                opacity: 0.8;
                margin-bottom: 4px;
            }
            
            .timeline-text {
                font-size: 14px;
                font-weight: 500;
            }
            
            /* Main Content */
            .main-content {
                flex: 1;
                padding: 10px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
            }
            
            .header {
                text-align: center;
                margin-bottom: 5px;
            }
            
            .logo {
                font-size: 48px;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 42px;
                font-weight: 700;
                margin-bottom: 5px;
                background: linear-gradient(45deg, #fff, #e0e0e0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .subtitle {
                font-size: 18px;
                opacity: 0.9;
                margin-bottom: 10px;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                width: 100%;
                max-width: 1200px;
                margin-bottom: 10px;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                opacity: 0;
                transform: translateY(20px);
            }
            
            .feature-card:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            .feature-icon {
                font-size: 32px;
                margin-bottom: 15px;
            }
            
            .feature-title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            
            .feature-desc {
                font-size: 14px;
                opacity: 0.8;
                line-height: 1.5;
            }
            
            .formats-section {
                text-align: center;
                width: 100%;
                max-width: 800px;
            }
            
            .formats-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 25px;
            }
            
            .format-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .format-btn {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .format-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            .format-btn.standard {
                background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
                border-color: #ff6b6b;
            }
            
            .format-btn.modern {
                background: linear-gradient(45deg, #4CAF50, #2E7D32);
            }
            
            .analyses-section {
                margin-top: 40px;
                text-align: center;
            }
            
            .analyses-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .analyses-placeholder {
                background: rgba(255, 255, 255, 0.1);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 40px 20px;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .placeholder-icon {
                font-size: 48px;
                margin-bottom: 15px;
                opacity: 0.6;
            }
            
            .placeholder-text {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
                opacity: 0.9;
            }
            
            .placeholder-desc {
                font-size: 14px;
                opacity: 0.7;
                line-height: 1.5;
            }
            
            /* Section Analyses Avancées */
            .advanced-section {
                text-align: center;
                margin-bottom: 5px;
                padding: 5px 0;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }
            
            .section-title {
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .section-subtitle {
                font-size: 16px;
                opacity: 0.8;
                max-width: 600px;
                margin: 0 auto;
                line-height: 1.5;
            }
            
            /* Générateur d'analyses */
            .generator-section {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 30px;
                margin-top: 40px;
                text-align: center;
            }
            
            .generator-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .generator-form {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .form-row {
                display: flex;
                gap: 20px;
                align-items: end;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
                min-width: 150px;
            }
            
            .form-group label {
                font-size: 14px;
                font-weight: 500;
                opacity: 0.9;
                text-align: left;
            }
            
            .form-select,
            .form-input {
                padding: 12px 16px;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .form-select:focus,
            .form-input:focus {
                outline: none;
                border-color: #FFD700;
                box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.2);
            }
            
            .form-select option {
                background: #1a1a1a;
                color: white;
            }
            
            .generate-btn {
                padding: 12px 24px;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .generate-btn:hover {
                background: linear-gradient(45deg, #45a049, #4CAF50);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }
            
            .generate-btn:active {
                transform: translateY(0);
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .container {
                    flex-direction: column;
                }
                
                .timeline-sidebar {
                    width: 100%;
                    max-height: 300px;
                }
                
                .main-content {
                    padding: 20px;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .format-buttons {
                    flex-direction: column;
                    align-items: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="timeline-sidebar">
                <div class="timeline-title">📅 Timeline Magic</div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">12 juillet 2024</div>
                        <div class="timeline-text">Bloomburrow</div>
                    </div>
                </div>
                
                <a href="https://magic.wizards.com/en/news/announcements/august-26-2024-banned-and-restricted-announcement" target="_blank" class="timeline-item ban">
                    <div class="timeline-icon">⚡</div>
                    <div class="timeline-content">
                        <div class="timeline-date">26 août 2024</div>
                        <div class="timeline-text">Ban Modern/Legacy : Nadu + Grief<br/>Ban Pioneer : Amalia + Sorin</div>
                    </div>
                </a>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">27 septembre 2024</div>
                        <div class="timeline-text">Duskmourn: House of Horror</div>
                    </div>
                </div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">15 novembre 2024</div>
                        <div class="timeline-text">Foundations</div>
                    </div>
                </div>
                
                <a href="https://magic.wizards.com/en/news/announcements/banned-and-restricted-december-16-2024" target="_blank" class="timeline-item ban">
                    <div class="timeline-icon">⚡</div>
                    <div class="timeline-content">
                        <div class="timeline-date">16 déc 2024</div>
                        <div class="timeline-text">Ban Modern : The One Ring<br/>Ban Legacy : Psychic Frog</div>
                    </div>
                </a>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">25 janvier 2025</div>
                        <div class="timeline-text">Innistrad Remastered</div>
                    </div>
                </div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">14 février 2025</div>
                        <div class="timeline-text">Aetherdrift</div>
                    </div>
                </div>
                
                <a href="https://magic.wizards.com/en/news/announcements/march-31-2025-banned-and-restricted-announcement" target="_blank" class="timeline-item ban">
                    <div class="timeline-icon">⚡</div>
                    <div class="timeline-content">
                        <div class="timeline-date">31 mars 2025</div>
                        <div class="timeline-text">Ban Modern : Underworld Breach<br/>Ban Legacy : Troll + Sowing Mycospawn</div>
                    </div>
                </a>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">11 avril 2025</div>
                        <div class="timeline-text">Tarkir: Dragonstorm</div>
                    </div>
                </div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">13 juin 2025</div>
                        <div class="timeline-text">Final Fantasy</div>
                    </div>
                </div>
                
                <a href="https://magic.wizards.com/en/news/announcements/banned-and-restricted-june-30-2025?utm_source=chatgpt.com" target="_blank" class="timeline-item ban">
                    <div class="timeline-icon">⚡</div>
                    <div class="timeline-content">
                        <div class="timeline-date">30 juin 2025</div>
                        <div class="timeline-text">Ban Standard : 7 cartes<br/>Cori-Steel Cutter, Monstrous Rage, etc.</div>
                    </div>
                </a>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">1 août 2025</div>
                        <div class="timeline-text">Edge of Eternities</div>
                    </div>
                </div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">26 septembre 2025</div>
                        <div class="timeline-text">Spider-Man</div>
                    </div>
                </div>
                
                <div class="timeline-item release">
                    <div class="timeline-icon">🎁</div>
                    <div class="timeline-content">
                        <div class="timeline-date">21 novembre 2025</div>
                        <div class="timeline-text">Avatar: The Last Airbender</div>
                    </div>
                </div>
                
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <div class="header">
                    <div class="logo">📊</div>
                    <h1 class="title">Manalytics</h1>
                    <p class="subtitle">Analyse avancée du métagame Magic: The Gathering</p>
                </div>
                
                <!-- Section Analyses Avancées -->
                <div class="advanced-section">
                    <div class="section-title">
                        🔬 Analyses Avancées
                    </div>
                    <div class="section-subtitle">
                        Outils d'analyse professionnels pour le métagame Magic
                    </div>
                </div>

                <!-- 4 carrés en parallèle -->
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">Performance</div>
                        <div class="feature-desc">Analyse des performances par archétype</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <div class="feature-title">Metagame</div>
                        <div class="feature-desc">Répartition et tendances du métagame</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚔️</div>
                        <div class="feature-title">Matchup</div>
                        <div class="feature-desc">Matrice des matchups entre archétypes</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📈</div>
                        <div class="feature-title">Evolution</div>
                        <div class="feature-desc">Évolution temporelle du métagame</div>
                    </div>
                </div>

                <!-- Ligne d'interaction pour générer les analyses -->
                <div class="generator-section">
                    <div class="generator-title">
                        ⚡ Générateur d'Analyses
                    </div>
                    <div class="generator-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="format-select">Format</label>
                                <select id="format-select" class="form-select">
                                    <option value="standard">Standard</option>
                                    <option value="modern">Modern</option>
                                    <option value="pioneer">Pioneer</option>
                                    <option value="legacy">Legacy</option>
                                    <option value="vintage">Vintage</option>
                                    <option value="pauper">Pauper</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="start-date">Date de début</label>
                                <input type="date" id="start-date" class="form-input">
                            </div>
                            <div class="form-group">
                                <label for="end-date">Date de fin</label>
                                <input type="date" id="end-date" class="form-input">
                            </div>
                            <div class="form-group">
                                <button id="generate-btn" class="generate-btn">
                                    🚀 Générer l'Analyse
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Section Analyses Disponibles -->
                <div class="analyses-section">
                    <div class="analyses-title">
                        📈 Analyses Disponibles
                    </div>
                    <div class="analyses-placeholder">
                        <div class="placeholder-icon">🔍</div>
                        <div class="placeholder-text">
                            Vos analyses personnalisées apparaîtront ici
                        </div>
                        <div class="placeholder-desc">
                            Utilisez le générateur ci-dessus pour créer de nouvelles analyses
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Animation au chargement
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.feature-card');
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 100);
                });
                
                // Initialiser les dates par défaut
                const today = new Date();
                const oneMonthAgo = new Date();
                oneMonthAgo.setMonth(today.getMonth() - 1);
                
                document.getElementById('start-date').value = oneMonthAgo.toISOString().split('T')[0];
                document.getElementById('end-date').value = today.toISOString().split('T')[0];
                
                // Gérer le clic sur le bouton générer
                document.getElementById('generate-btn').addEventListener('click', function() {
                    const format = document.getElementById('format-select').value;
                    const startDate = document.getElementById('start-date').value;
                    const endDate = document.getElementById('end-date').value;
                    
                    if (!startDate || !endDate) {
                        alert('Veuillez sélectionner les dates de début et de fin.');
                        return;
                    }
                    
                    if (new Date(startDate) > new Date(endDate)) {
                        alert('La date de début doit être antérieure à la date de fin.');
                        return;
                    }
                    
                    // Changer le texte du bouton pendant le traitement
                    const btn = this;
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '⏳ Génération en cours...';
                    btn.disabled = true;
                    
                    // Construire la commande
                    const command = `python advanced_metagame_analyzer.py --format ${format} --start-date ${startDate} --end-date ${endDate}`;
                    
                    // Afficher la commande générée
                    console.log('Commande générée:', command);
                    
                    // Faire un vrai appel API
                    const requestData = {
                        format: format,
                        start_date: startDate,
                        end_date: endDate
                    };
                    
                    fetch('/generate-analysis', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(requestData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            // Afficher un message de succès avec les fichiers générés
                            let filesHtml = '';
                            if (data.generated_files && data.generated_files.length > 0) {
                                filesHtml = '<div class="generated-files">';
                                filesHtml += '<h4>📁 Fichiers générés :</h4>';
                                
                                data.generated_files.forEach(file => {
                                    const fileName = file.split('/').pop();
                                    const fileType = file.split('.').pop().toLowerCase();
                                    let icon = '📄';
                                    
                                    if (fileType === 'html') icon = '🌐';
                                    else if (fileType === 'png') icon = '🖼️';
                                    else if (fileType === 'json') icon = '📊';
                                    
                                    filesHtml += `
                                        <div class="file-item">
                                            <a href="/files/${file}" target="_blank" class="file-link">
                                                ${icon} ${fileName}
                                            </a>
                                        </div>
                                    `;
                                });
                                
                                filesHtml += '</div>';
                                
                                // Bouton pour ouvrir le Finder
                                filesHtml += `
                                    <div class="finder-section">
                                        <button class="finder-btn" onclick="openFinder('${data.analysis_dir}')">
                                            🗂️ Ouvrir dans le Finder
                                        </button>
                                    </div>
                                `;
                            }
                            
                            const placeholder = document.querySelector('.analyses-placeholder');
                            placeholder.innerHTML = `
                                <div class="success-result">
                                    <div class="placeholder-icon">✅</div>
                                    <div class="placeholder-text">
                                        Analyse ${format.toUpperCase()} générée !
                                    </div>
                                    <div class="placeholder-desc">
                                        Période: ${startDate} au ${endDate}<br/>
                                        Commande: ${data.command}<br/>
                                        Résultat: 🎯 Lancement de l'analyse complète
                                    </div>
                                    ${filesHtml}
                                </div>
                            `;
                        } else {
                            throw new Error(data.detail || 'Erreur inconnue');
                        }
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        const placeholder = document.querySelector('.analyses-placeholder');
                        placeholder.innerHTML = `
                            <div class="placeholder-icon">❌</div>
                            <div class="placeholder-text">
                                Erreur lors de la génération
                            </div>
                            <div class="placeholder-desc">
                                ${error.message || 'Une erreur est survenue'}
                            </div>
                        `;
                    })
                    .finally(() => {
                        // Restaurer le bouton
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    });
                });
            });
            
            // Fonction pour ouvrir le Finder (macOS uniquement)
            function openFinder(path) {
                // Essayer d'ouvrir le Finder via une requête au serveur
                fetch('/open-finder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ path: path })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Finder ouvert avec succès');
                    } else {
                        // Fallback: copier le chemin dans le presse-papiers
                        navigator.clipboard.writeText(path).then(() => {
                            alert('Chemin copié dans le presse-papiers: ' + path);
                        });
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    // Fallback: copier le chemin dans le presse-papiers
                    navigator.clipboard.writeText(path).then(() => {
                        alert('Chemin copié dans le presse-papiers: ' + path);
                    });
                });
            }
        </script>
        
        <style>
            /* Styles pour les fichiers générés */
            .generated-files {
                margin-top: 20px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .generated-files h4 {
                margin-bottom: 10px;
                color: #fff;
                font-size: 16px;
            }
            
            .file-item {
                margin: 8px 0;
            }
            
            .file-link {
                display: inline-block;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.1);
                color: #fff;
                text-decoration: none;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
                font-size: 14px;
            }
            
            .file-link:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            
            .finder-section {
                margin-top: 15px;
                text-align: center;
            }
            
            .finder-btn {
                padding: 10px 20px;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .finder-btn:hover {
                background: linear-gradient(45deg, #45a049, #4CAF50);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }
            
            .success-result {
                text-align: center;
            }
        </style>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Démarrage du serveur Manalytics API Simple")
    print(f"📁 Répertoire projet: {PROJECT_ROOT}")
    print(f"📊 Données: {REAL_DATA_PATH}")
    
    # Vérification des données
    data_info = get_data_info()
    if data_info.get('data_loaded'):
        print(f"✅ Données chargées: {data_info['total_decks']} decks, {data_info['total_tournaments']} tournois")
    else:
        print("⚠️  Aucune donnée trouvée")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 