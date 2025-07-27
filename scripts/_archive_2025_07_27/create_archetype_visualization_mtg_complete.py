#!/usr/bin/env python3
"""
Complete MTG-themed visualization with gradients everywhere possible.
Uses advanced Plotly techniques including sunburst for pie chart gradients.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import math

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def interpolate_color(color1, color2, ratio):
    """Interpolate between two hex colors."""
    # Convert hex to RGB
    c1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
    c2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
    
    # Interpolate
    result_rgb = tuple(int(c1_rgb[i] * (1 - ratio) + c2_rgb[i] * ratio) for i in range(3))
    
    # Convert back to hex
    return f"#{result_rgb[0]:02x}{result_rgb[1]:02x}{result_rgb[2]:02x}"


def create_sunburst_gradient_data(labels, values, percentages):
    """
    Create sunburst data structure to simulate gradients in circular chart.
    Each multi-color archetype gets multiple thin slices.
    """
    sunburst_labels = []
    sunburst_parents = []
    sunburst_values = []
    sunburst_colors = []
    sunburst_text = []
    
    # Add root
    sunburst_labels.append("Metagame")
    sunburst_parents.append("")
    sunburst_values.append(sum(values[:10]))  # Top 10
    sunburst_colors.append("#FFFFFF")
    sunburst_text.append("")
    
    # Process each archetype
    for i in range(min(10, len(labels))):
        label = labels[i]
        value = values[i]
        percentage = percentages[i]
        arch_colors = get_archetype_colors(label)
        
        if len(arch_colors) == 1:
            # Single color - add as single slice
            sunburst_labels.append(f"{label}<br>{percentage}%")
            sunburst_parents.append("Metagame")
            sunburst_values.append(value)
            sunburst_colors.append(MTG_COLORS[arch_colors[0]])
            sunburst_text.append(f"{value} decks")
        else:
            # Multi-color - create gradient slices
            num_slices = 20  # Number of gradient segments
            slice_value = value / num_slices
            
            for j in range(num_slices):
                ratio = j / (num_slices - 1)
                
                # Interpolate color
                if len(arch_colors) == 2:
                    color = interpolate_color(MTG_COLORS[arch_colors[0]], MTG_COLORS[arch_colors[1]], ratio)
                else:
                    # 3+ colors
                    segment = ratio * (len(arch_colors) - 1)
                    idx = int(segment)
                    local_ratio = segment - idx
                    if idx < len(arch_colors) - 1:
                        color = interpolate_color(MTG_COLORS[arch_colors[idx]], MTG_COLORS[arch_colors[idx + 1]], local_ratio)
                    else:
                        color = MTG_COLORS[arch_colors[-1]]
                
                # Add label only to middle slice
                if j == num_slices // 2:
                    slice_label = f"{label}<br>{percentage}%"
                    slice_text = f"{value} decks"
                else:
                    slice_label = " "  # Space to avoid empty string issues
                    slice_text = ""
                
                sunburst_labels.append(slice_label)
                sunburst_parents.append("Metagame")
                sunburst_values.append(slice_value)
                sunburst_colors.append(color)
                sunburst_text.append(slice_text)
    
    return sunburst_labels, sunburst_parents, sunburst_values, sunburst_colors, sunburst_text


def create_gradient_bars_data(labels, values, percentages):
    """Create stacked bar data for gradient effect."""
    bar_traces = []
    
    for i, (label, value, percentage) in enumerate(zip(labels[:10], values[:10], percentages[:10])):
        arch_colors = get_archetype_colors(label)
        
        if len(arch_colors) == 1:
            # Single color bar
            bar_traces.append(go.Bar(
                x=[label],
                y=[value],
                marker_color=MTG_COLORS[arch_colors[0]],
                text=f"{value}<br>({percentage}%)",
                textposition='outside',
                hovertemplate=f'<b>{label}</b><br>Decks: {value}<br>Meta Share: {percentage}%<extra></extra>',
                showlegend=False
            ))
        else:
            # Multi-color gradient bar
            num_segments = 30
            segment_height = value / num_segments
            
            for j in range(num_segments):
                ratio = j / (num_segments - 1)
                
                # Interpolate color
                if len(arch_colors) == 2:
                    color = interpolate_color(MTG_COLORS[arch_colors[0]], MTG_COLORS[arch_colors[1]], ratio)
                else:
                    segment = ratio * (len(arch_colors) - 1)
                    idx = int(segment)
                    local_ratio = segment - idx
                    if idx < len(arch_colors) - 1:
                        color = interpolate_color(MTG_COLORS[arch_colors[idx]], MTG_COLORS[arch_colors[idx + 1]], local_ratio)
                    else:
                        color = MTG_COLORS[arch_colors[-1]]
                
                # Show text only on top segment
                show_text = j == num_segments - 1
                
                bar_traces.append(go.Bar(
                    x=[label],
                    y=[segment_height],
                    marker_color=color,
                    text=f"{value}<br>({percentage}%)" if show_text else "",
                    textposition='outside' if show_text else 'none',
                    hovertemplate=f'<b>{label}</b><br>Decks: {value}<br>Meta Share: {percentage}%<extra></extra>' if j == 0 else None,
                    hoverinfo='all' if j == 0 else 'skip',
                    showlegend=False,
                    offsetgroup=i,
                    base=j * segment_height if j > 0 else 0
                ))
    
    return bar_traces


def create_plotly_visualization():
    """Create complete MTG-themed visualization"""
    
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    # Filter out leagues
    tournaments = [t for t in tournaments if 'league' not in t.type.lower()]
    
    # Calculate temporal data
    temporal_data = calculate_temporal_data(tournaments)
    
    # Prepare data
    archetypes = meta_snapshot['archetypes']
    total_decks = meta_snapshot['total_decks']
    
    # Extract counts
    archetype_counts = {}
    for arch, data in archetypes.items():
        if isinstance(data, dict):
            archetype_counts[arch] = data['count']
        else:
            archetype_counts[arch] = data
    
    # Sort archetypes
    sorted_archetypes = sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare chart data
    labels = []
    values = []
    percentages = []
    
    for archetype, count in sorted_archetypes[:20]:
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
    
    # Create figure
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.6, 0.4],
        specs=[[{"type": "sunburst"}, {"type": "bar"}],
               [{"type": "scatter", "colspan": 2}, None]],
        subplot_titles=("🎨 Meta Distribution (MTG Gradients)", 
                       "📊 Top Archetypes",
                       "📈 Meta Evolution Timeline"),
        vertical_spacing=0.20,
        horizontal_spacing=0.15
    )
    
    # 1. Sunburst chart for gradient pie effect
    sunburst_labels, sunburst_parents, sunburst_values, sunburst_colors, sunburst_text = create_sunburst_gradient_data(labels, values, percentages)
    
    fig.add_trace(
        go.Sunburst(
            labels=sunburst_labels,
            parents=sunburst_parents,
            values=sunburst_values,
            marker=dict(
                colors=sunburst_colors,
                line=dict(width=0)  # No borders for smooth gradients
            ),
            text=sunburst_text,
            textinfo="label",
            hovertemplate='<b>%{label}</b><br>%{text}<extra></extra>',
            insidetextorientation='radial'
        ),
        row=1, col=1
    )
    
    # 2. Gradient bar chart
    bar_traces = create_gradient_bars_data(labels, values, percentages)
    for trace in bar_traces:
        fig.add_trace(trace, row=1, col=2)
    
    # 3. Timeline with gradient markers
    timeline_data = prepare_timeline_data(temporal_data, sorted_archetypes[:5])
    
    # Group data by archetype
    archetype_lines = {}
    for record in timeline_data:
        arch = record['archetype']
        if arch not in archetype_lines:
            archetype_lines[arch] = {'dates': [], 'percentages': []}
        archetype_lines[arch]['dates'].append(record['date'])
        archetype_lines[arch]['percentages'].append(record['percentage'])
    
    # Add timeline traces with gradient lines
    for i, (arch, data) in enumerate(archetype_lines.items()):
        arch_colors = get_archetype_colors(arch)
        
        if len(arch_colors) == 1:
            # Single color
            fig.add_trace(
                go.Scatter(
                    x=data['dates'],
                    y=data['percentages'],
                    mode='lines+markers',
                    name=arch,
                    line=dict(width=4, color=MTG_COLORS[arch_colors[0]]),
                    marker=dict(size=10, color=MTG_COLORS[arch_colors[0]], line=dict(width=2, color='white')),
                    hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Meta Share: %{y:.1f}%<extra></extra>'
                ),
                row=2, col=1
            )
        else:
            # Multi-color with gradient effect
            # Create segments for gradient line
            for j in range(len(data['dates']) - 1):
                # Calculate color for this segment
                segment_ratio = j / max(1, len(data['dates']) - 2)
                
                if len(arch_colors) == 2:
                    segment_color = interpolate_color(MTG_COLORS[arch_colors[0]], MTG_COLORS[arch_colors[1]], segment_ratio)
                else:
                    color_idx = int(segment_ratio * (len(arch_colors) - 1))
                    local_ratio = (segment_ratio * (len(arch_colors) - 1)) - color_idx
                    if color_idx < len(arch_colors) - 1:
                        segment_color = interpolate_color(MTG_COLORS[arch_colors[color_idx]], MTG_COLORS[arch_colors[color_idx + 1]], local_ratio)
                    else:
                        segment_color = MTG_COLORS[arch_colors[-1]]
                
                fig.add_trace(
                    go.Scatter(
                        x=[data['dates'][j], data['dates'][j+1]],
                        y=[data['percentages'][j], data['percentages'][j+1]],
                        mode='lines',
                        line=dict(width=4, color=segment_color),
                        showlegend=False if j > 0 else True,
                        name=arch if j == 0 else None,
                        hovertemplate='<b>' + arch + '</b><br>Date: %{x}<br>Meta Share: %{y:.1f}%<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # Add markers separately
            fig.add_trace(
                go.Scatter(
                    x=data['dates'],
                    y=data['percentages'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=[interpolate_color(MTG_COLORS[arch_colors[0]], MTG_COLORS[arch_colors[-1]], i/(len(data['dates'])-1)) for i in range(len(data['dates']))],
                        line=dict(width=2, color='white')
                    ),
                    showlegend=False,
                    hovertemplate='<b>' + arch + '</b><br>Date: %{x}<br>Meta Share: %{y:.1f}%<extra></extra>'
                ),
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'🎯 Manalytics - Complete MTG Color Gradient Analysis<br>' +
                   f'<sub>Tournaments Only (Leagues Excluded) - {datetime.now().strftime("%B %d, %Y")}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=True,
        height=1200,
        template='plotly_white',
        hovermode='closest',
        margin=dict(t=140, b=60, l=60, r=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Update axes
    fig.update_xaxes(showgrid=False, showticklabels=False, row=1, col=2)
    fig.update_yaxes(title_text="Number of Decks", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
    
    # Generate full HTML
    html_content = generate_full_html(fig, tournaments, total_decks, sorted_archetypes, archetype_counts)
    
    # Save HTML file
    output_file = Path("data/cache/standard_analysis_mtg_gradients.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Complete MTG gradient visualization created: {output_file}")
    print(f"📊 Processed {total_decks} decks from {len(tournaments)} tournaments")
    print(f"🎯 Top archetype: {format_archetype_name(sorted_archetypes[0][0])} with {sorted_archetypes[0][1]} decks ({percentages[0]}%)")
    
    return output_file


def generate_full_html(fig, tournaments, total_decks, sorted_archetypes, archetype_counts):
    """Generate complete HTML with stats and table."""
    
    # Calculate date range
    if tournaments:
        dates = [t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d') for t in tournaments]
        date_range = f"{min(dates)} to {max(dates)}"
    else:
        date_range = "No data"
    
    # Create table data
    table_data = []
    for i, (archetype, count) in enumerate(sorted_archetypes, 1):
        percentage = (count / total_decks) * 100
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        arch_colors = get_archetype_colors(clean_name)
        
        # Create gradient style for table row
        if len(arch_colors) == 1:
            row_style = f"background-color: {MTG_COLORS[arch_colors[0]]}22;"
        else:
            colors_str = ', '.join([MTG_COLORS[c] for c in arch_colors])
            row_style = f"background: linear-gradient(to right, {colors_str}22);"
        
        table_data.append({
            'rank': i,
            'name': clean_name,
            'count': count,
            'percentage': f'{percentage:.2f}%',
            'style': row_style
        })
    
    # Build table HTML
    table_rows = ""
    for row in table_data[:20]:  # Top 20 for table
        table_rows += f"""
        <tr style="{row['style']}">
            <td>#{row['rank']}</td>
            <td><strong>{row['name']}</strong></td>
            <td>{row['count']}</td>
            <td>{row['percentage']}</td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - MTG Gradient Metagame Analysis</title>
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
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .container {{
            max-width: 1600px;
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
            position: relative;
            overflow: hidden;
        }}
        .stat-box::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(to right, #0E68AB, #F44336);
        }}
        .stat-box:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #mainChart {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{
            background: rgba(102, 126, 234, 0.05);
        }}
        .gradient-showcase {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .gradient-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .gradient-bar {{
            width: 150px;
            height: 20px;
            border-radius: 10px;
            margin-right: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics - MTG Gradient Metagame Analysis</h1>
        <p>Revolutionary visualization with true Magic color gradients</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(tournaments)}</div>
                <div class="stat-label">Total Tournaments</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_decks}</div>
                <div class="stat-label">Total Decks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(archetype_counts)}</div>
                <div class="stat-label">Unique Archetypes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="font-size: 1.5em;">{format_archetype_name(sorted_archetypes[0][0]) if sorted_archetypes else 'N/A'}</div>
                <div class="stat-label">Top Archetype</div>
            </div>
        </div>
        
        <div class="gradient-showcase">
            <h3>🎨 MTG Color Gradient Examples</h3>
            <div class="gradient-item">
                <div class="gradient-bar" style="background: linear-gradient(to right, #0E68AB, #F44336);"></div>
                <span><strong>Izzet</strong> (Blue → Red)</span>
            </div>
            <div class="gradient-item">
                <div class="gradient-bar" style="background: linear-gradient(to right, #0E68AB, #1C1C1C);"></div>
                <span><strong>Dimir</strong> (Blue → Black)</span>
            </div>
            <div class="gradient-item">
                <div class="gradient-bar" style="background: linear-gradient(to right, #F44336, #FFFBD5);"></div>
                <span><strong>Boros</strong> (Red → White)</span>
            </div>
            <div class="gradient-item">
                <div class="gradient-bar" style="background: linear-gradient(to right, #1C1C1C, #4CAF50);"></div>
                <span><strong>Golgari</strong> (Black → Green)</span>
            </div>
            <div class="gradient-item">
                <div class="gradient-bar" style="background: linear-gradient(to right, #F44336, #4CAF50, #FFFBD5);"></div>
                <span><strong>Naya</strong> (Red → Green → White)</span>
            </div>
        </div>
        
        <div id="mainChart"></div>
        
        <div class="table-container">
            <h3>📊 Top 20 Archetypes Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Archetype</th>
                        <th>Decks</th>
                        <th>Meta %</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        var mainFig = {fig.to_json()};
        Plotly.newPlot('mainChart', mainFig.data, mainFig.layout, {{responsive: true}});
    </script>
</body>
</html>
"""


def calculate_temporal_data(tournaments):
    """Calculate archetype counts by date"""
    temporal_data = defaultdict(lambda: defaultdict(int))
    
    # Load decklists from JSON
    current_month = datetime.now().strftime("%Y-%m")
    monthly_file = Path("data/cache/decklists") / f"{current_month}.json"
    
    if monthly_file.exists():
        with open(monthly_file, 'r') as f:
            all_decklists = json.load(f)
        
        for tournament in tournaments:
            date = tournament.date if isinstance(tournament.date, str) else tournament.date.strftime('%Y-%m-%d')
            
            if tournament.id in all_decklists:
                decklists = all_decklists[tournament.id].get('decklists', [])
                for deck in decklists:
                    archetype = deck.get('archetype', 'Unknown')
                    temporal_data[date][archetype] += 1
    
    return dict(temporal_data)


def prepare_timeline_data(temporal_data, top_archetypes):
    """Prepare timeline data for top archetypes"""
    timeline_records = []
    
    # Get last 30 days
    dates = sorted(temporal_data.keys())
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_dates = [d for d in dates if d >= cutoff]
    
    for date in recent_dates:
        day_data = temporal_data[date]
        total = sum(day_data.values())
        
        if total > 0:
            for archetype, _ in top_archetypes[:5]:  # Top 5 for timeline
                clean_arch = format_archetype_name(archetype) if archetype else "Unknown"
                count = day_data.get(archetype, 0)
                percentage = (count / total * 100) if total > 0 else 0
                
                if count > 0:
                    timeline_records.append({
                        'date': date,
                        'archetype': clean_arch,
                        'count': count,
                        'percentage': round(percentage, 2)
                    })
    
    return timeline_records


if __name__ == "__main__":
    create_plotly_visualization()