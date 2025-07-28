#!/usr/bin/env python3
"""
Analyser les données Melee pour reconstruire les matchs depuis les standings finaux.
Ceci est une preuve de concept pour montrer qu'on peut déduire certains matchs.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def load_tournament(filepath: Path) -> Dict:
    """Charger un tournoi Melee"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_swiss_pairings(tournament_data: Dict) -> List[Dict]:
    """
    Analyser les pairings possibles basés sur le système Swiss.
    Dans Swiss, les joueurs avec le même score jouent ensemble.
    """
    decks = tournament_data.get('Decks', [])
    total_players = tournament_data.get('TotalPlayers', len(decks))
    
    # Créer un mapping player -> deck info
    player_info = {}
    for deck in decks:
        player = deck.get('PlayerName', '').strip()
        if player:
            player_info[player] = {
                'deck': deck.get('DeckName', 'Unknown'),
                'rank': deck.get('Rank', 999),
                'wins': deck.get('Wins', 0),
                'losses': deck.get('Losses', 0),
                'record': f"{deck.get('Wins', 0)}-{deck.get('Losses', 0)}"
            }
    
    logger.info(f"🎯 Analyse du tournoi: {tournament_data.get('TournamentName')}")
    logger.info(f"📊 {total_players} joueurs")
    logger.info(f"🏆 Format: {tournament_data.get('FormatDescription')}")
    logger.info("")
    
    # Grouper par record
    by_record = {}
    for player, info in player_info.items():
        record = info['record']
        if record not in by_record:
            by_record[record] = []
        by_record[record].append((player, info))
    
    # Afficher les groupes
    logger.info("📋 Groupes par record (pour Swiss pairing):")
    for record, players in sorted(by_record.items(), key=lambda x: x[0], reverse=True):
        logger.info(f"\n  Record {record}: {len(players)} joueurs")
        for player, info in sorted(players, key=lambda x: x[1]['rank']):
            logger.info(f"    #{info['rank']:2d} {player:20s} - {info['deck']}")
    
    # Calculer le nombre de rounds
    import math
    num_rounds = int(math.ceil(math.log2(total_players)))
    logger.info(f"\n🎲 Nombre de rounds estimé (Swiss): {num_rounds}")
    
    # Analyser les matchups possibles du dernier round
    logger.info("\n🔍 Matchups probables du dernier round:")
    logger.info("(Basé sur le principe que les joueurs avec le même record s'affrontent)")
    
    possible_matches = []
    for record, players in by_record.items():
        if len(players) < 2:
            continue
            
        logger.info(f"\n  Bracket {record}:")
        # Dans chaque bracket, on suppose que les joueurs adjacents par rang ont joué
        sorted_players = sorted(players, key=lambda x: x[1]['rank'])
        
        for i in range(0, len(sorted_players) - 1, 2):
            if i + 1 < len(sorted_players):
                p1, info1 = sorted_players[i]
                p2, info2 = sorted_players[i + 1]
                
                # Déterminer le gagnant probable (meilleur rang = gagnant)
                if info1['rank'] < info2['rank']:
                    winner = p1
                    winner_deck = info1['deck']
                else:
                    winner = p2
                    winner_deck = info2['deck']
                
                match = {
                    'player1': p1,
                    'deck1': info1['deck'],
                    'player2': p2,
                    'deck2': info2['deck'],
                    'winner': winner,
                    'winner_deck': winner_deck,
                    'record_bracket': record
                }
                possible_matches.append(match)
                
                logger.info(f"    {p1} ({info1['deck']}) vs {p2} ({info2['deck']})")
                logger.info(f"    → Gagnant probable: {winner}")
    
    return possible_matches


def calculate_archetype_distribution(tournament_data: Dict) -> Dict[str, int]:
    """Calculer la distribution des archétypes"""
    archetype_count = {}
    
    for deck in tournament_data.get('Decks', []):
        archetype = deck.get('DeckName', 'Unknown')
        archetype_count[archetype] = archetype_count.get(archetype, 0) + 1
    
    return archetype_count


def main():
    # Analyser le tournoi Boa
    boa_path = Path("data/raw/melee/standard/2025-07-19_Boa Qualifier #2 2025 (standard).json")
    
    if not boa_path.exists():
        logger.error(f"❌ Fichier non trouvé: {boa_path}")
        return
    
    tournament = load_tournament(boa_path)
    
    # Analyser la distribution
    logger.info("\n📊 Distribution des archétypes:")
    distribution = calculate_archetype_distribution(tournament)
    total = sum(distribution.values())
    
    for archetype, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        logger.info(f"  {archetype:30s}: {count:2d} ({percentage:5.1f}%)")
    
    logger.info("")
    
    # Analyser les matchups possibles
    matches = analyze_swiss_pairings(tournament)
    
    # Résumé
    logger.info(f"\n📈 Résumé:")
    logger.info(f"  - Matches reconstruits: {len(matches)}")
    logger.info(f"  - Archétypes uniques: {len(distribution)}")
    logger.info(f"  - Total de joueurs: {total}")
    
    # Limites
    logger.info("\n⚠️  Limites de cette approche:")
    logger.info("  1. On ne peut reconstruire que le dernier round avec certitude")
    logger.info("  2. Les rounds précédents nécessiteraient les standings round par round")
    logger.info("  3. C'est pourquoi l'API Round Standings est CRUCIALE")
    logger.info("\n💡 Solution: Utiliser --get-rounds dans scrape_melee_flexible.py")


if __name__ == "__main__":
    main()