#!/usr/bin/env python3
"""
Create ENHANCED HTML visualization of archetype distribution.
- Pie chart with archetype names INSIDE each slice
- Percentages EVERYWHERE
- More visual appeal
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.cache.reader import CacheReader
from src.cache.database import CacheDatabase
from src.utils.color_names import format_archetype_name


def create_visualization_html():
    """Create ENHANCED HTML visualization with better charts"""
    
    # Get meta snapshot
    reader = CacheReader()
    meta_snapshot = reader.get_meta_snapshot("standard", datetime.now())
    
    # Get database stats
    db = CacheDatabase()
    tournaments = db.get_tournaments_by_format("standard")
    
    # Filter out leagues
    tournaments = [t for t in tournaments if 'league' not in t.type.lower()]
    
    # Prepare data for visualization
    archetypes = meta_snapshot['archetypes']
    total_decks = meta_snapshot['total_decks']
    
    # Extract counts from archetype data (handle both dict and int formats)
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
    
    for archetype, count in sorted_archetypes[:20]:  # Top 20 for readability
        # Clean up archetype names
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        labels.append(clean_name)
        values.append(count)
        percentages.append(round((count / total_decks) * 100, 2))
    
    # Add "Others" if there are more than 20 archetypes
    if len(sorted_archetypes) > 20:
        others_count = sum(count for _, count in sorted_archetypes[20:])
        labels.append("Others")
        values.append(others_count)
        percentages.append(round((others_count / total_decks) * 100, 2))
    
    # Enhanced color palette
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1F2', '#F8B195',
        '#C7CEEA', '#FFDAB9', '#E8DAEF', '#D5DBDB', '#FADBD8',
        '#808080'  # Gray for "Others"
    ]
    
    # Create HTML with enhanced styling
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Enhanced Standard Metagame Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .stat-box {{
            padding: 20px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            min-width: 200px;
            text-align: center;
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        .stat-box:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 40px;
        }}
        .chart-container {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .chart-container h2 {{
            color: #34495e;
            margin-bottom: 20px;
            font-size: 1.4em;
            text-align: center;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        canvas {{
            max-height: 400px;
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
        .meta-bar {{
            height: 25px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 0.95em;
        }}
        @media (max-width: 1200px) {{
            .charts {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Manalytics - Enhanced Standard Metagame Analysis</h1>
        <p class="subtitle">Tournaments Only (Leagues Excluded) - {datetime.now().strftime('%B %d, %Y')}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(tournaments)}</div>
                <div class="stat-label">Tournaments Analyzed</div>
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
                <div class="stat-value">{sorted_archetypes[0][1] if sorted_archetypes else 0}</div>
                <div class="stat-label">Top Deck Count</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h2>📊 Top 10 Archetypes Distribution</h2>
                <canvas id="pieChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>📈 Meta Share by Archetype</h2>
                <canvas id="barChart"></canvas>
            </div>
            
            <div class="chart-container full-width">
                <h2>📋 All Archetypes - Horizontal View</h2>
                <canvas id="horizontalBarChart"></canvas>
            </div>
        </div>
        
        <h2 style="margin-top: 40px; color: #34495e;">🏆 Detailed Archetype Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Archetype</th>
                    <th>Decks</th>
                    <th>Meta %</th>
                    <th>Visual Share</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add enhanced table rows
    for i, (archetype, count) in enumerate(sorted_archetypes, 1):
        percentage = (count / total_decks) * 100
        bar_width = min(percentage * 4, 100)  # Scale for visual representation
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        
        # Determine tier
        tier_class = ""
        if percentage > 15:
            tier_class = "tier-1"
        elif percentage > 8:
            tier_class = "tier-2"
        elif percentage > 3:
            tier_class = "tier-3"
        
        html_content += f"""
                <tr>
                    <td style="font-weight: bold;">#{i}</td>
                    <td style="font-weight: 600;">{clean_name}</td>
                    <td>{count} <span style="color: #95a5a6;">({round(count/len(tournaments), 1)} per tournament)</span></td>
                    <td class="percentage-cell">{percentage:.2f}%</td>
                    <td style="width: 40%;">
                        <div class="meta-bar" style="width: {bar_width}%;">
                            {percentage:.1f}%
                        </div>
                    </td>
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
        
        // Enhanced Pie Chart with labels inside
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        new Chart(pieCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(labels[:10])},
                datasets: [{{
                    data: {json.dumps(values[:10])},
                    backgroundColor: {json.dumps(colors[:10])},
                    borderWidth: 3,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 12
                            }},
                            generateLabels: function(chart) {{
                                const data = chart.data;
                                return data.labels.map((label, i) => ({{
                                    text: `${{label}} (${{data.datasets[0].data[i]}} - ${{{json.dumps(percentages[:10])}[i]}}%)`,
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
                                let label = context.label || '';
                                const value = context.parsed;
                                const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
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
                            const value = context.dataset.data[context.dataIndex];
                            const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
                            return percentage > 8 ? '#fff' : '#333';
                        }},
                        font: {{
                            weight: 'bold',
                            size: function(context) {{
                                const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
                                return percentage > 10 ? 14 : percentage > 5 ? 12 : 10;
                            }}
                        }},
                        formatter: function(value, context) {{
                            const label = context.chart.data.labels[context.dataIndex];
                            const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
                            
                            // For large slices, show name + percentage
                            if (percentage > 10) {{
                                const shortLabel = label.length > 15 ? 
                                    label.split(' ').slice(0, 2).join(' ') : label;
                                return `${{shortLabel}}\\n${{percentage}}%`;
                            }}
                            // For medium slices, show percentage only
                            else if (percentage > 3) {{
                                return `${{percentage}}%`;
                            }}
                            // For small slices, show nothing (legend handles it)
                            return '';
                        }},
                        textAlign: 'center',
                        display: true
                    }}
                }}
            }}
        }});
        
        // Enhanced Bar Chart with percentages on top
        const barCtx = document.getElementById('barChart').getContext('2d');
        new Chart(barCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels[:10])},
                datasets: [{{
                    label: 'Number of Decks',
                    data: {json.dumps(values[:10])},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return value + ' decks';
                            }}
                        }}
                    }},
                    x: {{
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 45
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
                            const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
                            return `${{value}} (${{percentage}}%)`;
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const percentage = {json.dumps(percentages[:10])}[context.dataIndex];
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
        
        // Enhanced Horizontal Bar Chart for all archetypes
        const horizontalCtx = document.getElementById('horizontalBarChart').getContext('2d');
        new Chart(horizontalCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Meta Share %',
                    data: {json.dumps(percentages)},
                    backgroundColor: function(context) {{
                        const value = context.parsed.x;
                        if (value > 15) return '#FF6384';
                        if (value > 8) return '#FFA07A';
                        if (value > 3) return '#FFCE56';
                        return '#C9CBCF';
                    }},
                    borderWidth: 0
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                scales: {{
                    x: {{
                        beginAtZero: true,
                        max: Math.max(...{json.dumps(percentages)}) * 1.2,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
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
                        align: 'right',
                        color: '#333',
                        font: {{
                            weight: 'bold',
                            size: 10
                        }},
                        formatter: function(value, context) {{
                            const count = {json.dumps(values)}[context.dataIndex];
                            return `${{value}}% (${{count}} decks)`;
                        }},
                        padding: 4
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const count = {json.dumps(values)}[context.dataIndex];
                                return [
                                    `Meta Share: ${{context.parsed.x}}%`,
                                    `Total Decks: ${{count}}`,
                                    `Per Tournament: ${{(count / {len(tournaments)}).toFixed(1)}}`
                                ];
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_file = Path("data/cache/standard_analysis_no_leagues.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Enhanced visualization created: {output_file}")
    print(f"📊 Processed {total_decks} decks from {len(tournaments)} tournaments")
    print(f"🎯 Top archetype: {format_archetype_name(sorted_archetypes[0][0])} with {sorted_archetypes[0][1]} decks ({percentages[0]}%)")
    
    return output_file


if __name__ == "__main__":
    create_visualization_html()