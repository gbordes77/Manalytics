"""
Advanced tournament and matchup analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)

class TournamentAnalyzer:
    """Advanced analytics for tournament data."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_archetype_performance(self, format_name: str, archetype_name: str, days: int) -> Dict[str, Any]:
        """Get comprehensive performance metrics for an archetype."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = """
            WITH archetype_stats AS (
                SELECT 
                    d.id,
                    d.wins,
                    d.losses,
                    d.position,
                    t.players_count,
                    t.date,
                    CASE 
                        WHEN d.position <= 8 THEN 1 
                        ELSE 0 
                    END as top_8
                FROM manalytics.decklists d
                JOIN manalytics.archetypes a ON d.archetype_id = a.id
                JOIN manalytics.tournaments t ON d.tournament_id = t.id
                JOIN manalytics.formats f ON t.format_id = f.id
                WHERE f.name = %(format)s 
                    AND a.name = %(archetype)s
                    AND t.date BETWEEN %(start_date)s AND %(end_date)s
            )
            SELECT 
                COUNT(*) as total_entries,
                SUM(top_8) as top_8_count,
                AVG(COALESCE(wins, 0)) as avg_wins,
                AVG(COALESCE(losses, 0)) as avg_losses,
                COUNT(DISTINCT date) as tournament_days
            FROM archetype_stats;
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, {
                'format': format_name,
                'archetype': archetype_name,
                'start_date': start_date,
                'end_date': end_date
            })
            
            result = cursor.fetchone()
            if not result or result[0] == 0:
                return None
            
            total_entries = result[0]
            top_8_count = result[1] or 0
            avg_wins = float(result[2] or 0)
            avg_losses = float(result[3] or 0)
            tournament_days = result[4]
            
            # Calculate win rate if we have match data
            total_matches = avg_wins + avg_losses
            win_rate = (avg_wins / total_matches * 100) if total_matches > 0 else None
            
            return {
                "total_entries": total_entries,
                "top_8_appearances": top_8_count,
                "top_8_conversion": round(top_8_count / total_entries * 100, 2) if total_entries > 0 else 0,
                "avg_wins": round(avg_wins, 2),
                "avg_losses": round(avg_losses, 2),
                "win_rate": round(win_rate, 2) if win_rate else None,
                "tournaments_present": tournament_days,
                "entries_per_tournament": round(total_entries / tournament_days, 2) if tournament_days > 0 else 0
            }
    
    def get_archetype_decklists(self, format_name: str, archetype_name: str, 
                               limit: int, days: int, min_wins: Optional[int]) -> List[Dict]:
        """Get recent successful decklists for an archetype."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        query = """
            SELECT 
                d.id,
                p.name as player,
                t.name as tournament,
                t.date,
                d.wins,
                d.losses,
                d.mainboard,
                d.sideboard,
                t.url
            FROM manalytics.decklists d
            JOIN manalytics.players p ON d.player_id = p.id
            JOIN manalytics.archetypes a ON d.archetype_id = a.id
            JOIN manalytics.tournaments t ON d.tournament_id = t.id
            JOIN manalytics.formats f ON t.format_id = f.id
            WHERE f.name = %(format)s 
                AND a.name = %(archetype)s
                AND t.date BETWEEN %(start_date)s AND %(end_date)s
                {wins_filter}
            ORDER BY t.date DESC, COALESCE(d.wins, 0) DESC
            LIMIT %(limit)s;
        """
        
        wins_filter = "AND d.wins >= %(min_wins)s" if min_wins is not None else ""
        query = query.format(wins_filter=wins_filter)
        
        params = {
            'format': format_name,
            'archetype': archetype_name,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        }
        
        if min_wins is not None:
            params['min_wins'] = min_wins
        
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            
            decklists = []
            for row in cursor.fetchall():
                record = f"{row[4]}-{row[5]}" if row[4] is not None and row[5] is not None else "N/A"
                
                decklists.append({
                    "id": str(row[0]),
                    "player": row[1],
                    "tournament": row[2],
                    "date": row[3].isoformat(),
                    "record": record,
                    "mainboard": row[6],
                    "sideboard": row[7],
                    "tournament_url": row[8]
                })
            
            return decklists
    
    def get_archetype_card_stats(self, format_name: str, archetype_name: str, 
                                days: int, card_type: str) -> List[Dict]:
        """Analyze card frequency in an archetype."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # First get all decklists
        query = """
            SELECT d.mainboard, d.sideboard
            FROM manalytics.decklists d
            JOIN manalytics.archetypes a ON d.archetype_id = a.id
            JOIN manalytics.tournaments t ON d.tournament_id = t.id
            JOIN manalytics.formats f ON t.format_id = f.id
            WHERE f.name = %(format)s 
                AND a.name = %(archetype)s
                AND t.date BETWEEN %(start_date)s AND %(end_date)s;
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, {
                'format': format_name,
                'archetype': archetype_name,
                'start_date': start_date,
                'end_date': end_date
            })
            
            card_counts = defaultdict(lambda: {'count': 0, 'total_quantity': 0, 'lists': 0})
            total_lists = 0
            
            for row in cursor.fetchall():
                total_lists += 1
                
                if card_type in ['all', 'mainboard'] and row[0]:
                    for card in row[0]:
                        name = card['name']
                        quantity = card['quantity']
                        card_counts[name]['lists'] += 1
                        card_counts[name]['total_quantity'] += quantity
                
                if card_type in ['all', 'sideboard'] and row[1]:
                    for card in row[1]:
                        name = card['name']
                        quantity = card['quantity']
                        card_counts[name]['lists'] += 1
                        card_counts[name]['total_quantity'] += quantity
            
            # Calculate statistics
            card_stats = []
            for card_name, stats in card_counts.items():
                avg_quantity = stats['total_quantity'] / stats['lists']
                presence_rate = (stats['lists'] / total_lists * 100) if total_lists > 0 else 0
                
                card_stats.append({
                    'card_name': card_name,
                    'presence_rate': round(presence_rate, 1),
                    'avg_quantity': round(avg_quantity, 2),
                    'total_copies': stats['total_quantity'],
                    'lists_with_card': stats['lists']
                })
            
            # Sort by presence rate
            card_stats.sort(key=lambda x: x['presence_rate'], reverse=True)
            
            return card_stats[:50]  # Top 50 cards
    
    def calculate_matchup_matrix(self, format_name: str, days: int, min_matches: int) -> Dict:
        """
        Calculate matchup win rates using tournament standings analysis.
        This infers matchups from tournament results.
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get all tournament results
        query = """
            SELECT 
                t.id as tournament_id,
                a.name as archetype,
                d.wins,
                d.losses,
                d.position
            FROM manalytics.decklists d
            JOIN manalytics.archetypes a ON d.archetype_id = a.id
            JOIN manalytics.tournaments t ON d.tournament_id = t.id
            JOIN manalytics.formats f ON t.format_id = f.id
            WHERE f.name = %(format)s 
                AND t.date BETWEEN %(start_date)s AND %(end_date)s
                AND d.wins IS NOT NULL 
                AND d.losses IS NOT NULL
            ORDER BY t.id, d.position;
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, {
                'format': format_name,
                'start_date': start_date,
                'end_date': end_date
            })
            
            # Group by tournament
            tournaments = defaultdict(list)
            for row in cursor.fetchall():
                tournaments[row[0]].append({
                    'archetype': row[1],
                    'wins': row[2],
                    'losses': row[3],
                    'position': row[4]
                })
            
            # Infer matchups using statistical analysis
            matchup_data = defaultdict(lambda: {'wins': 0, 'losses': 0})
            
            for tournament_id, results in tournaments.items():
                # For each pair of decks in the tournament
                for i, deck1 in enumerate(results):
                    for deck2 in results[i+1:]:
                        # Use performance differential to infer likely matchup results
                        # This is a simplified model - could be enhanced
                        perf1 = deck1['wins'] / (deck1['wins'] + deck1['losses']) if (deck1['wins'] + deck1['losses']) > 0 else 0.5
                        perf2 = deck2['wins'] / (deck2['wins'] + deck2['losses']) if (deck2['wins'] + deck2['losses']) > 0 else 0.5
                        
                        # Estimate likelihood they played based on Swiss pairing principles
                        if abs(deck1['wins'] - deck2['wins']) <= 1:
                            # Likely paired at some point
                            key = tuple(sorted([deck1['archetype'], deck2['archetype']]))
                            
                            # Infer winner based on final performance
                            if perf1 > perf2:
                                if deck1['archetype'] == key[0]:
                                    matchup_data[key]['wins'] += 1
                                else:
                                    matchup_data[key]['losses'] += 1
                            else:
                                if deck2['archetype'] == key[0]:
                                    matchup_data[key]['wins'] += 1
                                else:
                                    matchup_data[key]['losses'] += 1
            
            # Convert to win rates
            matchup_matrix = {}
            for (arch1, arch2), data in matchup_data.items():
                total_matches = data['wins'] + data['losses']
                if total_matches >= min_matches:
                    win_rate = (data['wins'] / total_matches * 100) if total_matches > 0 else 50
                    
                    if arch1 not in matchup_matrix:
                        matchup_matrix[arch1] = {}
                    if arch2 not in matchup_matrix:
                        matchup_matrix[arch2] = {}
                    
                    matchup_matrix[arch1][arch2] = round(win_rate, 1)
                    matchup_matrix[arch2][arch1] = round(100 - win_rate, 1)
            
            return matchup_matrix
    
    def get_archetype_matchups(self, format_name: str, archetype_name: str, days: int) -> List[Dict]:
        """Get all matchup data for a specific archetype."""
        matchup_matrix = self.calculate_matchup_matrix(format_name, days, min_matches=10)
        
        if archetype_name not in matchup_matrix:
            return []
        
        matchups = []
        for opponent, win_rate in matchup_matrix[archetype_name].items():
            matchups.append({
                'opponent': opponent,
                'win_rate': win_rate,
                'classification': self._classify_matchup(win_rate)
            })
        
        # Sort by win rate
        matchups.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return matchups
    
    def compare_archetypes(self, format_name: str, archetypes: List[str], days: int) -> Dict:
        """Compare multiple archetypes across various metrics."""
        comparison = {}
        
        for archetype in archetypes:
            perf = self.get_archetype_performance(format_name, archetype, days)
            if perf:
                comparison[archetype] = perf
        
        # Add relative comparisons
        if len(comparison) >= 2:
            # Find best/worst for each metric
            metrics = ['top_8_conversion', 'win_rate', 'total_entries']
            
            for metric in metrics:
                values = [(arch, data.get(metric, 0)) for arch, data in comparison.items() if data.get(metric) is not None]
                if values:
                    values.sort(key=lambda x: x[1], reverse=True)
                    
                    # Mark best and worst
                    if len(values) >= 1:
                        comparison[values[0][0]][f'{metric}_rank'] = 'best'
                    if len(values) >= 2:
                        comparison[values[-1][0]][f'{metric}_rank'] = 'worst'
        
        return comparison
    
    def get_tournament_details(self, tournament_id: str) -> Dict:
        """Get detailed results for a specific tournament."""
        query = """
            SELECT 
                t.name,
                t.date,
                t.players_count,
                f.name as format,
                s.name as source,
                t.url,
                a.name as archetype,
                p.name as player,
                d.wins,
                d.losses,
                d.position
            FROM manalytics.tournaments t
            JOIN manalytics.formats f ON t.format_id = f.id
            JOIN manalytics.sources s ON t.source_id = s.id
            LEFT JOIN manalytics.decklists d ON d.tournament_id = t.id
            LEFT JOIN manalytics.archetypes a ON d.archetype_id = a.id
            LEFT JOIN manalytics.players p ON d.player_id = p.id
            WHERE t.id = %(tournament_id)s
            ORDER BY d.position, d.wins DESC;
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, {'tournament_id': tournament_id})
            
            rows = cursor.fetchall()
            if not rows:
                return None
            
            # Tournament info from first row
            tournament_info = {
                'id': tournament_id,
                'name': rows[0][0],
                'date': rows[0][1].isoformat(),
                'players_count': rows[0][2],
                'format': rows[0][3],
                'source': rows[0][4],
                'url': rows[0][5],
                'results': []
            }
            
            # Add results
            for row in rows:
                if row[6]:  # If archetype exists
                    tournament_info['results'].append({
                        'position': row[10],
                        'player': row[7],
                        'archetype': row[6],
                        'record': f"{row[8]}-{row[9]}" if row[8] is not None else "N/A"
                    })
            
            # Add archetype breakdown
            archetype_counts = defaultdict(int)
            for result in tournament_info['results']:
                archetype_counts[result['archetype']] += 1
            
            tournament_info['archetype_breakdown'] = [
                {
                    'archetype': arch,
                    'count': count,
                    'percentage': round(count / len(tournament_info['results']) * 100, 1)
                }
                for arch, count in archetype_counts.items()
            ]
            tournament_info['archetype_breakdown'].sort(key=lambda x: x['count'], reverse=True)
            
            return tournament_info
    
    def get_meta_trends(self, format_name: str, days: int, interval: str) -> List[Dict]:
        """Calculate meta trends over time."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Determine grouping based on interval
        if interval == 'daily':
            date_trunc = 't.date'
            interval_days = 1
        else:  # weekly
            date_trunc = "DATE_TRUNC('week', t.date)::date"
            interval_days = 7
        
        query = f"""
            SELECT 
                {date_trunc} as period,
                a.name as archetype,
                COUNT(d.id)::int as deck_count
            FROM manalytics.decklists d
            JOIN manalytics.archetypes a ON d.archetype_id = a.id
            JOIN manalytics.tournaments t ON d.tournament_id = t.id
            JOIN manalytics.formats f ON t.format_id = f.id
            WHERE f.name = %(format)s 
                AND t.date BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY period, a.name
            ORDER BY period, deck_count DESC;
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, {
                'format': format_name,
                'start_date': start_date,
                'end_date': end_date
            })
            
            # Organize by period
            periods = defaultdict(list)
            for row in cursor.fetchall():
                period = row[0]
                periods[period].append({
                    'archetype': row[1],
                    'count': row[2]
                })
            
            # Calculate percentages and format for output
            trends = []
            for period, archetypes in sorted(periods.items()):
                total = sum(a['count'] for a in archetypes)
                
                period_data = {
                    'period': period.isoformat(),
                    'total_decks': total,
                    'archetypes': []
                }
                
                for arch in archetypes[:10]:  # Top 10 per period
                    period_data['archetypes'].append({
                        'name': arch['archetype'],
                        'count': arch['count'],
                        'percentage': round(arch['count'] / total * 100, 2) if total > 0 else 0
                    })
                
                trends.append(period_data)
            
            return trends
    
    @staticmethod
    def _classify_matchup(win_rate: float) -> str:
        """Classify a matchup based on win rate."""
        if win_rate >= 60:
            return "Heavily Favored"
        elif win_rate >= 55:
            return "Favored"
        elif win_rate >= 45:
            return "Even"
        elif win_rate >= 40:
            return "Unfavored"
        else:
            return "Heavily Unfavored"