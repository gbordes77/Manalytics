#!/usr/bin/env python3
"""
Analyze MTGOData with advanced Plotly visualizations.

This script combines:
1. MTGOData listener data (matches)
2. Cache data (decklists with archetypes)
3. Advanced Plotly visualizations
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import math
from collections import defaultdict

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.manalytics.listener.listener_reader import ListenerReader
from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.manalytics.visualizers.metagame_dynamics import MetagameDynamicsVisualizer
from src.manalytics.visualizers.unified_dashboard import UnifiedDashboard
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class MTGODataAnalyzer:
    """Analyzes MTGOData with cache integration and Plotly visualizations"""
    
    def __init__(self):
        self.listener_reader = ListenerReader()
        self.cache_reader = CacheReader()
        self.db = CacheDatabase()
        self.viz = MetagameDynamicsVisualizer()
        
    def analyze_period(self, start_date: datetime, end_date: datetime):
        """Analyze a period with all visualizations"""
        print(f"📊 Analyzing period: {start_date.date()} to {end_date.date()}")
        
        # 1. Load listener data from MTGOData
        print("\n📡 Loading listener data from MTGOData...")
        listener_tournaments = self.listener_reader.get_tournaments_for_period(
            start_date, end_date, "standard"
        )
        print(f"✅ Loaded {len(listener_tournaments)} tournaments from MTGOData")
        
        # 2. Load cache data
        print("\n📋 Loading cache data...")
        cache_tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        cache_tournaments = [t for t in cache_tournaments 
                           if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower()]
        print(f"✅ Loaded {len(cache_tournaments)} tournaments from cache")
        
        # 3. Merge data
        print("\n🔄 Merging listener and cache data...")
        merged_data = self._merge_listener_and_cache(listener_tournaments, cache_tournaments)
        print(f"✅ Successfully merged {len(merged_data['matched_tournaments'])} tournaments")
        
        # 4. Calculate daily meta evolution
        print("\n📈 Calculating daily meta evolution...")
        daily_meta = self._calculate_daily_meta(merged_data)
        
        # 5. Create visualizations
        print("\n🎨 Creating advanced Plotly visualizations...")
        
        # Animated Sunburst
        print("  - Creating animated sunburst...")
        sunburst = self.viz.create_animated_sunburst(daily_meta)
        self.viz.save_visualization(sunburst, 'mtgodata_animated_sunburst.html')
        
        # Stream Graph
        print("  - Creating stream graph...")
        stream = self.viz.create_stream_graph(daily_meta)
        self.viz.save_visualization(stream, 'mtgodata_stream_graph.html')
        
        # Emergence Tracker
        print("  - Creating emergence tracker...")
        emergence = self.viz.create_emergence_tracker(daily_meta)
        self.viz.save_visualization(emergence, 'mtgodata_emergence_tracker.html')
        
        # Interactive Matchup Matrix
        print("  - Creating interactive matchup matrix...")
        matrix = self._create_interactive_matchup_matrix(merged_data)
        output_path = Path('data/cache/mtgodata_interactive_matrix.html')
        matrix.write_html(str(output_path))
        print(f"    Saved to: {output_path}")
        
        # Consensus Deck Builder
        print("  - Creating consensus deck builder...")
        consensus = self._create_consensus_deck_builder(merged_data)
        output_path = Path('data/cache/mtgodata_consensus_builder.html')
        consensus.write_html(str(output_path))
        print(f"    Saved to: {output_path}")
        
        print("\n✅ Analysis complete! Check the data/cache/ directory for visualizations.")
        
        return merged_data, daily_meta
    
    def _merge_listener_and_cache(self, listener_tournaments: Dict, cache_tournaments: List) -> Dict:
        """Merge listener match data with cache decklist data"""
        matched_tournaments = {}
        matchup_data = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))
        archetype_stats = defaultdict(lambda: {
            'matches': 0, 'wins': 0, 'losses': 0, 'decks': 0, 'tournaments': set()
        })
        
        total_matches = 0
        
        # Load cache decklists
        cache_data = {}
        for tournament in cache_tournaments:
            month_key = tournament.date.strftime("%Y-%m")
            decklists_file = Path(f"data/cache/decklists/{month_key}.json")
            
            if decklists_file.exists():
                with open(decklists_file, 'r') as f:
                    month_data = json.load(f)
                
                for key in month_data:
                    if (str(tournament.id) in key or 
                        tournament.name.lower() in key.lower() or
                        (hasattr(tournament, 'source_id') and str(tournament.source_id) in key)):
                        cache_data[tournament.id] = month_data[key]
                        break
        
        # Match and analyze
        for listener_id, listener_data in listener_tournaments.items():
            # Find matching cache data
            matched = False
            for cache_id, cached_tournament in cache_data.items():
                if str(listener_id) in str(cache_id) or str(cache_id) in str(listener_id):
                    matched = True
                    
                    # Create player -> archetype mapping
                    player_archetypes = {}
                    for deck in cached_tournament.get('decklists', []):
                        player = deck.get('player')
                        archetype = deck.get('archetype') or 'Unknown'
                        if player and archetype != 'Unknown':
                            player_archetypes[player] = archetype
                            archetype_stats[archetype]['decks'] += 1
                            archetype_stats[archetype]['tournaments'].add(listener_id)
                    
                    # Analyze matches
                    for round_data in listener_data['rounds']:
                        for match in round_data.get('Matches', []):
                            if match['Player2'] == 'BYE' or not match['Result'] or match['Result'] == '0-0-0':
                                continue
                            
                            player1 = match['Player1']
                            player2 = match['Player2']
                            
                            arch1 = player_archetypes.get(player1, 'Unknown')
                            arch2 = player_archetypes.get(player2, 'Unknown')
                            
                            if arch1 == 'Unknown' or arch2 == 'Unknown':
                                continue
                            
                            # Parse result
                            parts = match['Result'].split('-')
                            if len(parts) >= 2:
                                p1_wins = int(parts[0])
                                p2_wins = int(parts[1])
                                
                                total_matches += 1
                                
                                # Update stats
                                archetype_stats[arch1]['matches'] += 1
                                archetype_stats[arch2]['matches'] += 1
                                
                                if p1_wins > p2_wins:
                                    matchup_data[arch1][arch2]['wins'] += 1
                                    matchup_data[arch2][arch1]['losses'] += 1
                                    archetype_stats[arch1]['wins'] += 1
                                    archetype_stats[arch2]['losses'] += 1
                                else:
                                    matchup_data[arch1][arch2]['losses'] += 1
                                    matchup_data[arch2][arch1]['wins'] += 1
                                    archetype_stats[arch1]['losses'] += 1
                                    archetype_stats[arch2]['wins'] += 1
                    
                    matched_tournaments[listener_id] = {
                        'listener_data': listener_data,
                        'cache_data': cached_tournament,
                        'player_archetypes': player_archetypes
                    }
                    break
        
        return {
            'matched_tournaments': matched_tournaments,
            'matchup_data': dict(matchup_data),
            'archetype_stats': dict(archetype_stats),
            'total_matches': total_matches
        }
    
    def _calculate_daily_meta(self, merged_data: Dict) -> Dict[str, Dict]:
        """Calculate meta percentages for each day"""
        daily_meta = defaultdict(lambda: defaultdict(lambda: {
            'matches': 0, 'wins': 0, 'losses': 0, 'percentage': 0, 'win_rate': 50
        }))
        
        # Process each tournament
        for tid, tournament_data in merged_data['matched_tournaments'].items():
            date = tournament_data['listener_data']['date'].strftime('%Y-%m-%d')
            
            # Count matches by archetype for this tournament
            for round_data in tournament_data['listener_data']['rounds']:
                for match in round_data.get('Matches', []):
                    if match['Player2'] == 'BYE' or not match['Result'] or match['Result'] == '0-0-0':
                        continue
                    
                    player1 = match['Player1']
                    player2 = match['Player2']
                    
                    arch1 = tournament_data['player_archetypes'].get(player1, 'Unknown')
                    arch2 = tournament_data['player_archetypes'].get(player2, 'Unknown')
                    
                    if arch1 == 'Unknown' or arch2 == 'Unknown':
                        continue
                    
                    # Count matches
                    daily_meta[date][arch1]['matches'] += 1
                    daily_meta[date][arch2]['matches'] += 1
                    
                    # Parse result
                    parts = match['Result'].split('-')
                    if len(parts) >= 2:
                        p1_wins = int(parts[0])
                        p2_wins = int(parts[1])
                        
                        if p1_wins > p2_wins:
                            daily_meta[date][arch1]['wins'] += 1
                            daily_meta[date][arch2]['losses'] += 1
                        else:
                            daily_meta[date][arch1]['losses'] += 1
                            daily_meta[date][arch2]['wins'] += 1
        
        # Calculate percentages and win rates
        final_daily_meta = {}
        for date, archetypes in daily_meta.items():
            total_matches = sum(data['matches'] for data in archetypes.values()) / 2  # Divide by 2 since each match counts twice
            
            if total_matches > 0:
                final_daily_meta[date] = {}
                for archetype, data in archetypes.items():
                    percentage = (data['matches'] / (total_matches * 2)) * 100
                    win_rate = (data['wins'] / data['matches'] * 100) if data['matches'] > 0 else 50
                    
                    final_daily_meta[date][archetype] = {
                        'matches': data['matches'],
                        'wins': data['wins'],
                        'losses': data['losses'],
                        'percentage': percentage,
                        'win_rate': win_rate
                    }
        
        return final_daily_meta
    
    def _create_interactive_matchup_matrix(self, merged_data: Dict) -> go.Figure:
        """Create an interactive matchup matrix with advanced features"""
        matchup_data = merged_data['matchup_data']
        archetype_stats = merged_data['archetype_stats']
        
        # Get top archetypes by matches
        top_archetypes = sorted(
            [(arch, stats['matches']) for arch, stats in archetype_stats.items() if stats['matches'] >= 20],
            key=lambda x: x[1],
            reverse=True
        )[:15]
        
        archetype_names = [arch[0] for arch in top_archetypes]
        
        # Build matrix
        matrix = []
        hover_texts = []
        annotations = []
        
        for i, arch1 in enumerate(archetype_names):
            row = []
            hover_row = []
            
            for j, arch2 in enumerate(archetype_names):
                if arch1 == arch2:
                    row.append(50)
                    hover_row.append(f"<b>{arch1}</b><br>Mirror Match")
                else:
                    if arch1 in matchup_data and arch2 in matchup_data[arch1]:
                        wins = matchup_data[arch1][arch2]['wins']
                        losses = matchup_data[arch1][arch2]['losses']
                        total = wins + losses
                        
                        if total > 0:
                            win_rate = (wins / total) * 100
                            row.append(win_rate)
                            
                            # Confidence interval
                            p = wins / total
                            z = 1.96
                            margin = z * math.sqrt(p * (1 - p) / total)
                            ci_lower = max(0, (p - margin) * 100)
                            ci_upper = min(100, (p + margin) * 100)
                            
                            hover_row.append(
                                f"<b>{arch1} vs {arch2}</b><br>"
                                f"Win Rate: {win_rate:.1f}%<br>"
                                f"Record: {wins}-{losses}<br>"
                                f"CI: [{ci_lower:.1f}%, {ci_upper:.1f}%]<br>"
                                f"Sample Size: {total} matches"
                            )
                            
                            # Add annotation for extreme matchups
                            if total >= 10 and (win_rate <= 35 or win_rate >= 65):
                                annotations.append(dict(
                                    x=j, y=i,
                                    text=f"{win_rate:.0f}",
                                    showarrow=False,
                                    font=dict(color='white', size=12, weight='bold')
                                ))
                        else:
                            row.append(None)
                            hover_row.append(f"{arch1} vs {arch2}<br>No data")
                    else:
                        row.append(None)
                        hover_row.append(f"{arch1} vs {arch2}<br>No data")
            
            matrix.append(row)
            hover_texts.append(hover_row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=archetype_names,
            y=archetype_names,
            colorscale=[
                [0, '#8B0000'],      # Dark red (0%)
                [0.35, '#DC143C'],   # Crimson (35%)
                [0.45, '#FF6347'],   # Tomato (45%)
                [0.5, '#FFFAF0'],    # Floral white (50%)
                [0.55, '#90EE90'],   # Light green (55%)
                [0.65, '#32CD32'],   # Lime green (65%)
                [1, '#006400']       # Dark green (100%)
            ],
            hovertext=hover_texts,
            hovertemplate='%{hovertext}<extra></extra>',
            colorbar=dict(
                title='Win Rate %',
                tickmode='linear',
                tick0=0,
                dtick=10
            )
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🎲 Interactive Matchup Matrix - MTGOData Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 28}
            },
            xaxis=dict(title='Opponent', side='bottom', tickangle=-45),
            yaxis=dict(title='Your Deck', autorange='reversed'),
            width=1400,
            height=1200,
            annotations=annotations,
            plot_bgcolor='white'
        )
        
        return fig
    
    def _create_consensus_deck_builder(self, merged_data: Dict) -> go.Figure:
        """Create consensus deck visualization"""
        # Get top 3 archetypes
        archetype_stats = merged_data['archetype_stats']
        top_archetypes = sorted(
            [(arch, stats['matches']) for arch, stats in archetype_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=[f"{arch[0]}<br>({arch[1]} matches)" for arch in top_archetypes],
            horizontal_spacing=0.05
        )
        
        # For each archetype, analyze card frequencies
        for idx, (archetype, _) in enumerate(top_archetypes):
            card_counts = defaultdict(list)
            
            # Collect all decklists for this archetype
            for tournament_data in merged_data['matched_tournaments'].values():
                for deck in tournament_data['cache_data'].get('decklists', []):
                    if deck.get('archetype') == archetype:
                        # Count mainboard cards
                        for card_entry in deck.get('mainboard', []):
                            if isinstance(card_entry, dict):
                                card_name = card_entry.get('name', '')
                                count = card_entry.get('count', 0)
                            else:
                                # Parse string format "4 Lightning Bolt"
                                parts = card_entry.split(' ', 1)
                                if len(parts) == 2:
                                    count = int(parts[0])
                                    card_name = parts[1]
                                else:
                                    continue
                            
                            if card_name and count > 0:
                                card_counts[card_name].append(count)
            
            # Calculate consensus (average count per card)
            consensus_cards = []
            for card, counts in card_counts.items():
                avg_count = sum(counts) / len(counts)
                frequency = len(counts) / max(1, archetype_stats[archetype]['decks']) * 100
                
                if frequency > 50:  # Card appears in >50% of decks
                    consensus_cards.append({
                        'card': card,
                        'avg_count': avg_count,
                        'frequency': frequency
                    })
            
            # Sort by frequency
            consensus_cards.sort(key=lambda x: x['frequency'], reverse=True)
            top_cards = consensus_cards[:15]
            
            # Create bar chart
            if top_cards:
                fig.add_trace(
                    go.Bar(
                        x=[c['frequency'] for c in top_cards],
                        y=[c['card'] for c in top_cards],
                        orientation='h',
                        text=[f"{c['avg_count']:.1f}x" for c in top_cards],
                        textposition='auto',
                        marker_color=self.viz.color_map.get(archetype, '#808080'),
                        hovertemplate='<b>%{y}</b><br>Frequency: %{x:.1f}%<br>Avg Count: %{text}<extra></extra>'
                    ),
                    row=1, col=idx+1
                )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🃏 Consensus Deck Builder - Top 3 Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=False,
            height=600,
            width=1600
        )
        
        # Update axes
        for i in range(1, 4):
            fig.update_xaxes(title_text="Frequency %", range=[0, 100], row=1, col=i)
            fig.update_yaxes(autorange="reversed", row=1, col=i)
        
        return fig


def main():
    """Main analysis function"""
    analyzer = MTGODataAnalyzer()
    
    # Analyze July 1-21, 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21)
    
    analyzer.analyze_period(start_date, end_date)


if __name__ == "__main__":
    main()