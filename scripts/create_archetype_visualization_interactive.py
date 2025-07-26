#!/usr/bin/env python3
"""
Create HTML visualization of archetype distribution.
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
    """Create HTML visualization with bar chart and pie chart"""
    
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
    
    # Colors for charts
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384',
        '#36A2EB', '#FFCE56', '#FF9F40', '#9966FF', '#C9CBCF',
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#808080'  # Gray for "Others"
    ]
    
    # Create HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Standard Archetype Distribution</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }}
        .stat-box {{
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            min-width: 150px;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #36A2EB;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }}
        .chart-container {{
            position: relative;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        canvas {{
            max-height: 400px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            margin-top: 30px;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #36A2EB;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Manalytics - Standard Archetype Distribution</h1>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(tournaments)}</div>
                <div class="stat-label">Tournaments</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_decks}</div>
                <div class="stat-label">Total Decks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(archetype_counts)}</div>
                <div class="stat-label">Unique Archetypes</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h2>Pie Chart - Archetype Distribution</h2>
                <canvas id="pieChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2>Top 10 Archetypes</h2>
                <canvas id="barChart"></canvas>
            </div>
            
            <div class="chart-container full-width">
                <h2>All Archetypes - Horizontal Bar Chart</h2>
                <canvas id="horizontalBarChart"></canvas>
            </div>
        </div>
        
        <h2>Detailed Archetype Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Archetype</th>
                    <th>Decks</th>
                    <th>Percentage</th>
                    <th>Meta Share</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for i, (archetype, count) in enumerate(sorted_archetypes, 1):
        percentage = (count / total_decks) * 100
        bar_width = min(percentage * 3, 100)  # Scale for visual representation
        clean_name = format_archetype_name(archetype) if archetype else "Unknown"
        html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td>{clean_name}</td>
                    <td>{count}</td>
                    <td>{percentage:.2f}%</td>
                    <td>
                        <div style="width: {bar_width}px; height: 20px; background-color: #36A2EB; border-radius: 3px;"></div>
                    </td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="timestamp">
            Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Pie Chart
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        new Chart(pieCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    data: {json.dumps(values)},
                    backgroundColor: {json.dumps(colors[:len(labels)])},
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'right',
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                label += context.parsed + ' decks';
                                label += ' (' + {json.dumps(percentages)}[context.dataIndex] + '%)';
                                return label;
                            }}
                        }}
                    }},
                    datalabels: {{
                        color: '#fff',
                        font: {{
                            weight: 'bold',
                            size: 11
                        }},
                        formatter: function(value, context) {{
                            let label = context.chart.data.labels[context.dataIndex];
                            let percentage = {json.dumps(percentages)}[context.dataIndex];
                            // Only show label if percentage > 2%
                            if (percentage > 2) {{
                                return label + '\\n' + percentage + '%';
                            }}
                            return percentage > 1 ? percentage + '%' : '';
                        }}
                    }}
                }}
            }}
        }});
        
        // Bar Chart (Top 10)
        const barCtx = document.getElementById('barChart').getContext('2d');
        new Chart(barCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels[:10])},
                datasets: [{{
                    label: 'Number of Decks',
                    data: {json.dumps(values[:10])},
                    backgroundColor: '#36A2EB',
                    borderColor: '#2E86DE',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Horizontal Bar Chart (All)
        const horizontalCtx = document.getElementById('horizontalBarChart').getContext('2d');
        new Chart(horizontalCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Percentage of Meta',
                    data: {json.dumps(percentages)},
                    backgroundColor: '#FF6384',
                    borderColor: '#FF4F70',
                    borderWidth: 1
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                scales: {{
                    x: {{
                        beginAtZero: true,
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
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.x + '% (' + {json.dumps(values)}[context.dataIndex] + ' decks)';
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
    output_file = Path("data/cache/standard_analysis_no_leagues_interactive.html")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Visualization created: {output_file}")
    return output_file


if __name__ == "__main__":
    create_visualization_html()