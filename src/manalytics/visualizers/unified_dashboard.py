"""
Unified Dashboard - Combines all Plotly visualizations with the standard template.

This module creates a unified dashboard following the Manalytics visual template
with all advanced Plotly visualizations integrated.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class UnifiedDashboard:
    """Creates a unified dashboard with all visualizations following the template"""
    
    def __init__(self):
        self.template_style = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .header h1 {
                margin: 10px 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .header p {
                margin: 5px 0;
                opacity: 0.9;
                font-size: 1.1em;
            }
            .navigation {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .nav-btn {
                padding: 10px 20px;
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s;
                text-decoration: none;
            }
            .nav-btn:hover {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .nav-btn.active {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .visualization-container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                padding: 20px;
                margin: 20px 0;
                display: none;
            }
            .visualization-container.active {
                display: block;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s;
            }
            .summary-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }
            .summary-value {
                font-size: 3em;
                font-weight: 700;
                margin: 10px 0;
            }
            .summary-label {
                font-size: 1.1em;
                opacity: 0.9;
            }
            .info-box {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            .info-box h3 {
                color: #667eea;
                margin-top: 0;
            }
            
            /* Mobile responsive */
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                .header h1 {
                    font-size: 1.8em;
                }
                .navigation {
                    gap: 5px;
                }
                .nav-btn {
                    padding: 8px 15px;
                    font-size: 0.9em;
                }
            }
        </style>
        """
        
        self.javascript = """
        <script>
            function showVisualization(vizId) {
                // Hide all visualizations
                document.querySelectorAll('.visualization-container').forEach(el => {
                    el.classList.remove('active');
                });
                document.querySelectorAll('.nav-btn').forEach(el => {
                    el.classList.remove('active');
                });
                
                // Show selected visualization
                document.getElementById(vizId).classList.add('active');
                document.querySelector(`[onclick="showVisualization('${vizId}')"]`).classList.add('active');
                
                // Save preference
                localStorage.setItem('lastVisualization', vizId);
            }
            
            // Load last viewed visualization
            window.onload = function() {
                const lastViz = localStorage.getItem('lastVisualization') || 'overview';
                showVisualization(lastViz);
            }
            
            // Export functions
            function exportAllData() {
                const data = {
                    meta_data: window.metaData,
                    matchup_data: window.matchupData,
                    export_date: new Date().toISOString()
                };
                
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `manalytics_export_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
            }
        </script>
        """
    
    def create_unified_dashboard(self, 
                               merged_data: Dict,
                               daily_meta: Dict,
                               visualizations: Dict[str, str]) -> str:
        """
        Create a unified dashboard with all visualizations.
        
        Args:
            merged_data: Merged tournament and match data
            daily_meta: Daily meta evolution data
            visualizations: Dictionary of visualization HTML file paths
            
        Returns:
            Complete HTML dashboard
        """
        # Calculate summary statistics
        total_matches = merged_data['total_matches']
        total_tournaments = len(merged_data['matched_tournaments'])
        unique_archetypes = len(merged_data['archetype_stats'])
        
        # Get top archetype
        top_archetype = max(
            merged_data['archetype_stats'].items(),
            key=lambda x: x[1]['matches']
        )[0] if merged_data['archetype_stats'] else "N/A"
        
        # Create overview section
        overview_html = self._create_overview_section(merged_data, daily_meta)
        
        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Advanced MTGOData Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {self.template_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Manalytics - Advanced MTGOData Analysis Dashboard</h1>
            <p>Real-time match data from MTGOData • Interactive Plotly visualizations</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Period: July 1-21, 2025 • Standard Format</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Total Matches Analyzed</div>
                <div class="summary-value">{total_matches:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Tournaments Processed</div>
                <div class="summary-value">{total_tournaments}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Unique Archetypes</div>
                <div class="summary-value">{unique_archetypes}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Top Archetype</div>
                <div class="summary-value" style="font-size: 1.5em;">{top_archetype}</div>
            </div>
        </div>
        
        <div class="navigation">
            <button class="nav-btn active" onclick="showVisualization('overview')">📊 Overview</button>
            <button class="nav-btn" onclick="showVisualization('sunburst')">🎯 Animated Sunburst</button>
            <button class="nav-btn" onclick="showVisualization('stream')">📈 Stream Graph</button>
            <button class="nav-btn" onclick="showVisualization('emergence')">🚀 Emergence Tracker</button>
            <button class="nav-btn" onclick="showVisualization('matrix')">🎲 Matchup Matrix</button>
            <button class="nav-btn" onclick="showVisualization('consensus')">🃏 Consensus Builder</button>
            <button class="nav-btn" onclick="exportAllData()">💾 Export Data</button>
        </div>
        
        <!-- Overview Section -->
        <div id="overview" class="visualization-container active">
            <h2>📊 Metagame Overview</h2>
            {overview_html}
        </div>
        
        <!-- Animated Sunburst -->
        <div id="sunburst" class="visualization-container">
            <h2>🎯 Animated Metagame Evolution</h2>
            <iframe src="{visualizations.get('sunburst', '')}" 
                    style="width: 100%; height: 800px; border: none;"></iframe>
            <div class="info-box">
                <h3>How to use:</h3>
                <ul>
                    <li>Click the Play button to see the metagame evolution day by day</li>
                    <li>Use the slider to jump to specific dates</li>
                    <li>Hover over segments for detailed statistics</li>
                    <li>Inner ring shows macro archetypes (Aggro, Control, etc.)</li>
                </ul>
            </div>
        </div>
        
        <!-- Stream Graph -->
        <div id="stream" class="visualization-container">
            <h2>📈 Metagame Stream Evolution</h2>
            <iframe src="{visualizations.get('stream', '')}" 
                    style="width: 100%; height: 800px; border: none;"></iframe>
            <div class="info-box">
                <h3>Insights:</h3>
                <ul>
                    <li>Width of each stream represents the archetype's meta share</li>
                    <li>Use the range slider to zoom into specific periods</li>
                    <li>Hover to see exact percentages at any point</li>
                </ul>
            </div>
        </div>
        
        <!-- Emergence Tracker -->
        <div id="emergence" class="visualization-container">
            <h2>🚀 Archetype Emergence Tracker</h2>
            <iframe src="{visualizations.get('emergence', '')}" 
                    style="width: 100%; height: 800px; border: none;"></iframe>
            <div class="info-box">
                <h3>Understanding the chart:</h3>
                <ul>
                    <li><span style="color: green;">Green bubbles</span>: Emerging archetypes (growing rapidly)</li>
                    <li><span style="color: red;">Red bubbles</span>: Declining archetypes</li>
                    <li>Bubble size = growth rate</li>
                    <li>X-axis = current meta share, Y-axis = win rate</li>
                </ul>
            </div>
        </div>
        
        <!-- Matchup Matrix -->
        <div id="matrix" class="visualization-container">
            <h2>🎲 Interactive Matchup Matrix</h2>
            <iframe src="{visualizations.get('matrix', '')}" 
                    style="width: 100%; height: 1200px; border: none;"></iframe>
            <div class="info-box">
                <h3>Reading the matrix:</h3>
                <ul>
                    <li>Green = favorable matchup (>55% win rate)</li>
                    <li>Red = unfavorable matchup (<45% win rate)</li>
                    <li>Hover for exact win rates and confidence intervals</li>
                    <li>Numbers show extreme matchups (>65% or <35%)</li>
                </ul>
            </div>
        </div>
        
        <!-- Consensus Deck Builder -->
        <div id="consensus" class="visualization-container">
            <h2>🃏 Consensus Deck Builder</h2>
            <iframe src="{visualizations.get('consensus', '')}" 
                    style="width: 100%; height: 600px; border: none;"></iframe>
            <div class="info-box">
                <h3>How it works:</h3>
                <ul>
                    <li>Shows the most common cards for top 3 archetypes</li>
                    <li>Frequency = % of decks playing this card</li>
                    <li>Numbers show average copies per deck</li>
                    <li>Only cards appearing in >50% of decks are shown</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Store data for export
        window.metaData = {json.dumps(daily_meta)};
        window.matchupData = {json.dumps(merged_data['matchup_data'])};
    </script>
    
    {self.javascript}
</body>
</html>"""
        
        return html
    
    def _create_overview_section(self, merged_data: Dict, daily_meta: Dict) -> str:
        """Create the overview section with key charts"""
        # Get latest meta data
        latest_date = max(daily_meta.keys())
        latest_meta = daily_meta[latest_date]
        
        # Sort by percentage
        sorted_meta = sorted(
            latest_meta.items(),
            key=lambda x: x[1]['percentage'],
            reverse=True
        )[:10]
        
        # Create pie chart data
        pie_labels = []
        pie_values = []
        pie_colors = []
        
        for archetype, data in sorted_meta:
            pie_labels.append(f"{archetype} ({data['percentage']:.1f}%)")
            pie_values.append(data['percentage'])
            # Use color from metagame_dynamics
            from .metagame_dynamics import MetagameDynamicsVisualizer
            viz = MetagameDynamicsVisualizer()
            pie_colors.append(viz.color_map.get(archetype, '#808080'))
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Meta Distribution', 'Win Rates', 'Match Volume', 'Daily Trends'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # 1. Pie chart
        fig.add_trace(
            go.Pie(
                labels=pie_labels,
                values=pie_values,
                marker=dict(colors=pie_colors),
                textposition='inside',
                textinfo='label'
            ),
            row=1, col=1
        )
        
        # 2. Win rates bar chart
        fig.add_trace(
            go.Bar(
                x=[arch[0] for arch in sorted_meta],
                y=[arch[1]['win_rate'] for arch in sorted_meta],
                marker_color=[viz.color_map.get(arch[0], '#808080') for arch in sorted_meta],
                text=[f"{arch[1]['win_rate']:.1f}%" for arch in sorted_meta],
                textposition='outside'
            ),
            row=1, col=2
        )
        
        # 3. Match volume
        fig.add_trace(
            go.Bar(
                x=[arch[0] for arch in sorted_meta],
                y=[arch[1]['matches'] for arch in sorted_meta],
                marker_color=[viz.color_map.get(arch[0], '#808080') for arch in sorted_meta],
                text=[str(arch[1]['matches']) for arch in sorted_meta],
                textposition='outside'
            ),
            row=2, col=1
        )
        
        # 4. Daily trends for top 3
        for i, (archetype, _) in enumerate(sorted_meta[:3]):
            dates = []
            percentages = []
            
            for date in sorted(daily_meta.keys()):
                dates.append(date)
                if archetype in daily_meta[date]:
                    percentages.append(daily_meta[date][archetype]['percentage'])
                else:
                    percentages.append(0)
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=percentages,
                    mode='lines+markers',
                    name=archetype,
                    line=dict(width=2)
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Current Metagame Snapshot",
            title_x=0.5
        )
        
        # Update axes
        fig.update_xaxes(tickangle=-45, row=1, col=2)
        fig.update_xaxes(tickangle=-45, row=2, col=1)
        fig.update_yaxes(title_text="Win Rate %", row=1, col=2)
        fig.update_yaxes(title_text="Total Matches", row=2, col=1)
        fig.update_yaxes(title_text="Meta Share %", row=2, col=2)
        
        # Convert to HTML
        return fig.to_html(include_plotlyjs=False, div_id="overview-charts")
    
    def save_dashboard(self, html: str, filename: str = "unified_dashboard.html") -> Path:
        """Save the dashboard to file"""
        output_path = Path('data/cache') / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Unified dashboard saved to: {output_path}")
        print(f"🌐 Open: file://{output_path.absolute()}")
        return output_path