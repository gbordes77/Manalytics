#!/usr/bin/env python3
"""
Create visualization using MTGOData with EXACT template from archetype_charts.py
This is the correct script that generates the reference visualization.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

# Add project root
sys.path.append(str(Path(__file__).parent))

from src.manalytics.listener.listener_reader import ListenerReader
from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_standard_analysis_visualization():
    """Create interactive visualization with Plotly - EXACT SAME AS archetype_charts.py but with MTGOData"""
    
    print("📡 Using MTGOData instead of cache...")
    
    # Initialize readers
    listener_reader = ListenerReader()
    cache_reader = CacheReader()
    db = CacheDatabase()
    
    # Get MTGOData for July 1-21
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 21)
    
    print(f"\n📡 Loading MTGOData from {start_date.date()} to {end_date.date()}...")
    listener_tournaments = listener_reader.get_tournaments_for_period(start_date, end_date, "standard")
    
    # Get cache tournaments for merging
    cache_tournaments = db.get_tournaments_by_format("standard", start_date, end_date)
    cache_tournaments = [t for t in cache_tournaments if 'league' not in t.type.lower() and 'league' not in (t.name or '').lower()]
    
    # Merge data
    merged_data = merge_listener_and_cache(listener_reader, listener_tournaments, cache_tournaments)
    
    # Calculate meta by MATCHES (Jiliac methodology)
    meta_data = calculate_meta_by_matches(merged_data)
    
    # Calculate temporal data for timeline
    temporal_data = calculate_temporal_data_from_matches(merged_data['all_matches'])
    
    # Prepare data - EXACT SAME FORMAT as archetype_charts.py
    archetypes = {}
    for item in meta_data['meta_breakdown']:
        archetypes[item['archetype']] = {'count': item['decks']}
    
    total_decks = meta_data['total_decks']
    
    # Extract counts and prepare data
    archetype_data = []
    for arch, data in archetypes.items():
        count = data['count'] if isinstance(data, dict) else data
        percentage = (count / total_decks * 100) if total_decks > 0 else 0
        clean_name = format_archetype_name(arch) if arch else "Unknown"
        archetype_data.append({
            'archetype': clean_name,
            'count': count,
            'percentage': round(percentage, 2),
            'per_tournament': round(count / meta_data['total_tournaments'], 1) if meta_data['total_tournaments'] else 0
        })
    
    # Sort by count
    archetype_data.sort(key=lambda x: x['count'], reverse=True)
    
    # Create DataFrame
    df = pd.DataFrame(archetype_data)
    
    # Color mapping for MTG guilds - EXACT SAME as archetype_charts.py
    color_map = {
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
        'Domain': '#9370DB'
    }
    
    # Assign colors
    df['color'] = df['archetype'].apply(lambda x: get_archetype_color(x, color_map))
    
    # Create subplots - EXACT SAME LAYOUT
    fig = make_subplots(
        rows=3, cols=2,
        row_heights=[0.35, 0.35, 0.3],
        column_widths=[0.5, 0.5],
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
        vertical_spacing=0.08,
        horizontal_spacing=0.1
    )
    
    # 1. Interactive Pie Chart
    top_10 = df.head(10)
    others = df.iloc[10:].sum()
    if others['count'] > 0:
        pie_data = pd.concat([
            top_10,
            pd.DataFrame([{
                'archetype': 'Others',
                'count': others['count'],
                'percentage': others['percentage'],
                'color': '#808080'
            }])
        ])
    else:
        pie_data = top_10
    
    fig.add_trace(
        go.Pie(
            labels=pie_data['archetype'],
            values=pie_data['count'],
            text=[f"{row['archetype']}<br>{row['percentage']}%" for _, row in pie_data.iterrows()],
            hovertemplate='<b>%{label}</b><br>' +
                          'Decks: %{value}<br>' +
                          'Meta Share: %{percent}<br>' +
                          '<extra></extra>',
            marker_colors=pie_data['color'] if 'color' in pie_data else None,
            textposition='auto',
            textinfo='text'
        ),
        row=1, col=1
    )
    
    # 2. Bar Chart
    fig.add_trace(
        go.Bar(
            x=top_10['archetype'],
            y=top_10['count'],
            text=[f"{c} ({p}%)" for c, p in zip(top_10['count'], top_10['percentage'])],
            textposition='outside',
            marker_color=top_10['color'],
            hovertemplate='<b>%{x}</b><br>' +
                          'Decks: %{y}<br>' +
                          'Per Tournament: %{customdata}<br>' +
                          '<extra></extra>',
            customdata=top_10['per_tournament']
        ),
        row=1, col=2
    )
    
    # 3. Timeline Chart
    timeline_df = prepare_timeline_data(temporal_data, top_archetypes=df.head(5)['archetype'].tolist())
    
    for archetype in timeline_df['archetype'].unique():
        arch_data = timeline_df[timeline_df['archetype'] == archetype]
        color = next((c for a, c in color_map.items() if archetype.startswith(a)), '#708090')
        
        fig.add_trace(
            go.Scatter(
                x=arch_data['date'],
                y=arch_data['percentage'],
                name=archetype,
                mode='lines+markers',
                line=dict(width=3, color=color),
                marker=dict(size=8),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x}<br>' +
                              'Meta Share: %{y:.1f}%<br>' +
                              '<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 4. Detailed Table
    table_data = []
    for i, row in df.iterrows():
        trend = calculate_trend(row['archetype'], temporal_data)
        table_data.append([
            f"#{i+1}",
            row['archetype'],
            row['count'],
            f"{row['percentage']}%",
            f"{row['per_tournament']:.1f}",
            trend
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
                values=list(zip(*table_data)),
                fill_color=['#f0f0f0', 'white'],
                align=['center', 'left', 'center', 'center', 'center', 'center'],
                height=30,
                font=dict(size=12)
            )
        ),
        row=3, col=1
    )
    
    # Update layout - EXACT SAME
    fig.update_layout(
        title={
            'text': f"🎯 Manalytics - Interactive Standard Metagame Analysis<br>" +
                    f"<sub>MTGOData Analysis (Leagues Excluded) - {datetime.now().strftime('%B %d, %Y')}</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=True,
        height=1400,
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor='white',
        paper_bgcolor='#f5f7fa'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
    fig.update_xaxes(tickangle=-45, row=1, col=2)
    
    # Add statistics annotations
    stats_text = f"""
    <b>📊 Summary Statistics</b><br>
    Total Tournaments: {meta_data['total_tournaments']}<br>
    Total Decks: {total_decks}<br>
    Total Matches: {meta_data['total_matches']}<br>
    Unique Archetypes: {len(df)}<br>
    Top Archetype: {df.iloc[0]['archetype'] if len(df) > 0 else 'N/A'} ({df.iloc[0]['percentage'] if len(df) > 0 else 0}%)
    """
    
    fig.add_annotation(
        text=stats_text,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=12),
        align="left",
        bordercolor="#667eea",
        borderwidth=2,
        borderpad=10,
        bgcolor="white",
        opacity=0.95
    )
    
    # Save HTML with config for downloads
    config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'manalytics_mtgodata_{datetime.now().strftime("%Y%m%d")}',
            'height': 1400,
            'width': 1600,
            'scale': 2
        },
        'displaylogo': False,
        'modeBarButtonsToAdd': ['downloadSvg'],
        'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
    }
    
    # Generate HTML - EXACT SAME TEMPLATE
    html = fig.to_html(
        config=config,
        include_plotlyjs='cdn',
        div_id="plotly-div"
    )
    
    # Add custom CSS and mobile responsive design - EXACT SAME
    custom_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Manalytics - Interactive Standard Metagame Analysis</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .controls {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .btn {{
                padding: 10px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: transform 0.2s;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            #plotly-div {{
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                padding: 20px;
            }}
            
            /* Mobile responsive */
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                .header h1 {{
                    font-size: 1.5em;
                }}
                #plotly-div {{
                    padding: 10px;
                }}
            }}
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
            {html.split('<body>')[1].split('</body>')[0]}
        </div>
        
        <script>
            // CSV download function
            function downloadCSV() {{
                const data = {json.dumps([{
                    'Archetype': row['archetype'],
                    'Decks': row['count'],
                    'Percentage': row['percentage'],
                    'Per_Tournament': row['per_tournament']
                } for _, row in df.iterrows()])};
                
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
            
            // Reset filters
            function resetFilters() {{
                Plotly.restyle('plotly-div', {{}});
            }}
            
            // Make charts interactive
            document.getElementById('plotly-div').on('plotly_click', function(data) {{
                // Filter logic here
                console.log('Clicked:', data);
            }});
        </script>
    </body>
    </html>
    """
    
    # Save file
    output_file = Path("data/cache/mtgodata_exact_reference_template.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(custom_html)
    
    print(f"✅ Interactive Plotly visualization created: {output_file}")
    print(f"📊 Using EXACT template from archetype_charts.py")
    print(f"🌐 Open: file://{output_file.absolute()}")
    
    return output_file


def merge_listener_and_cache(listener_reader, listener_tournaments: Dict, cache_tournaments: List) -> Dict:
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


def calculate_meta_by_matches(merged_data: Dict) -> Dict:
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


def calculate_temporal_data_from_matches(all_matches: List[Dict]) -> Dict:
    """Calculate archetype distribution over time from matches"""
    temporal_data = defaultdict(lambda: defaultdict(int))
    
    for match in all_matches:
        date = match['date'].strftime('%Y-%m-%d')
        temporal_data[date][match['arch1']] += 1
        temporal_data[date][match['arch2']] += 1
    
    return dict(temporal_data)


def prepare_timeline_data(temporal_data, top_archetypes):
    """Prepare data for timeline visualization"""
    timeline_records = []
    
    # Get last 30 days
    dates = sorted(temporal_data.keys())
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_dates = [d for d in dates if d >= cutoff]
    
    for date in recent_dates:
        day_data = temporal_data[date]
        total = sum(day_data.values())
        
        if total > 0:
            for archetype in top_archetypes:
                # Clean archetype name
                clean_arch = format_archetype_name(archetype) if archetype else "Unknown"
                count = sum(v for k, v in day_data.items() if format_archetype_name(k) == clean_arch)
                percentage = (count / total * 100) if total > 0 else 0
                
                timeline_records.append({
                    'date': date,
                    'archetype': clean_arch,
                    'count': count,
                    'percentage': percentage
                })
    
    return pd.DataFrame(timeline_records)


def calculate_trend(archetype, temporal_data):
    """Calculate trend for an archetype"""
    dates = sorted(temporal_data.keys())
    if len(dates) < 14:
        return "➡️ Stable"
    
    # Last week vs previous week
    recent = dates[-7:]
    previous = dates[-14:-7]
    
    recent_count = sum(temporal_data[d].get(archetype, 0) for d in recent)
    previous_count = sum(temporal_data[d].get(archetype, 0) for d in previous)
    
    if recent_count > previous_count * 1.2:
        return "📈 Rising"
    elif recent_count < previous_count * 0.8:
        return "📉 Falling"
    else:
        return "➡️ Stable"


def get_archetype_color(archetype, color_map):
    """Get color for archetype"""
    for key, color in color_map.items():
        if archetype.startswith(key):
            return color
    return '#708090'  # Default gray


if __name__ == "__main__":
    create_standard_analysis_visualization()