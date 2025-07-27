#!/usr/bin/env python3
"""
Create Win Rate Mustache Graph - Jiliac Style Visualization
Shows win rates with confidence intervals for each archetype
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go
from scipy import stats
import numpy as np

def calculate_winrate_with_confidence(wins, total, confidence=0.95):
    """Calculate win rate with confidence interval using Wilson score interval."""
    if total == 0:
        return 0, 0, 0
    
    p_hat = wins / total
    z = stats.norm.ppf((1 + confidence) / 2)
    
    # Wilson score interval
    denominator = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denominator
    margin = z * np.sqrt(p_hat * (1 - p_hat) / total + z**2 / (4 * total**2)) / denominator
    
    lower = max(0, center - margin)
    upper = min(1, center + margin)
    
    return p_hat, lower, upper

def load_tournament_results():
    """Load tournament results and calculate win rates by archetype."""
    db_path = Path("/Volumes/DataDisk/_Projects/Manalytics/data/cache/tournaments.db")
    conn = sqlite3.connect(db_path)
    
    # Get all tournament results
    query = """
    SELECT t.id, t.date, t.tournament_name, t.json_file, t.format, t.source
    FROM tournaments t
    WHERE t.format = 'standard'
    AND t.tournament_name NOT LIKE '%League%'
    AND t.tournament_name NOT LIKE '%Mosh Pit%'
    AND t.tournament_name NOT LIKE '%Creative%'
    ORDER BY t.date DESC
    """
    
    cursor = conn.execute(query)
    tournaments = cursor.fetchall()
    
    archetype_stats = defaultdict(lambda: {'wins': 0, 'matches': 0, 'tournaments': set()})
    
    for tid, date, name, json_file, format_name, source in tournaments:
        # Load the full JSON to get bracket results
        json_path = Path("/Volumes/DataDisk/_Projects/Manalytics/data") / json_file
        if not json_path.exists():
            continue
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process bracket data to calculate wins/losses
        if 'Bracket' in data and isinstance(data['Bracket'], list):
            for match in data['Bracket']:
                if 'Player1' in match and 'Player2' in match:
                    p1_archetype = match['Player1'].get('Archetype', 'Unknown')
                    p2_archetype = match['Player2'].get('Archetype', 'Unknown')
                    
                    p1_wins = match['Player1'].get('Wins', 0)
                    p2_wins = match['Player2'].get('Wins', 0)
                    
                    if p1_archetype != 'Unknown':
                        archetype_stats[p1_archetype]['matches'] += 1
                        archetype_stats[p1_archetype]['wins'] += (1 if p1_wins > p2_wins else 0)
                        archetype_stats[p1_archetype]['tournaments'].add(tid)
                    
                    if p2_archetype != 'Unknown':
                        archetype_stats[p2_archetype]['matches'] += 1
                        archetype_stats[p2_archetype]['wins'] += (1 if p2_wins > p1_wins else 0)
                        archetype_stats[p2_archetype]['tournaments'].add(tid)
    
    conn.close()
    
    # Calculate win rates with confidence intervals
    results = []
    for archetype, stats in archetype_stats.items():
        if stats['matches'] >= 10:  # Minimum matches for statistical relevance
            winrate, lower, upper = calculate_winrate_with_confidence(stats['wins'], stats['matches'])
            results.append({
                'archetype': archetype,
                'winrate': winrate * 100,
                'lower': lower * 100,
                'upper': upper * 100,
                'matches': stats['matches'],
                'tournaments': len(stats['tournaments'])
            })
    
    # Sort by win rate
    results.sort(key=lambda x: x['winrate'], reverse=True)
    return results[:25]  # Top 25 archetypes

def create_mustache_graph(results):
    """Create the mustache graph visualization."""
    
    # Prepare data
    archetypes = [r['archetype'] for r in results]
    winrates = [r['winrate'] for r in results]
    lower_bounds = [r['lower'] for r in results]
    upper_bounds = [r['upper'] for r in results]
    matches = [r['matches'] for r in results]
    
    # Create the figure
    fig = go.Figure()
    
    # Add the mustache plot (error bars)
    fig.add_trace(go.Scatter(
        x=archetypes,
        y=winrates,
        mode='markers',
        marker=dict(
            size=12,
            color=winrates,
            colorscale='RdYlGn',
            cmin=40,
            cmax=60,
            showscale=True,
            colorbar=dict(title="Win Rate %")
        ),
        error_y=dict(
            type='data',
            symmetric=False,
            array=[u - w for u, w in zip(upper_bounds, winrates)],
            arrayminus=[w - l for w, l in zip(winrates, lower_bounds)],
            color='rgba(0,0,0,0.3)',
            thickness=2,
            width=8
        ),
        text=[f"{a}<br>Win Rate: {w:.1f}%<br>CI: [{l:.1f}%, {u:.1f}%]<br>Matches: {m}" 
              for a, w, l, u, m in zip(archetypes, winrates, lower_bounds, upper_bounds, matches)],
        hovertemplate='%{text}<extra></extra>',
        name='Win Rate'
    ))
    
    # Add 50% reference line
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title={
            'text': '🎯 Win Rate Mustache Graph - Archetype Performance with Confidence Intervals',
            'font': {'size': 24}
        },
        xaxis_title='Archetype',
        yaxis_title='Win Rate %',
        yaxis=dict(range=[30, 70]),
        height=600,
        showlegend=False,
        template='plotly_white',
        xaxis=dict(tickangle=-45)
    )
    
    return fig

def generate_html(fig, results):
    """Generate HTML with Jiliac-style visualization."""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Win Rate Mustache Graph - Manalytics</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
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
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .stats-grid {{
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
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .visualization-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .note {{
            background: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }}
        .export-btn {{
            background: white;
            color: #667eea;
            border: 2px solid white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }}
        .export-btn:hover {{
            background: transparent;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Win Rate Mustache Graph</h1>
        <p>Archetype Performance with Statistical Confidence Intervals</p>
        <button class="export-btn" onclick="exportToCSV()">📊 Export CSV</button>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">Archetypes Analyzed</div>
                <div class="stat-value">{len(results)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Best Win Rate</div>
                <div class="stat-value">{max(r['winrate'] for r in results):.1f}%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Average Win Rate</div>
                <div class="stat-value">{sum(r['winrate'] for r in results) / len(results):.1f}%</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Matches</div>
                <div class="stat-value">{sum(r['matches'] for r in results):,}</div>
            </div>
        </div>
        
        <div class="note">
            <strong>📊 How to read this graph:</strong> Each point shows an archetype's win rate. 
            The vertical lines (mustaches) show the 95% confidence interval - the true win rate 
            is likely within this range. Longer mustaches = less statistical certainty.
        </div>
        
        <div class="visualization-container">
            <div id="plotly-div"></div>
        </div>
        
        <div class="note">
            <strong>⚠️ Note:</strong> This analysis is based on bracket data only (Top 8). 
            Full round-by-round data from MTGO Listener will provide more accurate statistics.
        </div>
    </div>
    
    <script>
        var plotlyData = {fig.to_json()};
        Plotly.newPlot('plotly-div', plotlyData.data, plotlyData.layout, {{responsive: true}});
        
        function exportToCSV() {{
            const data = {json.dumps(results)};
            let csv = 'Archetype,Win Rate %,Lower Bound %,Upper Bound %,Matches,Tournaments\\n';
            data.forEach(row => {{
                csv += `"${{row.archetype}}",${{row.winrate.toFixed(2)}},${{row.lower.toFixed(2)}},${{row.upper.toFixed(2)}},${{row.matches}},${{row.tournaments}}\\n`;
            }});
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'winrate_mustache_data.csv';
            a.click();
        }}
    </script>
</body>
</html>"""
    
    return html_content

def main():
    print("🎯 Generating Win Rate Mustache Graph...")
    
    # Load and process data
    results = load_tournament_results()
    
    if not results:
        print("❌ No data found with sufficient matches")
        return
    
    # Create visualization
    fig = create_mustache_graph(results)
    
    # Generate HTML
    html_content = generate_html(fig, results)
    
    # Save file
    output_path = Path("/Volumes/DataDisk/_Projects/Manalytics/data/cache/winrate_mustache_graph.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Visualization saved to: {output_path}")
    print(f"📊 Analyzed {len(results)} archetypes")
    print(f"🎯 Best performer: {results[0]['archetype']} ({results[0]['winrate']:.1f}%)")

if __name__ == "__main__":
    main()