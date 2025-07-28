"""
Matchup Enricher - Enriches listener match data with archetype information.

This module takes raw match data from the listener and enriches it with:
- Archetype detection for decks
- Player deck details from tournament data
- Match context (round, tournament type, etc.)
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

from ...parsers.archetype_parser import ArchetypeParser
from ...cache.reader import CacheReader

logger = logging.getLogger(__name__)


class MatchupEnricher:
    """Enriches match data with archetype and deck information"""
    
    def __init__(self):
        """Initialize the enricher with necessary components"""
        self.archetype_parser = ArchetypeParser()
        self.cache_reader = CacheReader()
        
    def enrich_match(self, match_data: Dict, tournament_data: Dict) -> Dict:
        """
        Enrich a single match with archetype and deck information.
        
        Args:
            match_data: Raw match data from listener
            tournament_data: Tournament data with decklists
            
        Returns:
            Enriched match data
        """
        enriched = match_data.copy()
        
        # Get tournament decklists
        decklists = tournament_data.get('data', {}).get('Decklists', [])
        
        # Try to match players to decklists
        for player_key in ['player1', 'player2']:
            player = enriched.get(player_key, {})
            player_name = player.get('name')
            
            if player_name:
                # Find player's decklist in tournament
                player_deck = self._find_player_deck(player_name, decklists)
                
                if player_deck:
                    # Detect archetype if not already present
                    if not player.get('archetype'):
                        archetype = self.archetype_parser.detect_archetype(
                            player_deck.get('Mainboard', []),
                            player_deck.get('Sideboard', [])
                        )
                        player['archetype'] = archetype.get('archetype', 'Unknown')
                        player['colors'] = archetype.get('colors', [])
                    
                    # Add deck details
                    player['deck_details'] = {
                        'mainboard_count': len(player_deck.get('Mainboard', [])),
                        'sideboard_count': len(player_deck.get('Sideboard', [])),
                        'key_cards': self._get_key_cards(player_deck)
                    }
        
        # Add tournament context
        enriched['tournament_context'] = {
            'name': tournament_data.get('data', {}).get('Name', 'Unknown'),
            'format': tournament_data.get('format', 'standard'),
            'platform': tournament_data.get('platform', 'unknown'),
            'total_players': len(decklists)
        }
        
        return enriched
    
    def _find_player_deck(self, player_name: str, decklists: List[Dict]) -> Optional[Dict]:
        """Find a player's decklist by name"""
        for deck in decklists:
            if deck.get('Player') == player_name:
                return deck
        return None
    
    def _get_key_cards(self, deck: Dict) -> List[str]:
        """Extract key cards from a decklist"""
        key_cards = []
        
        # Get non-land cards with 3+ copies
        for card in deck.get('Mainboard', []):
            if card.get('Count', 0) >= 3 and 'Land' not in card.get('Types', []):
                key_cards.append(card.get('Name'))
        
        return key_cards[:5]  # Top 5 key cards
    
    def enrich_all_matches(self, tournament_matches: Dict[int, Dict]) -> Dict[int, Dict]:
        """
        Enrich all matches for multiple tournaments.
        
        Args:
            tournament_matches: Dictionary of tournament_id -> tournament data with matches
            
        Returns:
            Enriched tournament data
        """
        enriched_tournaments = {}
        
        for tournament_id, tournament_data in tournament_matches.items():
            enriched_tournament = tournament_data.copy()
            enriched_matches = []
            
            for match in tournament_data.get('matches', []):
                enriched_match = self.enrich_match(match, tournament_data)
                enriched_matches.append(enriched_match)
            
            enriched_tournament['matches'] = enriched_matches
            enriched_tournaments[tournament_id] = enriched_tournament
            
            logger.info(f"Enriched {len(enriched_matches)} matches for tournament {tournament_id}")
        
        return enriched_tournaments
    
    def validate_archetypes(self, enriched_data: Dict[int, Dict]) -> Dict:
        """
        Validate and standardize archetype names across all matches.
        
        Returns statistics about archetype detection.
        """
        stats = {
            'total_matches': 0,
            'archetypes_detected': 0,
            'unknown_archetypes': 0,
            'archetype_distribution': {}
        }
        
        for tournament_data in enriched_data.values():
            for match in tournament_data.get('matches', []):
                stats['total_matches'] += 1
                
                for player_key in ['player1', 'player2']:
                    player = match.get(player_key, {})
                    archetype = player.get('archetype', 'Unknown')
                    
                    if archetype != 'Unknown':
                        stats['archetypes_detected'] += 1
                    else:
                        stats['unknown_archetypes'] += 1
                    
                    # Track distribution
                    if archetype not in stats['archetype_distribution']:
                        stats['archetype_distribution'][archetype] = 0
                    stats['archetype_distribution'][archetype] += 1
        
        # Calculate percentages
        total_players = stats['archetypes_detected'] + stats['unknown_archetypes']
        if total_players > 0:
            stats['detection_rate'] = (stats['archetypes_detected'] / total_players) * 100
        else:
            stats['detection_rate'] = 0
        
        logger.info(f"Archetype detection rate: {stats['detection_rate']:.1f}%")
        return stats