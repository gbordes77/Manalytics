#!/usr/bin/env python3
"""
Create PLOTLY HTML visualization of archetype distribution using MATCH-BASED analysis.
This version counts MATCHES (not decks) to align with community standards.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name
from src.utils.mtg_colors import get_pie_colors, create_bar_gradient_marker, get_archetype_colors, MTG_COLORS, blend_colors

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def calculate_match_based_data(tournaments):
    """Calculate archetype distribution based on MATCHES, not decks."""
    archetype_matches = defaultdict(int)
    archetype_decks = defaultdict(int)
    total_matches = 0
    total_decks = 0
    unknown_matches = 0
    
    # Load decklists from cache
    monthly_file = Path("data/cache/decklists/2025-07.json")
    with open(monthly_file, 'r') as f:
        all_decklists = json.load(f)
    
    for tournament in tournaments:
        if tournament.id in all_decklists:
            decklists = all_decklists[tournament.id].get('decklists', [])
            for deck in decklists:
                archetype = deck.get('archetype')
                wins = deck.get('wins', 0) or 0
                losses = deck.get('losses', 0) or 0
                matches = wins + losses
                
                # Skip Unknown archetypes
                if not archetype:
                    continue
                    
                total_decks += 1
                
                if matches > 0:
                    archetype_matches[archetype] += matches
                    archetype_decks[archetype] += 1
                    total_matches += matches
    
    return {
        'archetype_matches': dict(archetype_matches),
        'archetype_decks': dict(archetype_decks),
        'total_matches': total_matches,
        'total_decks': total_decks,
        'unknown_matches': unknown_matches
    }


def calculate_temporal_data(tournaments):
    """Calculate day-by-day evolution for the last 30 days."""
    # Load decklists from cache
    monthly_file = Path("data/cache/decklists/2025-07.json")
    with open(monthly_file, 'r') as f:
        all_decklists = json.load(f)
    
    # Group by date
    daily_data = defaultdict(lambda: defaultdict(int))
    daily_totals = defaultdict(int)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for tournament in tournaments:
        # Parse date
        if hasattr(tournament.date, 'strftime'):
            t_date = tournament.date
        else:
            t_date = datetime.strptime(tournament.date, '%Y-%m-%d')
        
        # Only include last 30 days
        if t_date < start_date:
            continue
            
        date_str = t_date.strftime('%Y-%m-%d')
        
        if tournament.id in all_decklists:
            decklists = all_decklists[tournament.id].get('decklists', [])
            for deck in decklists:
                archetype = deck.get('archetype')
                wins = deck.get('wins', 0) or 0
                losses = deck.get('losses', 0) or 0
                matches = wins + losses
                
                # Skip Unknown archetypes
                if not archetype:
                    continue
                    
                if matches > 0:
                    daily_data[date_str][archetype] += matches
                    daily_totals[date_str] += matches
    
    return daily_data, daily_totals


def create_plotly_visualization():
    """Create interactive HTML visualization with Plotly using MATCH-BASED analysis"""
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    # Filter out leagues
    tournaments = [t for t in tournaments if 'league' not in t.type.lower()]
    
    # Calculate match-based data
    match_data = calculate_match_based_data(tournaments)
    archetype_matches = match_data['archetype_matches']
    archetype_decks = match_data['archetype_decks']
    total_matches = match_data['total_matches']
    total_decks = match_data['total_decks']
    
    # Calculate temporal data for timeline
    temporal_data, daily_totals = calculate_temporal_data(tournaments)
    
    # Sort archetypes by matches
    sorted_archetypes = sorted(archetype_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Filter archetypes above 1.5% threshold (based on matches)
    min_threshold = total_matches * 0.015  # 1.5%
    filtered_archetypes = [(arch, matches) for arch, matches in sorted_archetypes if matches >= min_threshold]
    
    # Prepare chart data
    labels = []
    values = []
    percentages = []
    deck_counts = []
    avg_matches_per_deck = []
    
    # Calculate data for each archetype
    for archetype, matches in filtered_archetypes:
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(matches)
        percentage = round((matches / total_matches) * 100, 2)
        percentages.append(percentage)
        
        # Additional stats
        decks = archetype_decks.get(archetype, 0)
        deck_counts.append(decks)
        avg_matches = round(matches / decks, 1) if decks > 0 else 0
        avg_matches_per_deck.append(avg_matches)
    
    # Get MTG-based colors for pie chart
    colors = []
    for label in labels:
        arch_colors = get_archetype_colors(label)
        if arch_colors:
            colors.append(MTG_COLORS[arch_colors[0]])
        else:
            colors.append("#808080")  # Gray fallback
    
    # Calculate date range
    if tournaments:
        dates = [t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d') for t in tournaments]
        date_range = f"{min(dates)} to {max(dates)}"
    else:
        date_range = "No data"
    
    # Create subplots with better spacing
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        specs=[[{"type": "domain"}, {"type": "bar"}],
               [{"type": "scatter", "colspan": 2}, None]],
        subplot_titles=("📊 Meta Distribution (by Matches)", 
                       "📈 Top Archetypes (Match-Based)",
                       "📉 Meta Evolution Timeline (Last 30 Days)"),
        vertical_spacing=0.25,
        horizontal_spacing=0.20
    )
    
    # 1. Pie Chart - with match counts
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0,
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            textposition='outside',
            textinfo='label+text',
            text=[f'{p}%' for p in percentages],
            customdata=list(zip(deck_counts, avg_matches_per_deck)),
            hovertemplate='<b>%{label}</b><br>' +
                         'Matches: %{value}<br>' +
                         'Meta Share: ' + '%{text}<br>' +
                         'Decks: %{customdata[0]}<br>' +
                         'Avg Matches/Deck: %{customdata[1]}<br>' +
                         '<extra></extra>',
            insidetextorientation='radial'
        ),
        row=1, col=1
    )
    
    # 2. Bar Chart with gradient colors
    bar_colors = []
    for label in labels[:10]:  # Top 10 for bar chart
        arch_colors = get_archetype_colors(label)
        if arch_colors:
            bar_colors.append(MTG_COLORS[arch_colors[0]])
        else:
            bar_colors.append('#808080')
    
    fig.add_trace(
        go.Bar(
            x=labels[:10],
            y=percentages[:10],
            text=[f'{p}%<br>{v} matches<br>{d} decks' for p, v, d in zip(percentages[:10], values[:10], deck_counts[:10])],
            textposition='outside',
            marker=dict(
                color=bar_colors,
                line=dict(color='white', width=1)
            ),
            customdata=list(zip(values[:10], deck_counts[:10], avg_matches_per_deck[:10])),
            hovertemplate='<b>%{x}</b><br>' +
                         'Meta Share: %{y}%<br>' +
                         'Matches: %{customdata[0]}<br>' +
                         'Decks: %{customdata[1]}<br>' +
                         'Avg Matches/Deck: %{customdata[2]}<br>' +
                         '<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Timeline Chart - show top 5 archetypes evolution
    timeline_archetypes = [arch for arch, _ in filtered_archetypes[:5]]
    
    for archetype in timeline_archetypes:
        dates = []
        percentages_timeline = []
        
        # Sort dates
        sorted_dates = sorted(temporal_data.keys())
        
        for date in sorted_dates:
            if date in daily_totals and daily_totals[date] > 0:
                dates.append(date)
                matches = temporal_data[date].get(archetype, 0)
                percentage = (matches / daily_totals[date]) * 100
                percentages_timeline.append(round(percentage, 2))
        
        if dates:  # Only add trace if we have data
            clean_name = format_archetype_name(archetype)
            arch_colors = get_archetype_colors(clean_name)
            color = MTG_COLORS[arch_colors[0]] if arch_colors else '#808080'
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=percentages_timeline,
                    mode='lines+markers',
                    name=clean_name,
                    line=dict(width=3, color=color),
                    marker=dict(size=8),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 'Meta Share: %{y}%<br>' +
                                 '<extra></extra>'
                ),
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'<b>📊 Standard Metagame Analysis (Match-Based)</b><br><sub>{date_range} | {len(tournaments)} Tournaments | {total_matches:,} Matches | {total_decks:,} Decks</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=True,
        height=1200,
        template='plotly_white',
        font=dict(size=14),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share (%)", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share (%)", row=1, col=2)
    
    # Create complete archetype table
    table_data = []
    for i, (archetype, matches) in enumerate(sorted_archetypes):
        percentage = round((matches / total_matches) * 100, 2)
        decks = archetype_decks.get(archetype, 0)
        avg_matches = round(matches / decks, 1) if decks > 0 else 0
        
        table_data.append({
            'rank': i + 1,
            'archetype': format_archetype_name(archetype) if archetype else "Unknown",
            'matches': matches,
            'percentage': percentage,
            'decks': decks,
            'avg_matches_per_deck': avg_matches,
            'trend': '📈' if i < 10 else '➖'  # Simple trend indicator
        })
    
    # Create HTML with the plot and table
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Standard Metagame Analysis (Match-Based)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            gap: 20px;
        }}
        .stat-card {{
            flex: 1;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .percentage {{
            font-weight: 600;
            color: #667eea;
        }}
        .export-btn {{
            background-color: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 20px 0;
            font-size: 16px;
        }}
        .export-btn:hover {{
            background-color: #5a67d8;
        }}
        .note {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .note strong {{
            color: #d97706;
        }}
        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
            }}
            .container {{
                padding: 15px;
            }}
            table {{
                font-size: 12px;
            }}
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Standard Metagame Analysis</h1>
            <h2>Match-Based Methodology (Community Standard)</h2>
            <p>{date_range}</p>
        </div>
        
        <div class="note">
            <strong>⚠️ Important:</strong> This analysis uses match-based counting (wins + losses), 
            not deck-based counting. This aligns with community standards and provides more accurate 
            meta percentages by weighting successful decks more heavily.
        </div>
        
        <div class="stats">
            <div class="stat-card" onclick="alert('Total competitive tournaments analyzed (excludes leagues)')">
                <h3>{len(tournaments)}</h3>
                <p>Tournaments</p>
            </div>
            <div class="stat-card" onclick="alert('Total matches played across all tournaments')">
                <h3>{total_matches:,}</h3>
                <p>Total Matches</p>
            </div>
            <div class="stat-card" onclick="alert('Total unique decklists submitted')">
                <h3>{total_decks:,}</h3>
                <p>Total Decks</p>
            </div>
            <div class="stat-card" onclick="alert('Total unique archetype strategies identified')">
                <h3>{len(sorted_archetypes)}</h3>
                <p>Unique Archetypes</p>
            </div>
        </div>
        
        <div id="plotDiv">{fig.to_html(div_id="plotDiv", include_plotlyjs=False)}</div>
        
        <h2>Complete Archetype Breakdown</h2>
        <button class="export-btn" onclick="exportTableToCSV()">📥 Export to CSV</button>
        
        <table id="archetypeTable">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Archetype</th>
                    <th>Matches</th>
                    <th>Meta %</th>
                    <th>Decks</th>
                    <th>Avg Matches/Deck</th>
                    <th>Trend</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for row in table_data:
        html_content += f"""
                <tr>
                    <td>{row['rank']}</td>
                    <td><strong>{row['archetype']}</strong></td>
                    <td>{row['matches']:,}</td>
                    <td class="percentage">{row['percentage']}%</td>
                    <td>{row['decks']}</td>
                    <td>{row['avg_matches_per_deck']}</td>
                    <td>{row['trend']}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <script>
        function exportTableToCSV() {
            const table = document.getElementById('archetypeTable');
            let csv = [];
            
            // Get headers
            const headers = [];
            table.querySelectorAll('thead th').forEach(th => {
                headers.push(th.textContent);
            });
            csv.push(headers.join(','));
            
            // Get rows
            table.querySelectorAll('tbody tr').forEach(tr => {
                const row = [];
                tr.querySelectorAll('td').forEach(td => {
                    row.push('"' + td.textContent.replace(/"/g, '""') + '"');
                });
                csv.push(row.join(','));
            });
            
            // Download
            const csvContent = csv.join('\\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'standard_metagame_matches.csv';
            link.click();
        }
    </script>
</body>
</html>
"""
    
    # Save the HTML file
    output_path = Path("data/cache/standard_analysis_matches.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Match-based visualization created: {output_path}")
    print(f"\n📊 Summary:")
    print(f"  - Total Matches: {total_matches:,}")
    print(f"  - Total Decks: {total_decks:,}")
    print(f"  - Tournaments: {len(tournaments)}")
    print(f"  - Unknown Match Rate: {round((match_data['unknown_matches'] / total_matches) * 100, 1)}%")
    print(f"\n🎯 Top 5 Archetypes (by matches):")
    for i, (arch, matches) in enumerate(filtered_archetypes[:5]):
        percentage = round((matches / total_matches) * 100, 2)
        decks = archetype_decks.get(arch, 0)
        clean_name = format_archetype_name(arch)
        print(f"  {i+1}. {clean_name}: {percentage}% ({matches} matches, {decks} decks)")


if __name__ == "__main__":
    create_plotly_visualization()