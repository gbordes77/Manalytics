"""
Wrapper pour utiliser les scrapers standalone avec l'orchestrateur
"""
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class StandaloneMTGOScraper:
    """Wrapper pour scrape_mtgo_standalone.py"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent.parent.parent.parent / "scrape_mtgo_standalone.py"
        
    def scrape_format(self, format_name: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Lance le scraper MTGO standalone
        
        Returns:
            Liste des tournois (métadonnées uniquement pour MTGO)
        """
        logger.info(f"Running MTGO standalone scraper for {format_name}")
        
        # Le script actuel ne prend pas de paramètres, il scrape tout juillet 2025
        # On pourrait le modifier pour accepter des dates, mais pour l'instant on le lance tel quel
        try:
            result = subprocess.run(
                ["python3", str(self.script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"MTGO scraper failed: {result.stderr}")
                return []
                
            # Le script sauvegarde directement les fichiers, on retourne un résumé
            logger.info("MTGO scraping completed successfully")
            
            # Compter les fichiers créés
            data_dir = Path("data/raw/mtgo") / format_name
            if data_dir.exists():
                files = list(data_dir.glob("*.json"))
                return [{"format": format_name, "files_created": len(files)}]
            
            return []
            
        except Exception as e:
            logger.error(f"Error running MTGO scraper: {e}")
            return []


class StandaloneMeleeScraper:
    """Wrapper pour scrape_melee_from_commit.py"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent.parent.parent.parent / "scrape_melee_from_commit.py"
        
    def scrape_tournaments(self, format_name: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Lance le scraper Melee standalone
        
        Returns:
            Liste des tournois avec leurs decklists
        """
        logger.info(f"Running Melee standalone scraper for {format_name}")
        
        # Le script actuel est configuré pour Standard et dates fixes
        # On pourrait le modifier pour accepter des paramètres
        try:
            result = subprocess.run(
                ["python3", str(self.script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Melee scraper failed: {result.stderr}")
                return []
                
            logger.info("Melee scraping completed successfully")
            
            # Charger les tournois créés
            tournaments = []
            data_dir = Path("data/raw/melee") / format_name.lower()
            
            if data_dir.exists():
                for json_file in data_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Convertir au format attendu par l'orchestrateur
                            tournaments.append({
                                'name': data.get('TournamentName', ''),
                                'date': data.get('TournamentStartDate', ''),
                                'decklists': [
                                    {
                                        'player': deck.get('PlayerName', ''),
                                        'mainboard': [],  # Les détails sont dans le fichier
                                        'sideboard': []
                                    }
                                    for deck in data.get('Decks', [])
                                ]
                            })
                    except Exception as e:
                        logger.error(f"Error loading {json_file}: {e}")
                        
            return tournaments
            
        except Exception as e:
            logger.error(f"Error running Melee scraper: {e}")
            return []


# Pour remplacer dans l'orchestrateur
def get_standalone_scrapers():
    """Retourne les scrapers standalone pour l'orchestrateur"""
    return {
        'mtgo': StandaloneMTGOScraper(),
        'melee': StandaloneMeleeScraper()
    }