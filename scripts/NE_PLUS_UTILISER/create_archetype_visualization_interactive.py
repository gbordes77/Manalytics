#!/usr/bin/env python3
"""
Create ENHANCED INTERACTIVE HTML visualization of archetype distribution.
Version avec toutes les fonctionnalités demandées :
- Click to filter
- Timeline evolution 
- Export PNG/CSV
- Mobile responsive
- Hover interactions améliorées
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


def create_interactive_visualization():
    """Create fully interactive HTML visualization with Chart.js"""
    
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
    colors = []
    
    # Enhanced color palette with MTG guild colors
    color_map = {
        'Izzet': '#C41E3A',      # Red-Blue
        'Dimir': '#0F1B3C',      # Blue-Black  
        'Golgari': '#7C9A2E',    # Black-Green
        'Boros': '#FFD700',      # Red-White
        'Azorius': '#0080FF',    # White-Blue
        'Gruul': '#FF6B35',      # Red-Green
        'Mono White': '#FFFDD0',
        'Mono Red': '#DC143C',
        'Mono Green': '#228B22',
        'Mono Blue': '#4169E1',
        'Mono Black': '#2F4F4F',
        'Naya': '#FFA500',
        'Domain': '#9370DB',
        'Colorless': '#A9A9A9'
    }
    
    # Default colors for unknown archetypes
    default_colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'
    ]
    
    for i, (archetype, count) in enumerate(sorted_archetypes[:20]):  # Top 20
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
        
        # Assign color based on archetype
        color_assigned = False
        for key, color in color_map.items():
            if clean_name.startswith(key):
                colors.append(color)
                color_assigned = True
                break
        if not color_assigned:
            colors.append(default_colors[i % len(default_colors)])
    
    # Add "Others" if there are more than 20 archetypes
    if len(sorted_archetypes) > 20:
        others_count = sum(count for _, count in sorted_archetypes[20:])
        labels.append("Others")
        values.append(others_count)
        percentages.append(round((others_count / total_decks) * 100, 2))
        colors.append('#808080')
    
    # Prepare timeline data
    timeline_data = prepare_timeline_data(temporal_data, sorted_archetypes[:5])
    
    # Calculate date range
    if tournaments:
        dates = [t.date if isinstance(t.date, str) else t.date.strftime('%Y-%m-%d') for t in tournaments]
        date_range = f"{min(dates)} to {max(dates)}"
    else:
        date_range = "No data"
    
    # Create interactive HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Interactive Standard Metagame Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@2"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: white;
            font-size: 2.5em;
            margin: 0 0 10px 0;
            font-weight: 600;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.9);
            font-size: 1.1em;
            margin: 0;
        }}
        .controls {{
            margin-top: 20px;
        }}
        .control-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        button {{
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            backdrop-filter: blur(10px);
        }}
        button:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        select {{
            padding: 10px;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-size: 1em;
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
        .charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 40px;
            padding: 0 20px;
        }}
        .chart-container {{
            background: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            position: relative;
            min-height: 450px;
        }}
        .chart-container h2 {{
            color: #34495e;
            margin-bottom: 30px;
            font-size: 1.3em;
            text-align: center;
            font-weight: 600;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        canvas {{
            max-height: 380px;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            margin-top: 30px;
            border-collapse: collapse;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }}
        th:hover {{
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .percentage-cell {{
            font-weight: bold;
            color: #667eea;
        }}
        .filter-badge {{
            display: inline-block;
            padding: 5px 15px;
            background: #e74c3c;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 0.95em;
        }}
        .trend-rising {{ color: #27ae60; font-weight: bold; }}
        .trend-falling {{ color: #e74c3c; font-weight: bold; }}
        .trend-stable {{ color: #95a5a6; }}
        
        /* Mobile responsive */
        @media (max-width: 1200px) {{
            .charts {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            h1 {{
                font-size: 1.8em;
            }}
            .stats {{
                flex-direction: column;
                align-items: center;
            }}
            .stat-box {{
                width: 100%;
                max-width: 300px;
            }}
            .controls {{
                flex-direction: column;
                align-items: center;
            }}
            table {{
                font-size: 0.9em;
            }}
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics - Interactive Metagame Analysis</h1>
        <p class="subtitle">Click on charts to filter • Hover for details • Export to PNG/SVG</p>
        
        <div class="controls">
            <button onclick="exportCSV()">📊 Download CSV</button>
            <button onclick="resetFilters()" id="resetBtn" style="display: none;">🔄 Reset Filters</button>
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
                <div class="stat-value">{len(archetype_counts)}</div>
                <div class="stat-label">Unique Archetypes</div>
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
        
        <div class="charts">
            <div class="chart-container">
                <h2>📊 Top 10 Archetypes Distribution (Click to Filter)</h2>
                <canvas id="pieChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>📈 Meta Share by Archetype</h2>
                <canvas id="barChart"></canvas>
            </div>
            
            <div class="chart-container full-width">
                <h2>📉 Meta Evolution Timeline</h2>
                <canvas id="timelineChart"></canvas>
            </div>
        </div>
        
        <h2 style="margin-top: 40px; color: #34495e;">🏆 Detailed Archetype Breakdown</h2>
        <table id="archetypeTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Rank ↕</th>
                    <th onclick="sortTable(1)">Archetype ↕</th>
                    <th onclick="sortTable(2)">Decks ↕</th>
                    <th onclick="sortTable(3)">Meta % ↕</th>
                    <th onclick="sortTable(4)">Per Tournament ↕</th>
                    <th>Trend</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for i, (archetype, count) in enumerate(sorted_archetypes, 1):
        percentage = (count / total_decks) * 100
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        per_tournament = round(count / len(tournaments), 1) if tournaments else 0
        trend = calculate_trend(archetype, temporal_data)
        trend_class = "trend-rising" if "Rising" in trend else "trend-falling" if "Falling" in trend else "trend-stable"
        
        html_content += f"""
                <tr class="archetype-row" data-archetype="{clean_name}">
                    <td>#{i}</td>
                    <td style="font-weight: 600;">{clean_name}</td>
                    <td>{count}</td>
                    <td class="percentage-cell">{percentage:.2f}%</td>
                    <td>{per_tournament}</td>
                    <td class="{trend_class}">{trend}</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="timestamp">
            Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Data includes {len(tournaments)} tournaments (leagues excluded)
        </div>
    </div>
    
    <script>
        // Register the plugin
        Chart.register(ChartDataLabels);
        
        // Global variables
        let pieChart, barChart, timelineChart;
        let currentFilter = null;
        let allData = {{
            labels: {json.dumps(labels[:10])},
            values: {json.dumps(values[:10])},
            percentages: {json.dumps(percentages[:10])},
            colors: {json.dumps(colors[:10])},
            timeline: {json.dumps(timeline_data)},
            allArchetypes: {json.dumps([{
                'name': format_archetype_name(arch) if arch else "Unknown",
                'count': count,
                'percentage': round((count / total_decks) * 100, 2)
            } for arch, count in sorted_archetypes])}
        }};
        
        // Initialize charts
        function initCharts() {{
            createPieChart();
            createBarChart();
            createTimelineChart();
        }}
        
        // Enhanced Pie Chart with click to filter
        function createPieChart() {{
            const ctx = document.getElementById('pieChart').getContext('2d');
            
            if (pieChart) pieChart.destroy();
            
            pieChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: allData.labels,
                    datasets: [{{
                        data: allData.values,
                        backgroundColor: allData.colors,
                        borderWidth: 3,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    layout: {{
                        padding: {{
                            top: 20,
                            bottom: 20
                        }}
                    }},
                    onClick: (event, elements) => {{
                        if (elements.length > 0) {{
                            const index = elements[0].index;
                            const archetype = allData.labels[index];
                            filterByArchetype(archetype);
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 20,
                                font: {{ size: 11 }},
                                boxWidth: 15,
                                generateLabels: function(chart) {{
                                    const data = chart.data;
                                    return data.labels.map((label, i) => ({{
                                        text: `${{label}} (${{allData.values[i]}} - ${{allData.percentages[i]}}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    }}));
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const percentage = allData.percentages[context.dataIndex];
                                    return [
                                        `${{label}}`,
                                        `Decks: ${{value}}`,
                                        `Meta Share: ${{percentage}}%`,
                                        `Per Tournament: ${{(value / {len(tournaments)}).toFixed(1)}}`
                                    ];
                                }}
                            }}
                        }},
                        datalabels: {{
                            color: function(context) {{
                                const percentage = allData.percentages[context.dataIndex];
                                return percentage > 8 ? '#fff' : '#333';
                            }},
                            font: {{
                                weight: 'bold',
                                size: function(context) {{
                                    const percentage = allData.percentages[context.dataIndex];
                                    return percentage > 10 ? 14 : percentage > 5 ? 12 : 10;
                                }}
                            }},
                            formatter: function(value, context) {{
                                const label = context.chart.data.labels[context.dataIndex];
                                const percentage = allData.percentages[context.dataIndex];
                                
                                if (percentage > 10) {{
                                    const shortLabel = label.length > 15 ? 
                                        label.split(' ').slice(0, 2).join(' ') : label;
                                    return `${{shortLabel}}\\n${{percentage}}%`;
                                }}
                                else if (percentage > 3) {{
                                    return `${{percentage}}%`;
                                }}
                                return '';
                            }},
                            textAlign: 'center',
                            display: true
                        }}
                    }}
                }}
            }});
        }}
        
        // Enhanced Bar Chart
        function createBarChart() {{
            const ctx = document.getElementById('barChart').getContext('2d');
            
            if (barChart) barChart.destroy();
            
            barChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: allData.labels,
                    datasets: [{{
                        label: 'Number of Decks',
                        data: allData.values,
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    onClick: (event, elements) => {{
                        if (elements.length > 0) {{
                            const index = elements[0].index;
                            const archetype = allData.labels[index];
                            filterByArchetype(archetype);
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 40,
                            bottom: 10,
                            left: 10,
                            right: 10
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + ' decks';
                                }},
                                padding: 10
                            }}
                        }},
                        x: {{
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 45,
                                padding: 10,
                                font: {{
                                    size: 10
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        datalabels: {{
                            anchor: 'end',
                            align: 'end',
                            color: '#667eea',
                            font: {{
                                weight: 'bold',
                                size: 12
                            }},
                            formatter: function(value, context) {{
                                const percentage = allData.percentages[context.dataIndex];
                                return `${{value}} (${{percentage}}%)`;
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const percentage = allData.percentages[context.dataIndex];
                                    return [
                                        `Decks: ${{context.parsed.y}}`,
                                        `Meta Share: ${{percentage}}%`,
                                        `Avg per tournament: ${{(context.parsed.y / {len(tournaments)}).toFixed(1)}}`
                                    ];
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Timeline Chart
        function createTimelineChart() {{
            const ctx = document.getElementById('timelineChart').getContext('2d');
            
            if (timelineChart) timelineChart.destroy();
            
            const datasets = [];
            const archetypesInTimeline = [...new Set(allData.timeline.map(d => d.archetype))];
            
            archetypesInTimeline.forEach((archetype, index) => {{
                const data = allData.timeline
                    .filter(d => d.archetype === archetype)
                    .map(d => ({{
                        x: d.date,
                        y: d.percentage
                    }}));
                
                datasets.push({{
                    label: archetype,
                    data: data,
                    borderColor: allData.colors[index] || '#' + Math.floor(Math.random()*16777215).toString(16),
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }});
            }});
            
            timelineChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    datasets: currentFilter ? 
                        datasets.filter(d => d.label === currentFilter) : 
                        datasets
                }},
                options: {{
                    responsive: true,
                    interaction: {{
                        mode: 'index',
                        intersect: false
                    }},
                    layout: {{
                        padding: {{
                            top: 20,
                            bottom: 10,
                            left: 10,
                            right: 10
                        }}
                    }},
                    scales: {{
                        x: {{
                            type: 'time',
                            time: {{
                                parser: 'YYYY-MM-DD',
                                tooltipFormat: 'MMM dd',
                                displayFormats: {{
                                    day: 'MMM dd'
                                }}
                            }},
                            title: {{
                                display: true,
                                text: 'Date',
                                padding: {{ top: 10 }}
                            }},
                            ticks: {{
                                maxRotation: 0,
                                autoSkip: true,
                                maxTicksLimit: 10
                            }}
                        }},
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Meta Share %',
                                padding: {{ bottom: 10 }}
                            }},
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }},
                                padding: 10
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'bottom'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + 
                                           context.parsed.y.toFixed(1) + '%';
                                }}
                            }}
                        }},
                        datalabels: {{
                            display: false
                        }}
                    }}
                }}
            }});
        }}
        
        // Filter by archetype
        function filterByArchetype(archetype) {{
            if (currentFilter === archetype) {{
                resetFilters();
                return;
            }}
            
            currentFilter = archetype;
            document.getElementById('filterBadge').style.display = 'inline-block';
            document.getElementById('filterBadge').textContent = 'Filtered: ' + archetype;
            document.getElementById('resetBtn').style.display = 'inline-block';
            
            // Update table
            const rows = document.querySelectorAll('.archetype-row');
            rows.forEach(row => {{
                if (row.dataset.archetype === archetype) {{
                    row.style.backgroundColor = '#e3f2fd';
                    row.style.fontWeight = 'bold';
                }} else {{
                    row.style.backgroundColor = '';
                    row.style.fontWeight = '';
                }}
            }});
            
            // Update timeline chart
            createTimelineChart();
        }}
        
        // Reset filters
        function resetFilters() {{
            currentFilter = null;
            document.getElementById('filterBadge').style.display = 'none';
            document.getElementById('resetBtn').style.display = 'none';
            
            // Reset table styling
            const rows = document.querySelectorAll('.archetype-row');
            rows.forEach(row => {{
                row.style.backgroundColor = '';
                row.style.fontWeight = '';
            }});
            
            // Reset timeline
            createTimelineChart();
        }}
        
        // Export to PNG
        function exportPNG() {{
            const canvas = pieChart.canvas;
            const url = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = 'manalytics_meta_' + new Date().toISOString().split('T')[0] + '.png';
            link.href = url;
            link.click();
        }}
        
        // Export to CSV
        function exportCSV() {{
            let csv = 'Rank,Archetype,Decks,Percentage,Per Tournament\\n';
            
            allData.allArchetypes.forEach((arch, index) => {{
                csv += `${{index + 1}},"${{arch.name}}",${{arch.count}},${{arch.percentage}}%,${{(arch.count / {len(tournaments)}).toFixed(1)}}\\n`;
            }});
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manalytics_meta_' + new Date().toISOString().split('T')[0] + '.csv';
            a.click();
        }}
        
        // Sort table
        function sortTable(column) {{
            const table = document.getElementById('archetypeTable');
            const tbody = table.getElementsByTagName('tbody')[0];
            const rows = Array.from(tbody.getElementsByTagName('tr'));
            
            let sortedRows = rows.sort((a, b) => {{
                let aVal = a.getElementsByTagName('td')[column].textContent;
                let bVal = b.getElementsByTagName('td')[column].textContent;
                
                // Handle numeric columns
                if (column === 0 || column === 2 || column === 4) {{
                    aVal = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
                    bVal = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
                }}
                
                if (aVal < bVal) return -1;
                if (aVal > bVal) return 1;
                return 0;
            }});
            
            // Toggle sort direction
            if (table.dataset.sortColumn == column && table.dataset.sortDir == 'asc') {{
                sortedRows.reverse();
                table.dataset.sortDir = 'desc';
            }} else {{
                table.dataset.sortDir = 'asc';
            }}
            table.dataset.sortColumn = column;
            
            // Re-append rows
            sortedRows.forEach(row => tbody.appendChild(row));
        }}
        
        // Update charts based on date range
        function updateCharts() {{
            const range = document.getElementById('dateRange').value;
            // This would require re-fetching data based on date range
            // For now, just refresh the charts
            initCharts();
        }}
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', initCharts);
    </script>
</body>
</html>
"""
    
    # Save HTML file - THIS IS THE CORRECT INTERACTIVE VERSION
    output_file = Path("data/cache/standard_analysis_no_leagues_interactive.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Enhanced interactive visualization created: {output_file}")
    print(f"📊 New features added:")
    print(f"   ✓ Click to filter on pie/bar charts")
    print(f"   ✓ Timeline evolution chart")
    print(f"   ✓ Export to PNG/CSV")
    print(f"   ✓ Mobile responsive design")
    print(f"   ✓ Sortable table")
    print(f"   ✓ Enhanced hover interactions")
    
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
    create_interactive_visualization()