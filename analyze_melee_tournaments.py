#!/usr/bin/env python3
"""
Analyser les tournois Melee récupérés pour comprendre leur structure
"""

import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_tournaments():
    """Analyser tous les tournois Melee"""
    
    melee_dir = Path("data/raw/melee/standard")
    json_files = list(melee_dir.glob("*.json"))
    
    logger.info("📊 Analyse des tournois Melee récupérés")
    logger.info("=" * 60)
    logger.info(f"Total: {len(json_files)} tournois")
    logger.info("")
    
    total_players = 0
    tournaments_with_rounds = 0
    
    for json_file in sorted(json_files):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tournament_name = data.get('TournamentName', 'Unknown')
        num_players = len(data.get('Decks', []))
        has_rounds = 'RoundStandings' in data
        
        logger.info(f"📁 {json_file.name}")
        logger.info(f"   Nom: {tournament_name}")
        logger.info(f"   Joueurs: {num_players}")
        logger.info(f"   Round Standings: {'✅ OUI' if has_rounds else '❌ NON'}")
        
        if has_rounds:
            tournaments_with_rounds += 1
            num_rounds = data.get('TotalRounds', 0)
            logger.info(f"   Rounds disponibles: {num_rounds}")
        
        logger.info("")
        total_players += num_players
    
    logger.info("=" * 60)
    logger.info(f"📈 Résumé:")
    logger.info(f"  - Tournois avec Round Standings: {tournaments_with_rounds}/{len(json_files)}")
    logger.info(f"  - Total de joueurs: {total_players}")
    logger.info(f"  - Moyenne par tournoi: {total_players/len(json_files):.1f} joueurs")
    
    if tournaments_with_rounds == 0:
        logger.warning("\n⚠️ AUCUN tournoi n'a de Round Standings!")
        logger.info("💡 Cela suggère un problème avec la récupération des rounds")


if __name__ == "__main__":
    analyze_tournaments()