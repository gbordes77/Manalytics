#!/usr/bin/env python3
"""
Create PLOTLY HTML visualization with WORKING gradients in table.
Based on the version that successfully showed gradients in the table.
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
from src.utils.mtg_colors import get_archetype_colors, MTG_COLORS

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_plotly_visualization():
    """Create interactive HTML visualization with working gradients"""
    
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
    
    # Prepare chart data
    labels = []
    values = []
    percentages = []
    raw_archetypes = []
    
    # Only show archetypes above 1.5%
    for archetype, count in filtered_archetypes:
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
        raw_archetypes.append(archetype)
    
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
        subplot_titles=("📊 Meta Distribution", 
                       "📈 Top Archetypes",
                       "📉 Meta Evolution Timeline (Last 30 Days)"),
        vertical_spacing=0.25,
        horizontal_spacing=0.20
    )
    
    # Get colors for all archetypes
    pie_colors = []
    bar_colors = []
    gradient_info = []
    
    for i, label in enumerate(labels):
        arch_colors = get_archetype_colors(label)
        # Use first color for base
        base_color = MTG_COLORS[arch_colors[0]]
        pie_colors.append(base_color)
        bar_colors.append(base_color)
        
        # Store gradient info for multi-color archetypes
        if len(arch_colors) > 1:
            gradient_info.append({
                'index': i,
                'label': label,
                'colors': arch_colors,
                'hex_colors': [MTG_COLORS[c] for c in arch_colors]
            })
    
    # 1. Pie Chart
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0,
            marker=dict(
                colors=pie_colors,
                line=dict(color='white', width=2)
            ),
            textposition='outside',
            textinfo='label+text',
            text=[f'{p}%' for p in percentages],
            customdata=percentages,
            hovertemplate='<b>%{label}</b><br>' +
                         'Decks: %{value}<br>' +
                         'Meta Share: %{customdata}%<br>' +
                         '<extra></extra>',
            insidetextorientation='radial'
        ),
        row=1, col=1
    )
    
    # 2. Bar Chart
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color=bar_colors,
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f"{v} ({p}%)" for v, p in zip(values, percentages)],
            textposition='outside',
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Decks: %{y}<br>Meta Share: %{text}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Timeline Chart
    timeline_data = prepare_timeline_data(temporal_data, filtered_archetypes[:5])
    
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
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'🎯 Manalytics - Interactive Standard Metagame Analysis<br>' +
                   f'<sub>Tournaments Only (Leagues Excluded) - {datetime.now().strftime("%B %d, %Y")}</sub>',
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
    
    # Update axes
    fig.update_xaxes(tickangle=-45, row=1, col=2, showgrid=False)
    fig.update_yaxes(title_text="Number of Decks", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Meta Share %", row=2, col=1)
    
    # Create table data WITH gradient styling
    table_data = []
    row_fills = []  # For Plotly table fills
    
    for i, (archetype, count) in enumerate(filtered_archetypes, 1):
        percentage = (count / total_decks) * 100
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        per_tournament = round(count / len(tournaments), 1) if tournaments else 0
        trend = calculate_trend(archetype, temporal_data)
        
        # Get colors for gradient
        arch_colors = get_archetype_colors(clean_name)
        
        table_data.append({
            'Rank': f'#{i}',
            'Archetype': clean_name,
            'Decks': count,
            'Meta %': f'{percentage:.2f}%',
            'Avg/Tournament': per_tournament,
            'Trend': trend,
            'colors': arch_colors  # Store for later use
        })
    
    # Create custom fill colors for each row based on archetype colors
    fill_colors = []
    for row in table_data:
        arch_colors = row['colors']
        if len(arch_colors) == 1:
            # Single color - use light version with rgba
            hex_color = MTG_COLORS[arch_colors[0]]
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            fill_colors.append(f'rgba({r},{g},{b},0.13)')
        else:
            # Multi-color - use primary color with higher opacity
            hex_color = MTG_COLORS[arch_colors[0]]
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            fill_colors.append(f'rgba({r},{g},{b},0.27)')
    
    # Create table with row-based coloring
    table_fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Rank', 'Archetype', 'Decks', 'Meta %', 'Avg/Tournament', 'Trend'],
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
            fill_color=[fill_colors] * 6,  # Apply same colors to all columns
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
    
    # Create HTML with gradient CSS
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
        
        /* Table gradient styles */
        .gradient-row {{
            position: relative;
            overflow: hidden;
        }}
        .gradient-row::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.3;
            pointer-events: none;
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
        
        // Gradient info for visualizations
        var gradientInfo = {json.dumps(gradient_info)};
        
        // Table data with colors
        var tableColorData = {json.dumps([{
            'label': d['Archetype'],
            'colors': d['colors']
        } for d in table_data])};
        
        // MTG colors
        var mtgColors = {{
            'W': '#FFFBD5',
            'U': '#0E68AB',
            'B': '#1C1C1C',
            'R': '#F44336',
            'G': '#4CAF50',
            'C': '#9E9E9E'
        }};
        
        Plotly.newPlot('mainChart', mainFig.data, mainFig.layout, {{responsive: true}}).then(function(gd) {{
            // Apply gradients to pie and bar charts
            setTimeout(function() {{
                var svg = gd.querySelector('.main-svg');
                if (!svg) return;
                
                // Create defs for gradients
                var defs = svg.querySelector('defs') || svg.insertBefore(document.createElementNS('http://www.w3.org/2000/svg', 'defs'), svg.firstChild);
                
                // Add gradient definitions
                gradientInfo.forEach(function(info) {{
                    // Radial gradient for pie
                    var radialGrad = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
                    radialGrad.setAttribute('id', 'pie_grad_' + info.index);
                    
                    info.hex_colors.forEach(function(color, i) {{
                        var stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                        stop.setAttribute('offset', (i / (info.hex_colors.length - 1) * 100) + '%');
                        stop.setAttribute('stop-color', color);
                        radialGrad.appendChild(stop);
                    }});
                    defs.appendChild(radialGrad);
                    
                    // Linear gradient for bars
                    var linearGrad = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                    linearGrad.setAttribute('id', 'bar_grad_' + info.index);
                    linearGrad.setAttribute('x1', '0%');
                    linearGrad.setAttribute('y1', '100%');
                    linearGrad.setAttribute('x2', '0%');
                    linearGrad.setAttribute('y2', '0%');
                    
                    info.hex_colors.forEach(function(color, i) {{
                        var stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                        stop.setAttribute('offset', (i / (info.hex_colors.length - 1) * 100) + '%');
                        stop.setAttribute('stop-color', color);
                        linearGrad.appendChild(stop);
                    }});
                    defs.appendChild(linearGrad);
                }});
                
                // Apply to pie slices
                var pieSlices = gd.querySelectorAll('.pielayer .slice path');
                gradientInfo.forEach(function(info) {{
                    if (pieSlices[info.index]) {{
                        pieSlices[info.index].style.fill = 'url(#pie_grad_' + info.index + ')';
                    }}
                }});
                
                // Apply to bars
                var bars = gd.querySelectorAll('.barlayer .points .point path');
                gradientInfo.forEach(function(info) {{
                    if (bars[info.index]) {{
                        bars[info.index].style.fill = 'url(#bar_grad_' + info.index + ')';
                    }}
                }});
            }}, 200);
        }});
        
        Plotly.newPlot('tableChart', tableFig.data, tableFig.layout, {{responsive: true}}).then(function(gd) {{
            // Apply gradient backgrounds to table rows
            setTimeout(function() {{
                // For each row with multi-color archetype, create CSS gradient
                var style = document.createElement('style');
                var css = '';
                
                tableColorData.forEach(function(data, i) {{
                    if (data.colors.length > 1) {{
                        var colors = data.colors.map(function(c) {{ return mtgColors[c]; }});
                        css += `
                            .table-row-${{i}} {{
                                background: linear-gradient(90deg, ${{colors.join(', ')}}) !important;
                            }}
                        `;
                    }}
                }});
                
                style.textContent = css;
                document.head.appendChild(style);
                
                // Apply classes to SVG elements
                var cells = gd.querySelectorAll('.table .cells rect');
                var cellsPerRow = 6;
                
                cells.forEach(function(cell, idx) {{
                    var rowIdx = Math.floor(idx / cellsPerRow);
                    var data = tableColorData[rowIdx];
                    
                    if (data && data.colors.length > 1) {{
                        // For multi-color rows, create gradient overlay
                        var parent = cell.parentNode;
                        var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                        rect.setAttribute('x', cell.getAttribute('x'));
                        rect.setAttribute('y', cell.getAttribute('y'));
                        rect.setAttribute('width', cell.getAttribute('width'));
                        rect.setAttribute('height', cell.getAttribute('height'));
                        
                        // Create gradient
                        var gradId = 'table_grad_' + rowIdx + '_' + idx;
                        var grad = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                        grad.setAttribute('id', gradId);
                        grad.setAttribute('x1', '0%');
                        grad.setAttribute('x2', '100%');
                        
                        data.colors.forEach(function(c, i) {{
                            var stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                            stop.setAttribute('offset', (i / (data.colors.length - 1) * 100) + '%');
                            stop.setAttribute('stop-color', mtgColors[c]);
                            stop.setAttribute('stop-opacity', '0.3');
                            grad.appendChild(stop);
                        }});
                        
                        var svg = gd.querySelector('svg');
                        var defs = svg.querySelector('defs') || svg.insertBefore(document.createElementNS('http://www.w3.org/2000/svg', 'defs'), svg.firstChild);
                        defs.appendChild(grad);
                        
                        rect.setAttribute('fill', 'url(#' + gradId + ')');
                        parent.appendChild(rect);
                    }}
                }});
                
                console.log('Table gradients applied');
            }}, 200);
        }});
        
        // Store original data
        var originalMainFig = JSON.parse(JSON.stringify(mainFig));
        
        function downloadCSV() {{
            let csv = 'Rank,Archetype,Decks,Percentage,Per Tournament\\n';
            {json.dumps([{
                'rank': i,
                'name': format_archetype_name(arch) if arch else "Unknown",
                'count': count,
                'percentage': round((count / total_decks) * 100, 2),
                'per_tournament': round(count / len(tournaments), 1) if tournaments else 0
            } for i, (arch, count) in enumerate(filtered_archetypes, 1)])}
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
            Plotly.react('mainChart', originalMainFig.data, originalMainFig.layout);
        }}
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_file = Path("data/cache/standard_analysis_no_leagues.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Plotly visualization with table gradients created: {output_file}")
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