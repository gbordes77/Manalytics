#!/usr/bin/env python3
"""
Analyze MTGOData with EXACT template from standard_analysis_no_leagues.html

This script creates the EXACT same layout and appearance with MTGOData.
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
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class MTGODataTemplateAnalyzer:
    """Creates EXACT template visualization with MTGOData"""
    
    def __init__(self):
        self.listener_reader = ListenerReader()
        self.cache_reader = CacheReader()
        self.db = CacheDatabase()
        
    def analyze_and_create_exact_template(self, start_date: datetime, end_date: datetime):
        """Create exact template visualization"""
        print(f"📊 Creating exact template analysis: {start_date.date()} to {end_date.date()}")
        
        # 1. Load and merge data
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
        
        # 2. Calculate meta by MATCHES (not decks)
        print("\n📈 Calculating meta by MATCHES...")
        meta_data = self._calculate_meta_by_matches(merged_data)
        
        # 3. Create EXACT template visualization
        print("\n🎨 Creating exact template visualization...")
        html = self._create_exact_template_html(meta_data, merged_data)
        
        # 4. Save
        output_path = Path('data/cache/mtgodata_exact_template.html')
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
            # Find matching cache data
            for cache_id, cached_tournament in cache_data.items():
                if str(listener_id) in str(cache_id) or str(cache_id) in str(listener_id):
                    tournament_count += 1
                    
                    # Create player -> archetype mapping
                    player_archetypes = {}
                    deck_count = 0
                    
                    for deck in cached_tournament.get('decklists', []):
                        player = deck.get('player')
                        archetype = deck.get('archetype') or 'Unknown'
                        if player and archetype != 'Unknown':
                            player_archetypes[player] = {
                                'archetype': archetype,
                                'deck': deck
                            }
                            deck_count += 1
                    
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
                                    'arch1': player_archetypes[player1]['archetype'],
                                    'arch2': player_archetypes[player2]['archetype'],
                                    'result': match['Result']
                                })
                    
                    matched_tournaments[listener_id] = {
                        'listener_data': listener_data,
                        'cache_data': cached_tournament,
                        'player_archetypes': player_archetypes,
                        'deck_count': deck_count
                    }
                    break
        
        print(f"  - Matched {tournament_count} tournaments")
        print(f"  - Found {len(all_matches)} valid matches")
        
        return {
            'matched_tournaments': matched_tournaments,
            'all_matches': all_matches,
            'tournament_count': tournament_count
        }
    
    def _calculate_meta_by_matches(self, merged_data: Dict) -> Dict:
        """Calculate meta percentages by MATCHES (not decks)"""
        archetype_matches = defaultdict(int)
        archetype_decks = defaultdict(set)  # Track unique players per archetype
        total_decks = 0
        
        # Count matches per archetype
        for match in merged_data['all_matches']:
            archetype_matches[match['arch1']] += 1
            archetype_matches[match['arch2']] += 1
            
            # Track unique player-tournament combinations
            archetype_decks[match['arch1']].add(f"{match['tournament_id']}_{match['player1']}")
            archetype_decks[match['arch2']].add(f"{match['tournament_id']}_{match['player2']}")
        
        # Calculate total matches (each match counts for 2)
        total_match_count = sum(archetype_matches.values())
        
        # Calculate total unique decks
        all_player_tournaments = set()
        for players in archetype_decks.values():
            all_player_tournaments.update(players)
        total_decks = len(all_player_tournaments)
        
        # Calculate percentages and prepare data
        meta_data = []
        for archetype, match_count in archetype_matches.items():
            percentage = (match_count / total_match_count * 100) if total_match_count > 0 else 0
            deck_count = len(archetype_decks[archetype])
            
            if percentage >= 1.0:  # Only show archetypes with at least 1%
                meta_data.append({
                    'archetype': archetype,
                    'matches': match_count,
                    'percentage': percentage,
                    'decks': deck_count,
                    'per_tournament': deck_count / merged_data['tournament_count'] if merged_data['tournament_count'] > 0 else 0
                })
        
        # Sort by percentage
        meta_data.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Calculate "Others"
        shown_percentage = sum(d['percentage'] for d in meta_data)
        if shown_percentage < 100:
            others_percentage = 100 - shown_percentage
            others_decks = total_decks - sum(d['decks'] for d in meta_data)
            meta_data.append({
                'archetype': 'Others',
                'matches': 0,
                'percentage': others_percentage,
                'decks': max(0, others_decks),
                'per_tournament': 0
            })
        
        print(f"  - Total matches analyzed: {len(merged_data['all_matches'])}")
        print(f"  - Total match instances: {total_match_count}")
        print(f"  - Unique decks: {total_decks}")
        print(f"  - Unique archetypes: {len(archetype_matches)}")
        
        return {
            'meta_breakdown': meta_data,
            'total_tournaments': merged_data['tournament_count'],
            'total_decks': total_decks,
            'total_matches': len(merged_data['all_matches']),
            'all_matches': merged_data['all_matches']
        }
    
    def _get_archetype_color(self, archetype: str) -> str:
        """Get color for archetype based on MTG colors"""
        colors = get_archetype_colors(archetype)
        
        if len(colors) == 1:
            return MTG_COLORS.get(colors[0], '#708090')
        elif len(colors) == 2:
            # Blend two colors
            c1 = MTG_COLORS.get(colors[0], '#708090')
            c2 = MTG_COLORS.get(colors[1], '#708090')
            # Simple blend - could be improved
            return f"#{hex(int((int(c1[1:3], 16) + int(c2[1:3], 16)) / 2))[2:].zfill(2)}" + \
                   f"{hex(int((int(c1[3:5], 16) + int(c2[3:5], 16)) / 2))[2:].zfill(2)}" + \
                   f"{hex(int((int(c1[5:7], 16) + int(c2[5:7], 16)) / 2))[2:].zfill(2)}"
        else:
            return '#708090'  # Default gray
    
    def _create_exact_template_html(self, meta_data: Dict, merged_data: Dict) -> str:
        """Create EXACT template HTML"""
        # Prepare data for visualization
        meta_breakdown = meta_data['meta_breakdown'][:10]  # Top 10 for pie
        
        # Colors for each archetype
        colors = []
        for item in meta_breakdown:
            if item['archetype'] == 'Others':
                colors.append('#808080')
            else:
                colors.append(self._get_archetype_color(item['archetype']))
        
        # Create figure with exact layout from template
        fig = make_subplots(
            rows=3, cols=2,
            row_heights=[0.35, 0.35, 0.3],
            column_widths=[0.45, 0.55],
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter", "colspan": 2}, None],
                [{"type": "table", "colspan": 2}, None]
            ],
            subplot_titles=(
                "📊 Meta Distribution (Click to Filter)",
                "📈 Top 10 Archetypes",
                "📉 Meta Evolution Timeline (Last 30 Days)",
                "🏆 Complete Archetype Breakdown"
            ),
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # 1. Pie Chart
        pie_labels = []
        pie_values = []
        pie_text = []
        for item in meta_breakdown:
            pie_labels.append(item['archetype'])
            pie_values.append(item['decks'])
            pie_text.append(f"{item['archetype']}<br>{item['percentage']:.2f}%")
        
        fig.add_trace(
            go.Pie(
                labels=pie_labels,
                values=pie_values,
                text=pie_text,
                textinfo='text',
                textposition='auto',
                marker=dict(colors=colors),
                hovertemplate='<b>%{label}</b><br>Decks: %{value}<br>Meta Share: %{percent}<br><extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. Bar Chart
        bar_data = [item for item in meta_data['meta_breakdown'] if item['archetype'] != 'Others'][:10]
        
        fig.add_trace(
            go.Bar(
                x=[item['archetype'] for item in bar_data],
                y=[item['decks'] for item in bar_data],
                text=[f"{item['decks']} ({item['percentage']:.2f}%)" for item in bar_data],
                textposition='outside',
                marker=dict(color=[self._get_archetype_color(item['archetype']) for item in bar_data]),
                customdata=[[item['per_tournament']] for item in bar_data],
                hovertemplate='<b>%{x}</b><br>Decks: %{y}<br>Per Tournament: %{customdata[0]:.1f}<br><extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Timeline (using daily aggregation)
        timeline_data = self._calculate_daily_timeline(meta_data['all_matches'])
        
        # Add top 5 archetypes to timeline
        top_5 = [item['archetype'] for item in bar_data[:5]]
        for archetype in top_5:
            if archetype in timeline_data:
                dates = sorted(timeline_data[archetype].keys())
                percentages = [timeline_data[archetype][date] for date in dates]
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=percentages,
                        mode='lines+markers',
                        name=archetype,
                        line=dict(width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Meta Share: %{y:.1f}%<br><extra></extra>'
                    ),
                    row=2, col=1
                )
        
        # 4. Table
        all_archetypes = meta_data['meta_breakdown']
        table_data = []
        for i, item in enumerate(all_archetypes[:20]):  # Top 20 in table
            table_data.append([
                f"#{i+1}",
                item['archetype'],
                item['decks'],
                f"{item['percentage']:.2f}%",
                f"{item['per_tournament']:.1f}",
                "➡️ Stable"  # Could calculate actual trend
            ])
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Rank', 'Archetype', 'Decks', 'Meta %', 'Avg/Tournament', 'Trend'],
                    fill_color='#667eea',
                    font=dict(color='white', size=14),
                    align='left',
                    height=35
                ),
                cells=dict(
                    values=list(zip(*table_data)) if table_data else [[], [], [], [], [], []],
                    fill_color=['#f0f0f0', 'white'],
                    align=['center', 'left', 'center', 'center', 'center', 'center'],
                    font=dict(size=12),
                    height=30
                )
            ),
            row=3, col=1
        )
        
        # Update layout to match template exactly
        fig.update_layout(
            title={
                'text': f"🎯 Manalytics - Interactive Standard Metagame Analysis<br><sub>Tournaments Only (Leagues Excluded) - {datetime.now().strftime('%B %d, %Y')}</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=True,
            height=1400,
            plot_bgcolor='white',
            paper_bgcolor='#f5f7fa',
            font=dict(family="Arial, sans-serif"),
            annotations=[
                dict(
                    text=f"""
    <b>📊 Summary Statistics</b><br>
    Total Tournaments: {meta_data['total_tournaments']}<br>
    Total Decks: {meta_data['total_decks']}<br>
    Unique Archetypes: {len([a for a in meta_data['meta_breakdown'] if a['archetype'] != 'Others'])}<br>
    Top Archetype: {meta_data['meta_breakdown'][0]['archetype']} ({meta_data['meta_breakdown'][0]['percentage']:.2f}%)
    """,
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    bgcolor="white",
                    bordercolor="#667eea",
                    borderwidth=2,
                    borderpad=10,
                    font=dict(size=12),
                    align="left",
                    opacity=0.95
                )
            ]
        )
        
        # Update axes
        fig.update_xaxes(tickangle=-45, row=1, col=2)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
        
        # Create HTML with exact template styling
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Interactive Standard Metagame Analysis</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        #plotly-div {
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            .header h1 {
                font-size: 1.5em;
            }
            #plotly-div {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Interactive Metagame Analysis</h1>
            <p>Click on charts to filter • Hover for details • Export to PNG/SVG</p>
            <div class="controls">
                <button class="btn" onclick="downloadCSV()">📊 Download CSV</button>
                <button class="btn" onclick="resetFilters()">🔄 Reset Filters</button>
            </div>
        </div>
        
        <div id="plotly-div" class="plotly-graph-div" style="height:1400px; width:100%;">
            {plotly_div}
        </div>
    </div>
    
    <script>
        // CSV download function
        function downloadCSV() {
            const data = {csv_data};
            
            const csv = [
                Object.keys(data[0]).join(','),
                ...data.map(row => Object.values(row).join(','))
            ].join('\\n');
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manalytics_meta_{date}.csv';
            a.click();
        }}
        
        // Reset filters function  
        function resetFilters() {{
            Plotly.Fx.reset('plotly-div');
        }}
    </script>
</body>
</html>
"""
        
        # Prepare CSV data
        csv_data = []
        for item in meta_data['meta_breakdown']:
            if item['archetype'] != 'Others':
                csv_data.append({
                    'Archetype': item['archetype'],
                    'Decks': item['decks'],
                    'Percentage': round(item['percentage'], 2),
                    'Per_Tournament': round(item['per_tournament'], 1)
                })
        
        # Generate final HTML
        plotly_html = fig.to_html(
            include_plotlyjs='cdn',
            div_id="plotly-div",
            config={
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'manalytics_meta_{datetime.now().strftime("%Y%m%d")}',
                    'height': 1400,
                    'width': 1600,
                    'scale': 2
                },
                'displaylogo': False,
                'modeBarButtonsToAdd': ['downloadSvg'],
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d', 
                                         'hoverClosestCartesian', 'hoverCompareCartesian'],
                'responsive': True
            }
        )
        
        # Extract just the div content
        import re
        match = re.search(r'<div>.*?</div>\s*</div>', plotly_html, re.DOTALL)
        if match:
            plotly_div = match.group(0)
        else:
            plotly_div = plotly_html
        
        html = html_template.format(
            plotly_div=plotly_div,
            csv_data=json.dumps(csv_data),
            date=datetime.now().strftime("%Y%m%d")
        )
        
        return html
    
    def _calculate_daily_timeline(self, all_matches: List[Dict]) -> Dict:
        """Calculate daily timeline data"""
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


def main():
    """Main function"""
    analyzer = MTGODataTemplateAnalyzer()
    
    # Analyze July 1-21, 2025
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21)
    
    analyzer.analyze_and_create_exact_template(start_date, end_date)


if __name__ == "__main__":
    main()