#!/usr/bin/env python3
"""
Create PLOTLY HTML visualization with TRUE GRADIENTS for MTG colors.
This version uses advanced Plotly techniques to show real gradients.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def create_gradient_bar(x_pos, height, colors, num_segments=20):
    """
    Create a gradient effect using multiple stacked bars.
    
    Args:
        x_pos: X position for the bar
        height: Total height of the bar
        colors: List of color codes
        num_segments: Number of segments for smooth gradient
        
    Returns:
        List of bar traces
    """
    traces = []
    segment_height = height / num_segments
    
    if len(colors) == 1:
        # Single color - no gradient needed
        return [go.Bar(
            x=[x_pos],
            y=[height],
            marker_color=MTG_COLORS[colors[0]],
            showlegend=False,
            hoverinfo='skip'
        )]
    
    # Create gradient segments
    for i in range(num_segments):
        ratio = i / (num_segments - 1)
        
        if len(colors) == 2:
            # Interpolate between two colors
            color = interpolate_color(MTG_COLORS[colors[0]], MTG_COLORS[colors[1]], ratio)
        else:
            # For 3+ colors, determine which pair we're between
            segment = ratio * (len(colors) - 1)
            idx = int(segment)
            local_ratio = segment - idx
            
            if idx < len(colors) - 1:
                color = interpolate_color(MTG_COLORS[colors[idx]], MTG_COLORS[colors[idx + 1]], local_ratio)
            else:
                color = MTG_COLORS[colors[-1]]
        
        traces.append(go.Bar(
            x=[x_pos],
            y=[segment_height],
            marker_color=color,
            showlegend=False,
            hoverinfo='skip',
            base=i * segment_height
        ))
    
    return traces


def interpolate_color(color1, color2, ratio):
    """Interpolate between two hex colors."""
    # Convert hex to RGB
    c1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
    c2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
    
    # Interpolate
    result_rgb = tuple(int(c1_rgb[i] * (1 - ratio) + c2_rgb[i] * ratio) for i in range(3))
    
    # Convert back to hex
    return f"#{result_rgb[0]:02x}{result_rgb[1]:02x}{result_rgb[2]:02x}"


def create_plotly_visualization():
    """Create interactive HTML visualization with true gradients"""
    
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    # Filter out leagues
    tournaments = [t for t in tournaments if 'league' not in t.type.lower()]
    
    # Calculate temporal data for timeline
    temporal_data = calculate_temporal_data(tournaments)
    
    # Prepare data for visualization
    archetypes = meta_snapshot['archetypes']
    total_decks = meta_snapshot['total_decks']
    
    # Extract counts from archetype data
    archetype_counts = {}
    for arch, data in archetypes.items():
        if isinstance(data, dict):
            archetype_counts[arch] = data['count']
        else:
            archetype_counts[arch] = data
    
    # Sort archetypes by count
    sorted_archetypes = sorted(archetype_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Prepare chart data
    labels = []
    values = []
    percentages = []
    
    for archetype, count in sorted_archetypes[:10]:  # Top 10 for gradient demo
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        column_widths=[0.5, 0.5],
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter", "colspan": 2}, None]],
        subplot_titles=("🎨 MTG Color Gradients Demo", 
                       "📊 Meta Distribution with Gradients",
                       "📉 Meta Evolution Timeline"),
        vertical_spacing=0.25,
        horizontal_spacing=0.20
    )
    
    # 1. Gradient Demo - Show pure gradients for each archetype
    y_pos = 0
    for i, label in enumerate(labels):
        arch_colors = get_archetype_colors(label)
        
        if len(arch_colors) >= 2:
            # Create gradient line
            x = np.linspace(0, 1, 100)
            y = np.full_like(x, y_pos)
            
            # Create color array
            colors_array = []
            for j in range(len(x)):
                ratio = j / (len(x) - 1)
                if len(arch_colors) == 2:
                    color = interpolate_color(MTG_COLORS[arch_colors[0]], MTG_COLORS[arch_colors[1]], ratio)
                else:
                    # Multi-color gradient
                    segment = ratio * (len(arch_colors) - 1)
                    idx = int(segment)
                    local_ratio = segment - idx
                    if idx < len(arch_colors) - 1:
                        color = interpolate_color(MTG_COLORS[arch_colors[idx]], MTG_COLORS[arch_colors[idx + 1]], local_ratio)
                    else:
                        color = MTG_COLORS[arch_colors[-1]]
                colors_array.append(color)
            
            # Add scatter trace with gradient
            for j in range(len(x) - 1):
                fig.add_trace(
                    go.Scatter(
                        x=[x[j], x[j+1]],
                        y=[y[j], y[j+1]],
                        mode='lines',
                        line=dict(color=colors_array[j], width=20),
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=1, col=1
                )
            
            # Add label
            fig.add_annotation(
                x=1.1,
                y=y_pos,
                text=label,
                showarrow=False,
                xref="x",
                yref="y",
                row=1, col=1
            )
        
        y_pos -= 1
    
    # 2. Bar Chart with real gradients
    # We'll create stacked segments for each bar
    for i, (label, value) in enumerate(zip(labels, values)):
        arch_colors = get_archetype_colors(label)
        
        if len(arch_colors) == 1:
            # Single color bar
            fig.add_trace(
                go.Bar(
                    x=[i],
                    y=[value],
                    marker_color=MTG_COLORS[arch_colors[0]],
                    showlegend=False,
                    text=f"{value} ({percentages[i]}%)",
                    textposition='outside',
                    hovertemplate=f'<b>{label}</b><br>Decks: {value}<br>Meta Share: {percentages[i]}%<extra></extra>'
                ),
                row=1, col=2
            )
        else:
            # Multi-color gradient bar
            num_segments = 20
            segment_height = value / num_segments
            
            for j in range(num_segments):
                ratio = j / (num_segments - 1)
                
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
                
                show_text = j == num_segments - 1  # Only show text on top segment
                
                fig.add_trace(
                    go.Bar(
                        x=[i],
                        y=[segment_height],
                        base=j * segment_height,
                        marker_color=color,
                        showlegend=False,
                        text=f"{value} ({percentages[i]}%)" if show_text else "",
                        textposition='outside' if show_text else 'none',
                        hovertemplate=f'<b>{label}</b><br>Decks: {value}<br>Meta Share: {percentages[i]}%<extra></extra>' if j == 0 else None,
                        hoverinfo='skip' if j > 0 else 'all'
                    ),
                    row=1, col=2
                )
    
    # Update axes for gradient demo
    fig.update_xaxes(range=[-0.1, 1.5], showticklabels=False, showgrid=False, row=1, col=1)
    fig.update_yaxes(range=[-len(labels), 1], showticklabels=False, showgrid=False, row=1, col=1)
    
    # Update axes for bar chart
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(range(len(labels))),
        ticktext=labels,
        tickangle=-45,
        row=1, col=2
    )
    fig.update_yaxes(title_text="Number of Decks", row=1, col=2)
    
    # 3. Timeline with gradient lines (simplified for clarity)
    timeline_data = prepare_timeline_data(temporal_data, sorted_archetypes[:5])
    
    # Group data by archetype
    archetype_lines = {}
    for record in timeline_data:
        arch = record['archetype']
        if arch not in archetype_lines:
            archetype_lines[arch] = {'dates': [], 'percentages': []}
        archetype_lines[arch]['dates'].append(record['date'])
        archetype_lines[arch]['percentages'].append(record['percentage'])
    
    # Add timeline traces
    for i, (arch, data) in enumerate(archetype_lines.items()):
        arch_colors = get_archetype_colors(arch)
        
        if len(arch_colors) == 1:
            line_color = MTG_COLORS[arch_colors[0]]
        else:
            # Use primary color for line, with gradient marker
            line_color = MTG_COLORS[arch_colors[0]]
        
        fig.add_trace(
            go.Scatter(
                x=data['dates'],
                y=data['percentages'],
                mode='lines+markers',
                name=arch,
                line=dict(width=3, color=line_color),
                marker=dict(
                    size=8,
                    color=MTG_COLORS[arch_colors[1]] if len(arch_colors) > 1 else line_color,
                    line=dict(color=line_color, width=2)
                ),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Meta Share: %{y:.1f}%<br>' +
                             '<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'🎯 Manalytics - True MTG Color Gradients Demo<br>' +
                   f'<sub>Showing real gradients for multi-color archetypes</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=True,
        height=1100,
        template='plotly_white',
        hovermode='closest',
        margin=dict(t=140, b=80, l=80, r=120)
    )
    
    # Update timeline axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - MTG Gradients Demo</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        #chart {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .info {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .gradient-preview {{
            display: inline-block;
            width: 100px;
            height: 20px;
            margin: 0 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 MTG Color Gradients Visualization</h1>
        <p>True gradients for multi-color archetypes</p>
    </div>
    
    <div class="info">
        <h3>Color Examples:</h3>
        <div>
            <span>Izzet (Blue/Red):</span>
            <span class="gradient-preview" style="background: linear-gradient(to right, #0E68AB, #F44336);"></span>
        </div>
        <div>
            <span>Dimir (Blue/Black):</span>
            <span class="gradient-preview" style="background: linear-gradient(to right, #0E68AB, #1C1C1C);"></span>
        </div>
        <div>
            <span>Boros (Red/White):</span>
            <span class="gradient-preview" style="background: linear-gradient(to right, #F44336, #FFFBD5);"></span>
        </div>
        <div>
            <span>Golgari (Black/Green):</span>
            <span class="gradient-preview" style="background: linear-gradient(to right, #1C1C1C, #4CAF50);"></span>
        </div>
    </div>
    
    <div id="chart"></div>
    
    <script>
        var fig = {fig.to_json()};
        Plotly.newPlot('chart', fig.data, fig.layout, {{responsive: true}});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_file = Path("data/cache/standard_analysis_gradients.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Gradient visualization created: {output_file}")
    
    return output_file


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
                
                if count > 0:  # Only add if there's data
                    timeline_records.append({
                        'date': date,
                        'archetype': clean_arch,
                        'count': count,
                        'percentage': round(percentage, 2)
                    })
    
    return timeline_records


if __name__ == "__main__":
    create_plotly_visualization()