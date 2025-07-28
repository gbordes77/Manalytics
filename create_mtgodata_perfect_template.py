#!/usr/bin/env python3
"""
Create PERFECT visualization using MTGOData with EXACT reference template.
This combines the modern dashboard style with MTGOData.
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.manalytics.listener.listener_reader import ListenerReader
from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PerfectDashboardCreator:
    """Creates dashboard with EXACT reference template"""
    
    def __init__(self):
        self.listener_reader = ListenerReader()
        self.cache_reader = CacheReader()
        self.db = CacheDatabase()
        
        # MTG color mappings - from archetype_charts.py
        self.color_map = {
            'Izzet': '#C41E3A',
            'Dimir': '#0F1B3C', 
            'Golgari': '#7C9A2E',
            'Boros': '#FFD700',
            'Azorius': '#0080FF',
            'Gruul': '#FF6B35',
            'Mono White': '#FFFDD0',
            'Mono Red': '#DC143C',
            'Mono Green': '#228B22',
            'Mono Blue': '#4169E1',
            'Mono Black': '#2F4F4F',
            'Naya': '#FFA500',
            'Domain': '#9370DB',
            'Esper': '#0080FF',
            'Jeskai': '#C41E3A',
            'Sultai': '#0F1B3C',
            'Mardu': '#FFD700',
            'Temur': '#0080FF'
        }
    
    def create_perfect_dashboard(self, start_date: datetime, end_date: datetime):
        """Create dashboard with exact reference template"""
        print(f"🎨 Creating PERFECT dashboard: {start_date.date()} to {end_date.date()}")
        
        # Load and merge data
        print("\n📡 Loading MTGOData...")
        listener_tournaments = self.listener_reader.get_tournaments_for_period(
            start_date, end_date, "standard"
        )
        
        print("\n📋 Loading cache data...")
        cache_tournaments = self.db.get_tournaments_by_format("standard", start_date, end_date)
        cache_tournaments = [t for t in cache_tournaments 
                           if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower()]
        
        print("\n🔄 Merging data...")
        merged_data = self._merge_listener_and_cache(listener_tournaments, cache_tournaments)
        
        print("\n📈 Calculating meta by MATCHES...")
        meta_data = self._calculate_meta_by_matches(merged_data)
        
        # Calculate daily timeline
        timeline_data = self._calculate_timeline(merged_data['all_matches'])
        
        print("\n🎨 Creating PERFECT visualization...")
        html = self._create_perfect_html(meta_data, timeline_data)
        
        output_path = Path('data/cache/mtgodata_perfect_template.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Saved to: {output_path}")
        print(f"🌐 Open: file://{output_path.absolute()}")
        
        return output_path
    
    def _merge_listener_and_cache(self, listener_tournaments: Dict, cache_tournaments: List) -> Dict:
        """Merge listener match data with cache decklist data"""
        matched_tournaments = {}
        all_matches = []
        tournament_count = 0
        total_decks = set()
        
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
        
        # Match and collect all matches
        for listener_id, listener_data in listener_tournaments.items():
            for cache_id, cached_tournament in cache_data.items():
                if str(listener_id) in str(cache_id) or str(cache_id) in str(listener_id):
                    tournament_count += 1
                    
                    # Create player -> archetype mapping
                    player_archetypes = {}
                    
                    for deck in cached_tournament.get('decklists', []):
                        player = deck.get('player')
                        archetype = deck.get('archetype') or 'Unknown'
                        if player and archetype != 'Unknown':
                            player_archetypes[player] = archetype
                            total_decks.add(f"{listener_id}_{player}")
                    
                    # Collect all matches
                    for round_data in listener_data['rounds']:
                        for match in round_data.get('Matches', []):
                            if match['Player2'] == 'BYE' or not match['Result'] or match['Result'] == '0-0-0':
                                continue
                            
                            player1 = match['Player1']
                            player2 = match['Player2']
                            
                            if player1 in player_archetypes and player2 in player_archetypes:
                                all_matches.append({
                                    'tournament_id': listener_id,
                                    'tournament_name': listener_data['name'],
                                    'date': listener_data['date'],
                                    'player1': player1,
                                    'player2': player2,
                                    'arch1': player_archetypes[player1],
                                    'arch2': player_archetypes[player2],
                                    'result': match['Result']
                                })
                    
                    matched_tournaments[listener_id] = {
                        'listener_data': listener_data,
                        'cache_data': cached_tournament,
                        'player_archetypes': player_archetypes
                    }
                    break
        
        print(f"  - Matched {tournament_count} tournaments")
        print(f"  - Found {len(all_matches)} valid matches")
        print(f"  - Total unique decks: {len(total_decks)}")
        
        return {
            'matched_tournaments': matched_tournaments,
            'all_matches': all_matches,
            'tournament_count': tournament_count,
            'total_decks': len(total_decks)
        }
    
    def _calculate_meta_by_matches(self, merged_data: Dict) -> Dict:
        """Calculate meta percentages by MATCHES"""
        archetype_matches = defaultdict(int)
        archetype_decks = defaultdict(set)
        
        # Count matches per archetype
        for match in merged_data['all_matches']:
            archetype_matches[match['arch1']] += 1
            archetype_matches[match['arch2']] += 1
            
            # Track unique decks
            archetype_decks[match['arch1']].add(f"{match['tournament_id']}_{match['player1']}")
            archetype_decks[match['arch2']].add(f"{match['tournament_id']}_{match['player2']}")
        
        # Calculate percentages
        total_match_count = sum(archetype_matches.values())
        
        meta_data = []
        for archetype, match_count in archetype_matches.items():
            percentage = (match_count / total_match_count * 100) if total_match_count > 0 else 0
            deck_count = len(archetype_decks[archetype])
            
            meta_data.append({
                'archetype': archetype,
                'matches': match_count,
                'percentage': percentage,
                'decks': deck_count,
                'per_tournament': deck_count / merged_data['tournament_count'] if merged_data['tournament_count'] > 0 else 0
            })
        
        # Sort by percentage
        meta_data.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Get unique archetypes count (> 1.5%)
        archetypes_above_threshold = len([a for a in meta_data if a['percentage'] > 1.5])
        
        return {
            'meta_breakdown': meta_data,
            'total_tournaments': merged_data['tournament_count'],
            'total_decks': merged_data['total_decks'],
            'total_matches': len(merged_data['all_matches']),
            'archetypes_above_threshold': archetypes_above_threshold,
            'top_archetype': meta_data[0]['archetype'] if meta_data else 'Unknown'
        }
    
    def _calculate_timeline(self, all_matches: List[Dict]) -> Dict:
        """Calculate timeline data for visualization"""
        daily_data = defaultdict(lambda: defaultdict(lambda: {'matches': 0}))
        
        # Group matches by date and archetype
        for match in all_matches:
            date = match['date'].strftime('%Y-%m-%d')
            daily_data[match['arch1']][date]['matches'] += 1
            daily_data[match['arch2']][date]['matches'] += 1
        
        # Calculate percentages
        timeline_data = defaultdict(dict)
        
        for archetype, dates in daily_data.items():
            for date, data in dates.items():
                # Get total matches for this date
                total_date_matches = sum(
                    daily_data[arch][date]['matches'] 
                    for arch in daily_data
                ) / 2  # Divide by 2 since each match is counted twice
                
                if total_date_matches > 0:
                    percentage = (data['matches'] / (total_date_matches * 2)) * 100
                    timeline_data[archetype][date] = percentage
        
        return timeline_data
    
    def _get_archetype_color(self, archetype: str) -> str:
        """Get color for archetype"""
        for key, color in self.color_map.items():
            if key.lower() in archetype.lower():
                return color
        return '#808080'
    
    def _create_perfect_html(self, meta_data: Dict, timeline_data: Dict) -> str:
        """Create HTML with EXACT reference template"""
        # Get date range
        start_date = datetime(2025, 7, 1).strftime('%Y-%m-%d')
        end_date = datetime(2025, 7, 21).strftime('%Y-%m-%d')
        
        # Prepare data for charts
        meta_breakdown = meta_data['meta_breakdown'][:10]  # Top 10
        
        # Create main figure
        mainFig = self._create_main_figure(meta_breakdown, timeline_data)
        
        # Create table figure
        tableFig = self._create_table_figure(meta_data['meta_breakdown'])
        
        # HTML template - EXACT COPY of reference
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Interactive Metagame Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .controls {{
            margin-top: 20px;
        }}
        .controls button {{
            padding: 10px 20px;
            margin: 0 10px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .controls button:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-box {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            border: 2px solid transparent;
        }}
        .stat-box:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-color: #667eea;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #mainChart, #tableChart {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics - Interactive Metagame Analysis</h1>
        <p>Hover for details • Export to PNG/SVG • MTG Color Gradients Preserved</p>
        
        <div class="controls">
            <button onclick="downloadCSV()">📊 Download CSV</button>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{meta_data['total_tournaments']}</div>
                <div class="stat-label">Total Tournaments</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{meta_data['total_decks']}</div>
                <div class="stat-label">Total Decks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{meta_data['archetypes_above_threshold']}</div>
                <div class="stat-label">Archetypes > 1.5%</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="font-size: 1.5em;">{meta_data['top_archetype']}</div>
                <div class="stat-label">Top Archetype</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Standard</div>
                <div class="stat-label">Format</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="font-size: 1.2em;">{start_date} to {end_date}</div>
                <div class="stat-label">Date Range</div>
            </div>
        </div>
        
        <div id="mainChart"></div>
        <div id="tableChart"></div>
    </div>
    
    <script>
        var mainFig = {json.dumps(mainFig)};
        var tableFig = {json.dumps(tableFig)};
        
        // Configuration
        var config = {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'toggleSpikelines'],
            displaylogo: false
        }};
        
        Plotly.newPlot('mainChart', mainFig.data, mainFig.layout, config);
        Plotly.newPlot('tableChart', tableFig.data, tableFig.layout, config);
        
        function downloadCSV() {{
            const data = {json.dumps([{
                'Archetype': item['archetype'],
                'Decks': item['decks'],
                'Percentage': round(item['percentage'], 2),
                'Per_Tournament': round(item['per_tournament'], 1)
            } for item in meta_breakdown])};
            
            const csv = [
                Object.keys(data[0]).join(','),
                ...data.map(row => Object.values(row).join(','))
            ].join('\\n');
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manalytics_mtgodata_{datetime.now().strftime("%Y%m%d")}.csv';
            a.click();
        }}
    </script>
</body>
</html>
"""
        
        return html_template
    
    def _create_main_figure(self, meta_breakdown: List[Dict], timeline_data: Dict) -> Dict:
        """Create main figure with pie, bar and timeline"""
        # Create figure
        fig = make_subplots(
            rows=2, cols=2,
            row_heights=[0.6, 0.4],
            column_widths=[0.4, 0.6],
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter", "colspan": 2}, None]
            ],
            subplot_titles=(
                "📊 Meta Distribution",
                "📈 Top Archetypes", 
                "📉 Meta Evolution Timeline (Last 30 Days)"
            ),
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Colors
        colors = [self._get_archetype_color(item['archetype']) for item in meta_breakdown]
        
        # 1. Pie Chart
        fig.add_trace(
            go.Pie(
                labels=[item['archetype'] for item in meta_breakdown],
                values=[item['decks'] for item in meta_breakdown],
                text=[f"{item['percentage']:.2f}%" for item in meta_breakdown],
                textinfo='label+text',
                textposition='outside',
                marker=dict(colors=colors, line=dict(color='white', width=2)),
                customdata=[[item['percentage']] for item in meta_breakdown],
                hovertemplate='<b>%{label}</b><br>Decks: %{value}<br>Meta Share: %{customdata[0]:.2f}%<br><extra></extra>',
                hole=0
            ),
            row=1, col=1
        )
        
        # 2. Bar Chart
        fig.add_trace(
            go.Bar(
                x=[item['archetype'] for item in meta_breakdown],
                y=[item['decks'] for item in meta_breakdown],
                text=[f"{item['decks']} ({item['percentage']:.2f}%)" for item in meta_breakdown],
                textposition='outside',
                marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.2)', width=1)),
                hovertemplate='<b>%{x}</b><br>Decks: %{y}<br>Meta Share: %{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Timeline - Top 5 archetypes
        top_5 = meta_breakdown[:5]
        for item in top_5:
            archetype = item['archetype']
            if archetype in timeline_data:
                dates = sorted(timeline_data[archetype].keys())
                percentages = [timeline_data[archetype][date] for date in dates]
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=percentages,
                        mode='lines+markers',
                        name=archetype,
                        line=dict(width=3, color=self._get_archetype_color(archetype)),
                        marker=dict(size=6, color=self._get_archetype_color(archetype)),
                        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Meta Share: %{y:.1f}%<br><extra></extra>'
                    ),
                    row=2, col=1
                )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f"🎯 Manalytics - Interactive Standard Metagame Analysis<br><sub>MTGOData Analysis (Leagues Excluded) - {datetime.now().strftime('%B %d, %Y')}</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=True,
            height=1100,
            hovermode='closest',
            margin=dict(t=140, b=80, l=80, r=120)
        )
        
        # Update axes
        fig.update_xaxes(tickangle=-45, showgrid=False, row=1, col=2)
        fig.update_yaxes(title_text="Number of Decks", row=1, col=2)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
        
        return fig.to_dict()
    
    def _create_table_figure(self, meta_breakdown: List[Dict]) -> Dict:
        """Create table figure"""
        # Prepare table data
        table_data = []
        colors = []
        
        for i, item in enumerate(meta_breakdown):
            table_data.append([
                f"#{i+1}",
                item['archetype'],
                item['decks'],
                f"{item['percentage']:.2f}%",
                round(item['per_tournament'], 1),
                "➡️ Stable"  # Simplified trend
            ])
            
            # Get color with transparency
            color = self._get_archetype_color(item['archetype'])
            if color.startswith('#'):
                # Convert hex to rgba
                hex_color = color.lstrip('#')
                r = int(hex_color[:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                colors.append(f"rgba({r}, {g}, {b}, 0.27)")
            else:
                colors.append(color)
        
        # Create table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Rank', 'Archetype', 'Decks', 'Meta %', 'Avg/Tournament', 'Trend'],
                fill=dict(color='rgba(102, 126, 234, 0.8)'),
                font=dict(color='white', size=14),
                align='left',
                height=40
            ),
            cells=dict(
                values=list(zip(*table_data)) if table_data else [[], [], [], [], [], []],
                fill=dict(color=[colors] * 6),
                align='left',
                font=dict(size=12),
                height=30
            )
        )])
        
        fig.update_layout(
            title={'text': '🏆 Complete Archetype Breakdown'},
            margin=dict(t=60, b=20, l=20, r=20),
            height=600
        )
        
        return fig.to_dict()


def main():
    """Main function"""
    creator = PerfectDashboardCreator()
    
    # Analyze July 1-21, 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21)
    
    creator.create_perfect_dashboard(start_date, end_date)


if __name__ == "__main__":
    main()