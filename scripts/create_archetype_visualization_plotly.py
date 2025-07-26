#!/usr/bin/env python3
"""
Create PLOTLY HTML visualization of archetype distribution.
Version avec Plotly pour une meilleure interactivité.
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
    """Create interactive HTML visualization with Plotly"""
    
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
    
    # Filter archetypes above 1.5% threshold
    min_threshold = total_decks * 0.015  # 1.5%
    filtered_archetypes = [(arch, count) for arch, count in sorted_archetypes if count >= min_threshold]
    
    # Filter archetypes above 1.5% threshold
    min_threshold = total_decks * 0.015  # 1.5%
    filtered_archetypes = [(arch, count) for arch, count in sorted_archetypes if count >= min_threshold]
    
    # Prepare chart data
    labels = []
    values = []
    percentages = []
    raw_archetypes = []  # Keep raw names for color mapping
    
    # Only show archetypes above 1.5%
    for archetype, count in filtered_archetypes:
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
        raw_archetypes.append(archetype)
    
    # NO "Others" category - we only show archetypes above 1.5%
    
    # Get MTG-based colors for pie chart
    # For gradients, we'll use the primary color for now
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
        subplot_titles=("📊 Meta Distribution (Click to Filter)", 
                       "📈 Top Archetypes",
                       "📉 Meta Evolution Timeline (Last 30 Days)"),
        vertical_spacing=0.25,  # Increased from 0.15
        horizontal_spacing=0.20  # Increased from 0.1
    )
    
    # 1. Pie Chart - avec vrais gradients via injection SVG
    # On va utiliser les couleurs de base et appliquer les gradients après le rendu
    pie_colors = []
    
    for i in range(min(10, len(labels))):
        arch_colors = get_archetype_colors(labels[i])
        if len(arch_colors) == 1:
            pie_colors.append(MTG_COLORS[arch_colors[0]])
        else:
            # Pour multi-couleurs, on utilise la première couleur
            # Les gradients seront appliqués via JavaScript après le rendu
            pie_colors.append(MTG_COLORS[arch_colors[0]])
    
    fig.add_trace(
        go.Pie(
            labels=labels[:10],
            values=values[:10],
            hole=0,
            marker=dict(
                colors=pie_colors,
                line=dict(color='white', width=2)
            ),
            textposition='outside',
            textinfo='label+text',
            text=[f'{p}%' for p in percentages[:10]],
            customdata=percentages[:10],
            hovertemplate='<b>%{label}</b><br>' +
                         'Decks: %{value}<br>' +
                         'Meta Share: %{customdata}%<br>' +
                         '<extra></extra>',
            insidetextorientation='radial'
        ),
        row=1, col=1
    )
    
    # 2. Bar Chart with gradient effect
    # We need to create a single trace with all bars for proper display
    num_bars = min(10, len(labels))
    
    # Prepare data for grouped bars
    bar_x = []
    bar_y = []
    bar_colors = []
    bar_texts = []
    
    # First pass: create base bars
    for i in range(num_bars):
        arch_colors = get_archetype_colors(labels[i])
        
        if len(arch_colors) == 1:
            # Single color
            bar_x.append(labels[i])
            bar_y.append(values[i])
            bar_colors.append(MTG_COLORS[arch_colors[0]])
            bar_texts.append(f"{values[i]} ({percentages[i]}%)")
        else:
            # For multi-color, we'll use a blended color for now
            # True gradients will be applied via post-processing
            primary_color = MTG_COLORS[arch_colors[0]]
            secondary_color = MTG_COLORS[arch_colors[1]] if len(arch_colors) > 1 else primary_color
            blended = blend_colors(primary_color, secondary_color, 0.5)
            
            bar_x.append(labels[i])
            bar_y.append(values[i])
            bar_colors.append(blended)
            bar_texts.append(f"{values[i]} ({percentages[i]}%)")
    
    # Add the main bar trace
    fig.add_trace(
        go.Bar(
            x=bar_x,
            y=bar_y,
            marker=dict(
                color=bar_colors,
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=bar_texts,
            textposition='outside',
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Decks: %{y}<br>Meta Share: %{text}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Store gradient info for bar chart post-processing
    bar_gradient_info = []
    for i in range(num_bars):
        arch_colors = get_archetype_colors(labels[i])
        if len(arch_colors) > 1:
            bar_gradient_info.append({
                'index': i,
                'label': labels[i],
                'colors': arch_colors
            })
    
    # 3. Timeline Chart - use filtered archetypes
    timeline_data = prepare_timeline_data(temporal_data, filtered_archetypes[:5])
    
    # Group data by archetype
    archetype_lines = {}
    for record in timeline_data:
        arch = record['archetype']
        if arch not in archetype_lines:
            archetype_lines[arch] = {'dates': [], 'percentages': []}
        archetype_lines[arch]['dates'].append(record['date'])
        archetype_lines[arch]['percentages'].append(record['percentage'])
    
    # Add timeline traces with MTG colors
    for i, (arch, data) in enumerate(archetype_lines.items()):
        # Get colors for this archetype
        arch_colors = get_archetype_colors(arch)
        if len(arch_colors) == 1:
            line_color = MTG_COLORS[arch_colors[0]]
        else:
            # For multi-color, use the primary color
            line_color = MTG_COLORS[arch_colors[0]]
        
        fig.add_trace(
            go.Scatter(
                x=data['dates'],
                y=data['percentages'],
                mode='lines+markers',
                name=arch,
                line=dict(width=3, color=line_color),
                marker=dict(size=6, color=line_color),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x}<br>' +
                             'Meta Share: %{y:.1f}%<br>' +
                             '<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Update layout with better margins and height
    fig.update_layout(
        title={
            'text': f'🎯 Manalytics - Interactive Standard Metagame Analysis<br>' +
                   f'<sub>Tournaments Only (Leagues Excluded) - {datetime.now().strftime("%B %d, %Y")}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=True,
        height=1100,  # Increased from 900
        template='plotly_white',
        hovermode='closest',
        margin=dict(t=140, b=80, l=80, r=120)  # Increased margins
    )
    
    # Update axes
    fig.update_xaxes(tickangle=-45, row=1, col=2, showgrid=False)
    fig.update_yaxes(title_text="Number of Decks", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
    
    # Create table data - only show archetypes above 1.5%
    table_data = []
    for i, (archetype, count) in enumerate(filtered_archetypes, 1):
        percentage = (count / total_decks) * 100
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        per_tournament = round(count / len(tournaments), 1) if tournaments else 0
        trend = calculate_trend(archetype, temporal_data)
        
        table_data.append({
            'Rank': f'#{i}',
            'Archetype': clean_name,
            'Decks': count,
            'Meta %': f'{percentage:.2f}%',
            'Avg/Tournament': per_tournament,
            'Trend': trend
        })
    
    # Create table
    table_fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(table_data[0].keys()),
            fill_color='rgba(102, 126, 234, 0.8)',
            font=dict(color='white', size=14),
            align='left',
            height=40
        ),
        cells=dict(
            values=[
                [d['Rank'] for d in table_data],
                [d['Archetype'] for d in table_data],
                [d['Decks'] for d in table_data],
                [d['Meta %'] for d in table_data],
                [d['Avg/Tournament'] for d in table_data],
                [d['Trend'] for d in table_data]
            ],
            fill_color='lavender',
            align='left',
            height=30,
            font=dict(size=12)
        )
    )])
    
    table_fig.update_layout(
        title='🏆 Complete Archetype Breakdown',
        height=600,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    
    # Prepare gradient definitions for SVG injection
    gradient_defs = []
    gradient_info = []  # Pour stocker les infos sur chaque gradient
    
    for i, label in enumerate(labels[:10]):
        arch_colors = get_archetype_colors(label)
        if len(arch_colors) > 1:
            gradient_id = f"gradient_{i}"
            gradient_info.append({
                'index': i,
                'id': gradient_id,
                'colors': arch_colors
            })
            
            # Créer un gradient radial pour le pie chart (du centre vers l'extérieur)
            if len(arch_colors) == 2:
                gradient_defs.append(f"""
                    <radialGradient id="{gradient_id}" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:{MTG_COLORS[arch_colors[0]]};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{MTG_COLORS[arch_colors[1]]};stop-opacity:1" />
                    </radialGradient>
                """)
            else:
                # 3+ colors
                stops = []
                for j, color in enumerate(arch_colors):
                    offset = (j / (len(arch_colors) - 1)) * 100
                    stops.append(f'<stop offset="{offset}%" style="stop-color:{MTG_COLORS[color]};stop-opacity:1" />')
                gradient_defs.append(f"""
                    <radialGradient id="{gradient_id}" cx="50%" cy="50%" r="50%">
                        {''.join(stops)}
                    </radialGradient>
                """)
    
    # Create HTML with both figures
    html_content = f"""
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
        <p>Click on charts to filter • Hover for details • Export to PNG/SVG</p>
        
        <div class="controls">
            <button onclick="downloadCSV()">📊 Download CSV</button>
            <button onclick="resetFilters()">🔄 Reset Filters</button>
        </div>
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
                <div class="stat-value">{len(filtered_archetypes)}</div>
                <div class="stat-label">Archetypes > 1.5%</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="font-size: 1.5em;">{format_archetype_name(sorted_archetypes[0][0]) if sorted_archetypes else 'N/A'}</div>
                <div class="stat-label">Top Archetype</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Standard</div>
                <div class="stat-label">Format</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="font-size: 1.2em;">{date_range}</div>
                <div class="stat-label">Date Range</div>
            </div>
        </div>
        
        <div id="mainChart"></div>
        <div id="tableChart"></div>
    </div>
    
    <script>
        var mainFig = {fig.to_json()};
        var tableFig = {table_fig.to_json()};
        
        // Store bar gradient info
        var barGradientInfo = {json.dumps(bar_gradient_info)};
        
        Plotly.newPlot('mainChart', mainFig.data, mainFig.layout, {{responsive: true}}).then(function() {{
            // Apply gradients to pie slices and bars after rendering
            setTimeout(function() {{
                var svg = document.querySelector('#mainChart svg.main-svg');
                if (!svg) return;
                
                // Create or get defs element
                var defs = svg.querySelector('defs') || svg.insertBefore(document.createElementNS('http://www.w3.org/2000/svg', 'defs'), svg.firstChild);
                
                // Add gradient definitions for pie
                var gradientDefs = `{''.join(gradient_defs)}`;
                
                // Define MTG colors in JavaScript
                var mtgColors = {{
                    'W': '#FFFBD5',
                    'U': '#0E68AB',
                    'B': '#1C1C1C',
                    'R': '#F44336',
                    'G': '#4CAF50',
                    'C': '#9E9E9E'
                }};
                
                // Add linear gradients for bars
                barGradientInfo.forEach(function(info, idx) {{
                    var barGradientId = 'bar_gradient_' + idx;
                    var colors = info.colors;
                    
                    if (colors.length === 2) {{
                        gradientDefs += `
                            <linearGradient id="${{barGradientId}}" x1="0%" y1="100%" x2="0%" y2="0%">
                                <stop offset="0%" style="stop-color:${{mtgColors[colors[0]]}};stop-opacity:1" />
                                <stop offset="100%" style="stop-color:${{mtgColors[colors[1]]}};stop-opacity:1" />
                            </linearGradient>
                        `;
                    }} else if (colors.length > 2) {{
                        var stops = '';
                        colors.forEach(function(color, i) {{
                            var offset = (i / (colors.length - 1)) * 100;
                            stops += `<stop offset="${{offset}}%" style="stop-color:${{mtgColors[color]}};stop-opacity:1" />`;
                        }});
                        gradientDefs += `
                            <linearGradient id="${{barGradientId}}" x1="0%" y1="100%" x2="0%" y2="0%">
                                ${{stops}}
                            </linearGradient>
                        `;
                    }}
                }});
                
                defs.innerHTML += gradientDefs;
                
                // Apply gradients to pie slices
                var pieSlices = svg.querySelectorAll('.slice path');
                var gradientInfo = {json.dumps(gradient_info)};
                
                gradientInfo.forEach(function(info) {{
                    if (info.index < pieSlices.length) {{
                        pieSlices[info.index].style.fill = 'url(#' + info.id + ')';
                        pieSlices[info.index].setAttribute('fill', 'url(#' + info.id + ')');
                    }}
                }});
                
                // Apply gradients to bars
                var barRects = svg.querySelectorAll('.barlayer .bars rect');
                barGradientInfo.forEach(function(info, idx) {{
                    var barIndex = info.index;
                    if (barIndex < barRects.length) {{
                        barRects[barIndex].style.fill = 'url(#bar_gradient_' + idx + ')';
                        barRects[barIndex].setAttribute('fill', 'url(#bar_gradient_' + idx + ')');
                    }}
                }});
                
                console.log('Applied ' + gradientInfo.length + ' pie gradients and ' + barGradientInfo.length + ' bar gradients');
            }}, 200);
        }});
        
        Plotly.newPlot('tableChart', tableFig.data, tableFig.layout, {{responsive: true}});
        
        // Store original data for reset
        var originalMainFig = JSON.parse(JSON.stringify(mainFig));
        
        function downloadCSV() {{
            let csv = 'Rank,Archetype,Decks,Percentage,Per Tournament\\n';
            {json.dumps([{
                'rank': i,
                'name': format_archetype_name(arch) if arch else "Unknown",
                'count': count,
                'percentage': round((count / total_decks) * 100, 2),
                'per_tournament': round(count / len(tournaments), 1) if tournaments else 0
            } for i, (arch, count) in enumerate(sorted_archetypes, 1)])}
            .forEach(row => {{
                csv += `${{row.rank}},"${{row.name}}",${{row.count}},${{row.percentage}}%,${{row.per_tournament}}\\n`;
            }});
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manalytics_meta_' + new Date().toISOString().split('T')[0] + '.csv';
            a.click();
        }}
        
        function resetFilters() {{
            // Reset to original data
            Plotly.react('mainChart', originalMainFig.data, originalMainFig.layout);
        }}
        
        // Add click handler for pie chart filtering
        document.getElementById('mainChart').on('plotly_click', function(data) {{
            if (data.points[0].curveNumber === 0) {{ // Pie chart
                var clickedLabel = data.points[0].label;
                
                // Filter bar chart and timeline
                var newBarData = mainFig.data[1];
                var barIndices = [];
                newBarData.x.forEach((label, i) => {{
                    if (label === clickedLabel) {{
                        barIndices.push(i);
                    }}
                }});
                
                if (barIndices.length > 0) {{
                    // Highlight selected in bar chart
                    var colors = new Array(newBarData.x.length).fill('rgba(102, 126, 234, 0.3)');
                    barIndices.forEach(i => {{
                        colors[i] = 'rgba(102, 126, 234, 1)';
                    }});
                    
                    Plotly.restyle('mainChart', {{
                        'marker.color': [colors]
                    }}, [1]);
                    
                    // Filter timeline to show only selected archetype
                    var timelineTraces = [];
                    for (var i = 2; i < mainFig.data.length; i++) {{
                        if (mainFig.data[i].name === clickedLabel) {{
                            timelineTraces.push(i);
                        }}
                    }}
                    
                    // Update visibility
                    var visible = new Array(mainFig.data.length).fill(true);
                    for (var i = 2; i < mainFig.data.length; i++) {{
                        visible[i] = timelineTraces.includes(i);
                    }}
                    
                    Plotly.restyle('mainChart', 'visible', visible);
                }}
            }}
        }})
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_file = Path("data/cache/standard_analysis_no_leagues.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Plotly visualization created: {output_file}")
    print(f"📊 Processed {total_decks} decks from {len(tournaments)} tournaments")
    print(f"🎯 Top archetype: {format_archetype_name(sorted_archetypes[0][0])} with {sorted_archetypes[0][1]} decks ({percentages[0]}%)")
    
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


if __name__ == "__main__":
    create_plotly_visualization()