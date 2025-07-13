#!/usr/bin/env python3

import argparse
import asyncio
import aiofiles
import json
import os
import sys
from pathlib import Path
from typing import List
import structlog
from tqdm import tqdm

from src.python.classifier.archetype_engine import ArchetypeEngine

logger = structlog.get_logger()

async def process_tournament_file(file_path: str, engine: ArchetypeEngine, format_name: str, output_dir: str) -> bool:
    """Traiter un fichier de tournoi individuel"""
    try:
        # Lire le fichier d'entrée
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            tournament_data = json.loads(content)
            
        # Classifier les decks
        classified_data = engine.classify_tournament(tournament_data, format_name)
        
        # Créer le chemin de sortie en conservant la structure
        relative_path = os.path.relpath(file_path, os.path.dirname(file_path))
        output_path = os.path.join(output_dir, relative_path)
        
        # Créer les dossiers de sortie si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Sauvegarder le fichier classifié
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(classified_data, indent=2, ensure_ascii=False))
            
        # Compter les archétypes trouvés
        archetype_counts = {}
        for deck in classified_data.get('decks', []):
            archetype = deck.get('archetype', 'Unknown')
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            
        logger.info("Tournament classified", 
                   file=os.path.basename(file_path),
                   total_decks=len(classified_data.get('decks', [])),
                   archetypes=len(archetype_counts),
                   unknown_count=archetype_counts.get('Unknown', 0))
        
        return True
        
    except Exception as e:
        logger.error("Failed to process tournament file", file=file_path, error=str(e))
        return False

async def find_tournament_files(input_dir: str) -> List[str]:
    """Trouver tous les fichiers de tournoi à traiter"""
    tournament_files = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json') and 'tournament_' in file:
                tournament_files.append(os.path.join(root, file))
                
    return tournament_files

async def main():
    parser = argparse.ArgumentParser(description='Classifier les archétypes des decklists')
    parser.add_argument('--input', required=True, help='Dossier contenant les fichiers de tournoi')
    parser.add_argument('--output', required=True, help='Dossier de sortie pour les fichiers classifiés')
    parser.add_argument('--format', required=True, help='Format Magic (Modern, Legacy, etc.)')
    parser.add_argument('--rules', required=True, help='Chemin vers MTGOFormatData')
    parser.add_argument('--concurrency', type=int, default=10, help='Nombre de fichiers traités en parallèle')
    
    args = parser.parse_args()
    
    # Configuration du logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger.info("Starting classification", 
               input_dir=args.input,
               output_dir=args.output,
               format=args.format,
               rules_path=args.rules)
    
    # Initialiser le moteur de classification
    engine = ArchetypeEngine(args.rules)
    
    # Charger les données du format
    if not engine.load_format_data(args.format):
        logger.error("Failed to load format data")
        sys.exit(1)
        
    # Trouver tous les fichiers à traiter
    tournament_files = await find_tournament_files(args.input)
    
    if not tournament_files:
        logger.warning("No tournament files found")
        sys.exit(0)
        
    logger.info("Found tournament files", count=len(tournament_files))
    
    # Créer le dossier de sortie
    os.makedirs(args.output, exist_ok=True)
    
    # Traiter les fichiers avec un semaphore pour limiter la concurrence
    semaphore = asyncio.Semaphore(args.concurrency)
    
    async def process_with_semaphore(file_path: str):
        async with semaphore:
            return await process_tournament_file(file_path, engine, args.format, args.output)
    
    # Lancer le traitement avec barre de progression
    tasks = [process_with_semaphore(file_path) for file_path in tournament_files]
    
    results = []
    with tqdm(total=len(tasks), desc="Processing tournaments") as pbar:
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            pbar.update(1)
            
    # Statistiques finales
    successful = sum(results)
    failed = len(results) - successful
    
    logger.info("Classification completed", 
               total_files=len(tournament_files),
               successful=successful,
               failed=failed)
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 