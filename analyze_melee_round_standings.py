#!/usr/bin/env python3
"""
Analyser comment extraire les matchs depuis les Round Standings Melee
"""

import json
from pathlib import Path
import logging
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_matches_from_round(round_data: Dict, round_num: int) -> List[Dict]:
    """Extraire les matchs d'un round en utilisant la logique Swiss"""
    standings = round_data['standings']
    matches = []
    
    if round_num == 1:
        # Round 1 : Pairings aléatoires, mais on peut déduire des standings
        # Les gagnants (1-0) ont battu les perdants (0-1)
        winners = [p for p in standings if p['MatchRecord'] == '1-0-0']
        losers = [p for p in standings if p['MatchRecord'] == '0-1-0']
        
        # Dans Swiss, généralement on apparie 1 vs N/2+1, 2 vs N/2+2, etc.
        # Mais on ne peut pas être sûr sans les pairings exacts
        logger.info(f"  Round {round_num}: {len(winners)} gagnants, {len(losers)} perdants")
        
    else:
        # Rounds suivants : Les joueurs avec le même record s'affrontent
        # Grouper par record
        by_record = {}
        for player in standings:
            record = player['MatchRecord']
            if record not in by_record:
                by_record[record] = []
            by_record[record].append(player)
        
        logger.info(f"  Round {round_num} - Groupes par record:")
        for record, players in sorted(by_record.items(), reverse=True):
            logger.info(f"    {record}: {len(players)} joueurs")
            
            # Dans chaque groupe, on peut déduire certains matchs
            # Mais sans les pairings exacts, c'est de la spéculation
    
    return matches


def analyze_tournament_for_matches(filepath: Path):
    """Analyser un tournoi pour voir ce qu'on peut extraire"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tournament_name = data.get('TournamentName', 'Unknown')
    total_players = len(data.get('Decks', []))
    
    logger.info(f"\n🏆 {tournament_name}")
    logger.info(f"   {total_players} joueurs")
    
    # 1. Ce qu'on peut calculer SANS les matchs exacts
    logger.info("\n✅ Ce qu'on PEUT faire avec ces données :")
    
    # Distribution des archétypes
    archetypes = {}
    for deck in data.get('Decks', []):
        archetype = deck.get('DeckName', 'Unknown')
        archetypes[archetype] = archetypes.get(archetype, 0) + 1
    
    logger.info("   📊 Meta Share (distribution des archétypes):")
    for arch, count in sorted(archetypes.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / total_players * 100) if total_players > 0 else 0
        logger.info(f"      - {arch}: {count} ({percentage:.1f}%)")
    
    # Performance par archétype
    logger.info("\n   🏅 Performance par archétype (basé sur le classement final):")
    top8_archetypes = {}
    for deck in data.get('Decks', []):
        if deck.get('Rank', 999) <= 8:
            arch = deck.get('DeckName', 'Unknown')
            top8_archetypes[arch] = top8_archetypes.get(arch, 0) + 1
    
    for arch, count in sorted(top8_archetypes.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"      - {arch}: {count} dans le Top 8")
    
    # 2. Ce qu'on POURRAIT faire avec les Round Standings
    logger.info("\n❓ Ce qu'on POURRAIT faire avec les Round Standings :")
    
    if 'RoundStandings' in data:
        rounds = data['RoundStandings']
        logger.info(f"   {len(rounds)} rounds disponibles")
        
        # Analyser chaque round
        for round_data in rounds[:2]:  # Juste les 2 premiers pour l'exemple
            extract_matches_from_round(round_data, round_data['round'])
        
        # Estimation du nombre de matchs
        total_rounds = len(rounds)
        estimated_matches = (total_players // 2) * total_rounds
        logger.info(f"\n   📈 Estimation: ~{estimated_matches} matchs dans ce tournoi")
        
        logger.info("\n   💡 MAIS : Sans les pairings exacts, on ne peut que spéculer")
        logger.info("      - On sait QUI a gagné/perdu")
        logger.info("      - On ne sait PAS qui a joué contre qui (sauf déduction)")
    
    else:
        logger.info("   ❌ Pas de Round Standings dans ce fichier")


def main():
    """Analyser tous les tournois Melee"""
    melee_dir = Path("data/raw/melee/standard")
    json_files = list(melee_dir.glob("*.json"))
    
    logger.info("🎯 Analyse des possibilités avec les données Melee")
    logger.info("=" * 60)
    
    # Analyser un tournoi en détail
    if json_files:
        # Prendre le tournoi Boa comme exemple
        boa_file = [f for f in json_files if "Boa" in f.name]
        if boa_file:
            analyze_tournament_for_matches(boa_file[0])
        else:
            analyze_tournament_for_matches(json_files[0])
    
    # Résumé global
    logger.info("\n" + "=" * 60)
    logger.info("📊 RÉSUMÉ : Que faire avec les données Melee ?")
    logger.info("=" * 60)
    
    logger.info("\n1️⃣ UTILISATION IMMÉDIATE (sans reconstruction):")
    logger.info("   ✅ Meta Share : % de chaque archétype")
    logger.info("   ✅ Performance : Quel archétype finit dans le Top 8")
    logger.info("   ✅ Tendances : Évolution du méta dans le temps")
    
    logger.info("\n2️⃣ UTILISATION AVANCÉE (avec reconstruction Swiss):")
    logger.info("   🔄 Reconstruire ~70% des matchs par déduction")
    logger.info("   ⚠️  Mais avec incertitude sur les pairings exacts")
    
    logger.info("\n3️⃣ RECOMMENDATION:")
    logger.info("   → Utiliser Melee pour le META SHARE")
    logger.info("   → Utiliser MTGO pour les MATCHUPS (données exactes)")
    logger.info("   → Combiner les deux pour une vue complète!")


if __name__ == "__main__":
    main()