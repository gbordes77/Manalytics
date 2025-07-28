"""
Matchup Heatmap Visualizer.

Creates an interactive heatmap showing win rates between archetypes,
similar to Jiliac's matchup matrix visualization.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MatchupHeatmapVisualizer:
    """Creates interactive matchup heatmap visualizations"""
    
    def __init__(self):
        """Initialize the visualizer"""
        self.mtg_colors = {
            'W': '#FFFBD5',  # White
            'U': '#0E68AB',  # Blue
            'B': '#1C1C1C',  # Black
            'R': '#F44336',  # Red
            'G': '#4CAF50',  # Green
            'C': '#9E9E9E'   # Colorless
        }
        
    def create_matchup_heatmap(self, matchup_matrix: Dict[str, Dict[str, Dict]], 
                              output_path: Optional[Path] = None) -> str:
        """
        Create an interactive heatmap of matchup win rates.
        
        Args:
            matchup_matrix: Dictionary of archetype -> archetype -> stats
            output_path: Where to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        # Get all unique archetypes
        archetypes = sorted(set(
            list(matchup_matrix.keys()) + 
            [opp for data in matchup_matrix.values() for opp in data.keys()]
        ))
        
        # Create matrix data
        n = len(archetypes)
        z = np.full((n, n), np.nan)  # Use NaN for missing data
        hover_text = [['' for _ in range(n)] for _ in range(n)]
        
        for i, arch1 in enumerate(archetypes):
            for j, arch2 in enumerate(archetypes):
                if arch1 == arch2:
                    z[i][j] = 50.0  # 50% for mirror matches
                    hover_text[i][j] = f"{arch1} vs {arch2}<br>Mirror Match: 50%"
                elif arch1 in matchup_matrix and arch2 in matchup_matrix[arch1]:
                    stats = matchup_matrix[arch1][arch2]
                    z[i][j] = stats['win_rate']
                    hover_text[i][j] = (
                        f"{arch1} vs {arch2}<br>"
                        f"Win Rate: {stats['win_rate']}%<br>"
                        f"Matches: {stats['matches']}<br>"
                        f"95% CI: [{stats['confidence_lower']:.1f}%, {stats['confidence_upper']:.1f}%]"
                    )
        
        # Create the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=archetypes,
            y=archetypes,
            hoverongaps=False,
            hovertext=hover_text,
            hovertemplate='%{hovertext}<extra></extra>',
            colorscale=[
                [0, '#d32f2f'],      # Red for low win rates
                [0.4, '#ff9800'],    # Orange
                [0.5, '#ffeb3b'],    # Yellow for 50%
                [0.6, '#8bc34a'],    # Light green
                [1, '#2e7d32']       # Dark green for high win rates
            ],
            zmid=50,
            colorbar=dict(
                title="Win Rate %",
                tickmode='linear',
                tick0=0,
                dtick=10
            )
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🎯 Matchup Matrix - Win Rates Between Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Opponent Archetype',
                tickangle=-45,
                side='bottom'
            ),
            yaxis=dict(
                title='Your Archetype',
                autorange='reversed'  # Top to bottom
            ),
            width=1200,
            height=1000,
            plot_bgcolor='white',
            margin=dict(l=150, r=50, t=100, b=150)
        )
        
        # Add diagonal line for mirror matches
        fig.add_shape(
            type="line",
            x0=-0.5, y0=-0.5,
            x1=n-0.5, y1=n-0.5,
            line=dict(color="rgba(0,0,0,0.3)", width=2, dash="dot")
        )
        
        # Add annotations for significant matchups
        annotations = []
        for i, arch1 in enumerate(archetypes):
            for j, arch2 in enumerate(archetypes):
                if i != j and not np.isnan(z[i][j]):
                    if z[i][j] >= 65 or z[i][j] <= 35:  # Highlight extreme matchups
                        annotations.append(
                            dict(
                                x=j, y=i,
                                text=f"{z[i][j]:.0f}",
                                showarrow=False,
                                font=dict(
                                    color='white' if z[i][j] >= 65 or z[i][j] <= 35 else 'black',
                                    size=12,
                                    family='Arial Black'
                                )
                            )
                        )
        
        fig.update_layout(annotations=annotations)
        
        # Generate HTML
        html_content = self._generate_html_template(fig)
        
        # Save to file
        if not output_path:
            output_path = Path("data/cache/matchup_heatmap.html")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Matchup heatmap saved to {output_path}")
        return str(output_path)
    
    def _generate_html_template(self, fig) -> str:
        """Generate the full HTML template with styling"""
        plotly_html = fig.to_html(include_plotlyjs='cdn', div_id='matchup-heatmap')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Matchup Matrix</title>
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
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .info-box {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .color-box {{
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
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
            font-weight: 700;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #7f8c8d;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Matchup Matrix Analysis</h1>
        <p>Win rates between archetypes based on real match data</p>
    </div>
    
    <div class="container">
        <div class="info-box">
            <h2>📊 How to Read This Matrix</h2>
            <div class="legend">
                <div class="legend-item">
                    <div class="color-box" style="background: #2e7d32;"></div>
                    <span><strong>Green (>60%)</strong>: Favorable matchup</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #ffeb3b;"></div>
                    <span><strong>Yellow (~50%)</strong>: Even matchup</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #d32f2f;"></div>
                    <span><strong>Red (<40%)</strong>: Unfavorable matchup</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #e0e0e0;"></div>
                    <span><strong>Gray</strong>: Insufficient data</span>
                </div>
            </div>
            <p style="margin-top: 20px;">
                <strong>Read from left (your deck) to top (opponent's deck)</strong>. 
                Numbers show your win percentage against that opponent.
                Hover over cells for detailed statistics including sample size and confidence intervals.
            </p>
        </div>
        
        {plotly_html}
        
        <div class="info-box" style="margin-top: 30px;">
            <h2>💡 Key Insights</h2>
            <ul>
                <li>Matchups with <strong>larger sample sizes</strong> (>30 matches) are more reliable</li>
                <li>Confidence intervals show the statistical uncertainty - wider intervals mean less certainty</li>
                <li>Mirror matches are always 50% by definition</li>
                <li>Extreme matchups (>65% or <35%) are highlighted with win rate numbers</li>
            </ul>
        </div>
    </div>
</body>
</html>"""