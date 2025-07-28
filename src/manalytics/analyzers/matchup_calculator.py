"""
Matchup Calculator - Calculates win rates between archetypes.

This module aggregates match results by archetype to calculate:
- Win rates for each archetype matchup
- Confidence intervals using Wilson score
- Sample sizes for reliability
"""

import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class MatchupCalculator:
    """Calculates matchup statistics between archetypes"""
    
    def __init__(self):
        """Initialize the calculator"""
        self.matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        
    def add_match_result(self, archetype1: str, archetype2: str, winner: int):
        """
        Add a match result to the data.
        
        Args:
            archetype1: Player 1's archetype
            archetype2: Player 2's archetype
            winner: 1 if player 1 won, 2 if player 2 won
        """
        if winner == 1:
            self.matchup_data[archetype1][archetype2]['wins'] += 1
            self.matchup_data[archetype2][archetype1]['losses'] += 1
        elif winner == 2:
            self.matchup_data[archetype1][archetype2]['losses'] += 1
            self.matchup_data[archetype2][archetype1]['wins'] += 1
            
    def process_matches(self, enriched_tournaments: Dict[int, Dict]):
        """
        Process all matches from enriched tournament data.
        
        Args:
            enriched_tournaments: Dictionary of tournament data with enriched matches
        """
        total_matches = 0
        
        for tournament_data in enriched_tournaments.values():
            for match in tournament_data.get('matches', []):
                player1 = match.get('player1', {})
                player2 = match.get('player2', {})
                result = match.get('result', {})
                
                archetype1 = player1.get('archetype', 'Unknown')
                archetype2 = player2.get('archetype', 'Unknown')
                winner = result.get('winner')
                
                # Skip if missing data
                if archetype1 == 'Unknown' or archetype2 == 'Unknown' or not winner:
                    continue
                
                # Convert winner string to number
                if winner == 'player1':
                    winner_num = 1
                elif winner == 'player2':
                    winner_num = 2
                else:
                    continue
                
                self.add_match_result(archetype1, archetype2, winner_num)
                total_matches += 1
        
        logger.info(f"Processed {total_matches} matches for matchup calculations")
        
    def calculate_win_rate(self, wins: int, total: int) -> Tuple[float, float, float]:
        """
        Calculate win rate with Wilson score confidence interval.
        
        Args:
            wins: Number of wins
            total: Total matches
            
        Returns:
            Tuple of (win_rate, lower_bound, upper_bound)
        """
        if total == 0:
            return 0.0, 0.0, 0.0
            
        # Calculate point estimate
        p_hat = wins / total
        
        # Wilson score interval (95% confidence)
        z = 1.96  # 95% confidence
        
        denominator = 1 + z**2 / total
        centre = (p_hat + z**2 / (2 * total)) / denominator
        margin = z * math.sqrt((p_hat * (1 - p_hat) / total + z**2 / (4 * total**2))) / denominator
        
        lower = max(0, centre - margin)
        upper = min(1, centre + margin)
        
        return p_hat, lower, upper
        
    def get_matchup_matrix(self) -> Dict[str, Dict[str, Dict]]:
        """
        Get the complete matchup matrix with statistics.
        
        Returns:
            Dictionary of archetype -> archetype -> stats
        """
        matrix = {}
        
        for archetype1, opponents in self.matchup_data.items():
            matrix[archetype1] = {}
            
            for archetype2, results in opponents.items():
                wins = results['wins']
                losses = results['losses']
                total = wins + losses
                
                if total > 0:
                    win_rate, lower, upper = self.calculate_win_rate(wins, total)
                    
                    matrix[archetype1][archetype2] = {
                        'win_rate': round(win_rate * 100, 1),
                        'confidence_lower': round(lower * 100, 1),
                        'confidence_upper': round(upper * 100, 1),
                        'matches': total,
                        'wins': wins,
                        'losses': losses
                    }
        
        return matrix
        
    def get_archetype_performance(self) -> Dict[str, Dict]:
        """
        Calculate overall performance for each archetype.
        
        Returns:
            Dictionary of archetype -> overall stats
        """
        performance = {}
        
        for archetype, opponents in self.matchup_data.items():
            total_wins = 0
            total_losses = 0
            
            for results in opponents.values():
                total_wins += results['wins']
                total_losses += results['losses']
            
            total_matches = total_wins + total_losses
            
            if total_matches > 0:
                win_rate, lower, upper = self.calculate_win_rate(total_wins, total_matches)
                
                performance[archetype] = {
                    'overall_win_rate': round(win_rate * 100, 1),
                    'confidence_lower': round(lower * 100, 1),
                    'confidence_upper': round(upper * 100, 1),
                    'total_matches': total_matches,
                    'total_wins': total_wins,
                    'total_losses': total_losses
                }
        
        # Sort by win rate
        performance = dict(sorted(
            performance.items(),
            key=lambda x: x[1]['overall_win_rate'],
            reverse=True
        ))
        
        return performance
        
    def get_significant_matchups(self, min_matches: int = 10) -> List[Dict]:
        """
        Get matchups with significant sample sizes.
        
        Args:
            min_matches: Minimum number of matches to be considered significant
            
        Returns:
            List of significant matchups with statistics
        """
        significant = []
        
        for archetype1, opponents in self.matchup_data.items():
            for archetype2, results in opponents.items():
                # Avoid duplicates (only include A vs B, not B vs A)
                if archetype1 >= archetype2:
                    continue
                    
                total = results['wins'] + results['losses']
                
                if total >= min_matches:
                    win_rate1, lower1, upper1 = self.calculate_win_rate(
                        results['wins'], total
                    )
                    
                    # Get reverse matchup
                    reverse_results = self.matchup_data[archetype2][archetype1]
                    win_rate2, lower2, upper2 = self.calculate_win_rate(
                        reverse_results['wins'], total
                    )
                    
                    significant.append({
                        'matchup': f"{archetype1} vs {archetype2}",
                        'archetype1': archetype1,
                        'archetype2': archetype2,
                        'archetype1_win_rate': round(win_rate1 * 100, 1),
                        'archetype2_win_rate': round(win_rate2 * 100, 1),
                        'matches': total,
                        'confidence_overlap': lower1 <= upper2 and lower2 <= upper1
                    })
        
        # Sort by number of matches
        significant.sort(key=lambda x: x['matches'], reverse=True)
        
        return significant
        
    def get_summary_stats(self) -> Dict:
        """Get summary statistics about the matchup data"""
        total_matchups = 0
        total_matches = 0
        archetypes = set()
        
        for archetype1, opponents in self.matchup_data.items():
            archetypes.add(archetype1)
            for archetype2, results in opponents.items():
                archetypes.add(archetype2)
                if archetype1 < archetype2:  # Count each matchup once
                    total_matchups += 1
                    total_matches += results['wins'] + results['losses']
        
        return {
            'total_archetypes': len(archetypes),
            'total_unique_matchups': total_matchups,
            'total_matches': total_matches,
            'average_matches_per_matchup': round(total_matches / total_matchups, 1) if total_matchups > 0 else 0
        }