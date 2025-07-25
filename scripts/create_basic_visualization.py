#!/usr/bin/env python3
"""
Crée une visualisation HTML basique des archétypes sans leagues
Utilise Chart.js depuis CDN (pas besoin d'installer de modules)
"""

import json
from datetime import datetime
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("/Volumes/DataDisk/_Projects/Manalytics/data/cache")
OUTPUT_DIR.mkdir(exist_ok=True)

def create_html_visualization():
    """Crée une visualisation HTML des données sans leagues"""
    
    # Charger les données
    with open('archetype_data_no_leagues.json', 'r') as f:
        data = json.load(f)
    
    # Préparer les données pour les graphiques
    archetypes = [a['name'] for a in data['archetypes'][:15]]  # Top 15
    decks = [a['decks'] for a in data['archetypes'][:15]]
    percentages = [a['percentage'] for a in data['archetypes'][:15]]
    
    # Calculer les "Others"
    others_count = sum(a['decks'] for a in data['archetypes'][15:])
    if others_count > 0:
        archetypes.append('Others')
        decks.append(others_count)
        others_percentage = round(others_count / data['total_decks'] * 100, 2)
        percentages.append(others_percentage)
    
    # Créer le HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Standard Analysis (No Leagues)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
        }}
        .stat-box {{
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            min-width: 180px;
            text-align: center;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2.5em;
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
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .chart-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        canvas {{
            max-height: 400px;
        }}
        .table-container {{
            margin-top: 40px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .percentage-bar {{
            background-color: #667eea;
            height: 20px;
            border-radius: 3px;
            position: relative;
            overflow: hidden;
        }}
        .percentage-bar::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 2s infinite;
        }}
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        .timestamp {{
            text-align: center;
            color: #999;
            margin-top: 40px;
            font-size: 0.9em;
        }}
        .comparison {{
            margin-top: 30px;
            padding: 20px;
            background-color: #e8f4fd;
            border-radius: 10px;
            border-left: 4px solid #36A2EB;
        }}
        .comparison h3 {{
            margin-top: 0;
            color: #36A2EB;
        }}
        .diff-stat {{
            display: inline-block;
            margin-right: 20px;
            font-weight: 600;
        }}
        .positive {{ color: #4caf50; }}
        .negative {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Manalytics - Standard Analysis (Excluding Leagues)</h1>
        <div class="subtitle">Competitive Tournament Data Only - July 1-25, 2025</div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{data['total_tournaments']}</div>
                <div class="stat-label">Tournaments</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data['total_decks']}</div>
                <div class="stat-label">Total Decks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data['unique_archetypes']}</div>
                <div class="stat-label">Unique Archetypes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data['archetypes'][0]['percentage']:.1f}%</div>
                <div class="stat-label">Top Deck Share</div>
            </div>
        </div>
        
        <div class="comparison">
            <h3>📊 Analysis Without Leagues vs With Leagues</h3>
            <div>
                <span class="diff-stat">Tournaments: <span class="negative">41 vs 67 (-38.8%)</span></span>
                <span class="diff-stat">Total Decks: <span class="negative">624 vs 1,140 (-45.3%)</span></span>
                <span class="diff-stat">Data Quality: <span class="positive">Higher (Competitive Only)</span></span>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h2 class="chart-title">📊 Top 10 Archetypes Distribution</h2>
                <canvas id="pieChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">📈 Meta Share by Archetype</h2>
                <canvas id="barChart"></canvas>
            </div>
            
            <div class="chart-container full-width">
                <h2 class="chart-title">📉 All Archetypes - Horizontal View</h2>
                <canvas id="horizontalBarChart"></canvas>
            </div>
        </div>
        
        <div class="table-container">
            <h2 class="chart-title">📋 Detailed Archetype Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Archetype</th>
                        <th>Decks</th>
                        <th>Percentage</th>
                        <th>Visual Share</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Ajouter les lignes du tableau
    for i, archetype in enumerate(data['archetypes'][:20], 1):
        bar_width = archetype['percentage'] * 3  # Scale for visual
        html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{archetype['name']}</strong></td>
                        <td>{archetype['decks']}</td>
                        <td>{archetype['percentage']:.2f}%</td>
                        <td>
                            <div class="percentage-bar" style="width: {bar_width}px;"></div>
                        </td>
                    </tr>
"""
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="timestamp">
            Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Données pour les graphiques
        const archetypes = {json.dumps(archetypes[:10])};
        const decks = {json.dumps(decks[:10])};
        const percentages = {json.dumps(percentages[:10])};
        
        // Configuration commune
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
        
        // Pie Chart
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        new Chart(pieCtx, {{
            type: 'doughnut',
            data: {{
                labels: archetypes,
                datasets: [{{
                    data: decks,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 12
                            }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                label += context.parsed + ' decks';
                                label += ' (' + percentages[context.dataIndex] + '%)';
                                return label;
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Bar Chart
        const barCtx = document.getElementById('barChart').getContext('2d');
        new Chart(barCtx, {{
            type: 'bar',
            data: {{
                labels: archetypes,
                datasets: [{{
                    label: 'Number of Decks',
                    data: decks,
                    backgroundColor: '#667eea',
                    borderColor: '#5a5fbf',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            display: true,
                            color: '#f0f0f0'
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: false
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Horizontal Bar Chart (All archetypes)
        const allArchetypes = {json.dumps([a['name'] for a in data['archetypes']])};
        const allPercentages = {json.dumps([a['percentage'] for a in data['archetypes']])};
        
        const horizontalCtx = document.getElementById('horizontalBarChart').getContext('2d');
        new Chart(horizontalCtx, {{
            type: 'bar',
            data: {{
                labels: allArchetypes,
                datasets: [{{
                    label: 'Meta Share %',
                    data: allPercentages,
                    backgroundColor: '#764ba2',
                    borderColor: '#5a3a7e',
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
                        }},
                        grid: {{
                            display: true,
                            color: '#f0f0f0'
                        }}
                    }},
                    y: {{
                        grid: {{
                            display: false
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
                                return context.parsed.x + '%';
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
    
    # Sauvegarder le fichier
    output_file = OUTPUT_DIR / "standard_analysis_no_leagues.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Visualisation créée : {output_file}")
    print(f"📊 Statistiques :")
    print(f"   • Tournois : {data['total_tournaments']}")
    print(f"   • Decks : {data['total_decks']}")
    print(f"   • Archétypes : {data['unique_archetypes']}")
    print(f"   • Top deck : {data['archetypes'][0]['name']} ({data['archetypes'][0]['percentage']:.1f}%)")

if __name__ == "__main__":
    create_html_visualization()