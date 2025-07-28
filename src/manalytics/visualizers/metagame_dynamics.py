"""
Metagame Dynamics Visualization - Animated temporal evolution of the metagame.

This module creates an interactive Plotly visualization showing how the metagame
evolves over time with animations and advanced interactions.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
from pathlib import Path
import json
from collections import defaultdict

# MTG Color scheme
MTG_COLORS = {
    'W': '#FFFBD5',  # White
    'U': '#0E68AB',  # Blue  
    'B': '#150B00',  # Black
    'R': '#D3202A',  # Red
    'G': '#00733E',  # Green
    'WU': '#68A5D9',  # Azorius
    'WB': '#7D6D69',  # Orzhov
    'WR': '#F5B78C',  # Boros
    'WG': '#7FA36F',  # Selesnya
    'UB': '#4B5C8C',  # Dimir
    'UR': '#7B68A3',  # Izzet
    'UG': '#4A8C7B',  # Simic
    'BR': '#8B4F5F',  # Rakdos
    'BG': '#5C6F3D',  # Golgari
    'RG': '#A36F3F',  # Gruul
    'WUB': '#656B7C',  # Esper
    'WUR': '#9B8FA3',  # Jeskai
    'WUG': '#6B9B8F',  # Bant
    'WBR': '#8B6B69',  # Mardu
    'WBG': '#6B7B5F',  # Abzan
    'WRG': '#9B8B6F',  # Naya
    'UBR': '#7B5C7C',  # Grixis
    'UBG': '#4B6B5F',  # Sultai
    'URG': '#7B8B6F',  # Temur
    'BRG': '#6B5C4F',  # Jund
    'WUBR': '#7B6B7C',  # Yore
    'WUBG': '#6B7B6F',  # Witch
    'WURG': '#8B8B7F',  # Ink
    'WBRG': '#8B7B6F',  # Dune
    'UBRG': '#6B6B5F',  # Glint
    'WUBRG': '#7B7B7B'  # Five Color
}


class MetagameDynamicsVisualizer:
    """Creates animated visualizations of metagame evolution"""
    
    def __init__(self):
        self.color_map = self._create_archetype_color_map()
    
    def _create_archetype_color_map(self) -> Dict[str, str]:
        """Create a color map for common archetypes based on their colors"""
        return {
            'Izzet Cauldron': MTG_COLORS['UR'],
            'Dimir Midrange': MTG_COLORS['UB'],
            'Mono White Caretaker': MTG_COLORS['W'],
            'Esper Legends': MTG_COLORS['WUB'],
            'Esper Midrange': MTG_COLORS['WUB'],
            'Mono Red Aggro': MTG_COLORS['R'],
            'Gruul Aggro': MTG_COLORS['RG'],
            'Golgari Midrange': MTG_COLORS['BG'],
            'Azorius Control': MTG_COLORS['WU'],
            'Rakdos Midrange': MTG_COLORS['BR'],
            'Selesnya Tokens': MTG_COLORS['WG'],
            'Boros Convoke': MTG_COLORS['WR'],
            'Simic Ramp': MTG_COLORS['UG'],
            'Orzhov Control': MTG_COLORS['WB'],
            'Temur Ramp': MTG_COLORS['URG'],
            'Jeskai Control': MTG_COLORS['WUR'],
            'Grixis Midrange': MTG_COLORS['UBR'],
            'Jund Midrange': MTG_COLORS['BRG'],
            'Sultai Ramp': MTG_COLORS['UBG'],
            'Naya Aggro': MTG_COLORS['WRG'],
            'Bant Ramp': MTG_COLORS['WUG'],
            'Mardu Midrange': MTG_COLORS['WBR'],
            'Abzan Midrange': MTG_COLORS['WBG']
        }
    
    def create_animated_sunburst(self, daily_meta_data: Dict[str, Dict]) -> go.Figure:
        """
        Create an animated sunburst chart showing metagame evolution.
        
        Args:
            daily_meta_data: Dictionary with dates as keys and meta percentages as values
            
        Returns:
            Plotly figure with animation
        """
        # Sort dates
        sorted_dates = sorted(daily_meta_data.keys())
        
        # Create frames for animation
        frames = []
        
        for date in sorted_dates:
            meta_data = daily_meta_data[date]
            
            # Prepare data for sunburst
            labels = []
            parents = []
            values = []
            colors = []
            hover_text = []
            
            # Add root
            labels.append("Metagame")
            parents.append("")
            values.append(100)
            colors.append("#ffffff")
            hover_text.append("Total Metagame")
            
            # Group by macro archetype (Aggro, Control, Midrange, Combo, Other)
            macro_groups = self._classify_archetypes(meta_data)
            
            for macro, archetypes in macro_groups.items():
                if not archetypes:
                    continue
                    
                # Add macro archetype
                macro_total = sum(meta_data[arch]['percentage'] for arch in archetypes)
                labels.append(macro)
                parents.append("Metagame")
                values.append(macro_total)
                colors.append(self._get_macro_color(macro))
                hover_text.append(f"{macro}: {macro_total:.1f}%")
                
                # Add individual archetypes
                for arch in archetypes:
                    arch_data = meta_data[arch]
                    labels.append(arch)
                    parents.append(macro)
                    values.append(arch_data['percentage'])
                    colors.append(self.color_map.get(arch, '#808080'))
                    
                    # Create detailed hover text
                    hover = (f"<b>{arch}</b><br>"
                            f"Share: {arch_data['percentage']:.1f}%<br>"
                            f"Win Rate: {arch_data.get('win_rate', 50):.1f}%<br>"
                            f"Matches: {arch_data.get('matches', 0)}")
                    hover_text.append(hover)
            
            frame = go.Frame(
                data=[go.Sunburst(
                    labels=labels,
                    parents=parents,
                    values=values,
                    marker=dict(colors=colors),
                    hovertext=hover_text,
                    hoverinfo='text',
                    textinfo='label+percent parent'
                )],
                name=date
            )
            frames.append(frame)
        
        # Create initial figure
        fig = go.Figure(
            data=frames[0].data,
            frames=frames
        )
        
        # Add play button and slider
        fig.update_layout(
            title={
                'text': '🎯 Metagame Evolution - Standard Format',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 28}
            },
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'x': 0.1,
                'y': 0,
                'xanchor': 'right',
                'yanchor': 'top',
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300, 'easing': 'quadratic-in-out'}
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 20},
                    'prefix': 'Date: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {
                        'args': [[frame.name], {
                            'frame': {'duration': 300, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 300}
                        }],
                        'label': frame.name,
                        'method': 'animate'
                    }
                    for frame in frames
                ]
            }],
            width=1200,
            height=800
        )
        
        return fig
    
    def create_stream_graph(self, daily_meta_data: Dict[str, Dict]) -> go.Figure:
        """
        Create a stream graph showing metagame flow over time.
        
        Args:
            daily_meta_data: Dictionary with dates as keys and meta percentages as values
            
        Returns:
            Plotly figure
        """
        # Get all archetypes and dates
        sorted_dates = sorted(daily_meta_data.keys())
        all_archetypes = set()
        for meta in daily_meta_data.values():
            all_archetypes.update(meta.keys())
        
        # Filter top archetypes
        archetype_totals = defaultdict(float)
        for meta in daily_meta_data.values():
            for arch, data in meta.items():
                archetype_totals[arch] += data['percentage']
        
        top_archetypes = sorted(archetype_totals.items(), key=lambda x: x[1], reverse=True)[:15]
        top_arch_names = [arch[0] for arch in top_archetypes]
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each archetype
        for archetype in top_arch_names:
            x = []
            y = []
            
            for date in sorted_dates:
                x.append(datetime.strptime(date, '%Y-%m-%d'))
                if archetype in daily_meta_data[date]:
                    y.append(daily_meta_data[date][archetype]['percentage'])
                else:
                    y.append(0)
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                stackgroup='one',
                name=archetype,
                line=dict(width=0.5, color=self.color_map.get(archetype, '#808080')),
                fillcolor=self.color_map.get(archetype, '#808080'),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Share: %{y:.1f}%<extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': '📈 Metagame Stream - Top 15 Archetypes',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Date',
                rangeslider=dict(visible=True),
                type='date'
            ),
            yaxis=dict(
                title='Meta Share %',
                range=[0, 100]
            ),
            hovermode='x unified',
            width=1400,
            height=800,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_emergence_tracker(self, daily_meta_data: Dict[str, Dict]) -> go.Figure:
        """
        Create a scatter plot tracking emerging archetypes.
        
        Args:
            daily_meta_data: Dictionary with dates as keys and meta percentages as values
            
        Returns:
            Plotly figure
        """
        # Calculate growth rates
        sorted_dates = sorted(daily_meta_data.keys())
        archetype_growth = defaultdict(list)
        
        for i in range(1, len(sorted_dates)):
            prev_date = sorted_dates[i-1]
            curr_date = sorted_dates[i]
            
            prev_meta = daily_meta_data[prev_date]
            curr_meta = daily_meta_data[curr_date]
            
            for archetype, curr_data in curr_meta.items():
                if archetype in prev_meta:
                    prev_pct = prev_meta[archetype]['percentage']
                    curr_pct = curr_data['percentage']
                    
                    if prev_pct > 0:
                        growth_rate = ((curr_pct - prev_pct) / prev_pct) * 100
                    else:
                        growth_rate = 100 if curr_pct > 0 else 0
                    
                    archetype_growth[archetype].append({
                        'date': curr_date,
                        'growth': growth_rate,
                        'percentage': curr_pct,
                        'win_rate': curr_data.get('win_rate', 50)
                    })
        
        # Create animated scatter plot
        fig = go.Figure()
        
        # Find archetypes with significant changes
        emerging = []
        declining = []
        
        for archetype, growth_data in archetype_growth.items():
            if not growth_data:
                continue
                
            # Get latest data
            latest = growth_data[-1]
            avg_growth = np.mean([g['growth'] for g in growth_data[-3:]])  # Last 3 periods
            
            if avg_growth > 20 and latest['percentage'] > 2:
                emerging.append((archetype, latest, avg_growth))
            elif avg_growth < -20 and latest['percentage'] > 2:
                declining.append((archetype, latest, avg_growth))
        
        # Sort by growth rate
        emerging.sort(key=lambda x: x[2], reverse=True)
        declining.sort(key=lambda x: x[2])
        
        # Add traces
        # Emerging archetypes
        if emerging:
            fig.add_trace(go.Scatter(
                x=[e[1]['percentage'] for e in emerging],
                y=[e[1]['win_rate'] for e in emerging],
                mode='markers+text',
                marker=dict(
                    size=[abs(e[2]) for e in emerging],
                    color='green',
                    sizemode='area',
                    sizeref=2.*max([abs(e[2]) for e in emerging])/(40.**2),
                    sizemin=4,
                    line=dict(width=2, color='darkgreen')
                ),
                text=[e[0] for e in emerging],
                textposition='top center',
                name='Emerging',
                hovertemplate='<b>%{text}</b><br>Share: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Growth: +%{marker.size:.1f}%<extra></extra>'
            ))
        
        # Declining archetypes
        if declining:
            fig.add_trace(go.Scatter(
                x=[d[1]['percentage'] for d in declining],
                y=[d[1]['win_rate'] for d in declining],
                mode='markers+text',
                marker=dict(
                    size=[abs(d[2]) for d in declining],
                    color='red',
                    sizemode='area',
                    sizeref=2.*max([abs(d[2]) for d in declining])/(40.**2),
                    sizemin=4,
                    line=dict(width=2, color='darkred')
                ),
                text=[d[0] for d in declining],
                textposition='bottom center',
                name='Declining',
                hovertemplate='<b>%{text}</b><br>Share: %{x:.1f}%<br>Win Rate: %{y:.1f}%<br>Growth: %{marker.size:.1f}%<extra></extra>'
            ))
        
        # Add reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add annotations
        fig.add_annotation(
            x=5, y=50,
            text="Average",
            showarrow=False,
            font=dict(size=12, color="gray"),
            xshift=-40,
            yshift=-20
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🚀 Archetype Emergence Tracker',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                title='Meta Share %',
                range=[0, max(30, max([e[1]['percentage'] for e in emerging + declining]) * 1.1) if emerging + declining else 30]
            ),
            yaxis=dict(
                title='Win Rate %',
                range=[35, 65]
            ),
            width=1200,
            height=800,
            showlegend=True
        )
        
        return fig
    
    def _classify_archetypes(self, meta_data: Dict) -> Dict[str, List[str]]:
        """Classify archetypes into macro categories"""
        categories = {
            'Aggro': [],
            'Midrange': [],
            'Control': [],
            'Combo': [],
            'Ramp': [],
            'Other': []
        }
        
        for archetype in meta_data.keys():
            arch_lower = archetype.lower()
            
            if 'aggro' in arch_lower or 'burn' in arch_lower or 'convoke' in arch_lower:
                categories['Aggro'].append(archetype)
            elif 'midrange' in arch_lower:
                categories['Midrange'].append(archetype)
            elif 'control' in arch_lower:
                categories['Control'].append(archetype)
            elif 'combo' in arch_lower or 'cauldron' in arch_lower:
                categories['Combo'].append(archetype)
            elif 'ramp' in arch_lower:
                categories['Ramp'].append(archetype)
            else:
                categories['Other'].append(archetype)
        
        return categories
    
    def _get_macro_color(self, macro: str) -> str:
        """Get color for macro archetype"""
        macro_colors = {
            'Aggro': '#D32F2F',
            'Midrange': '#388E3C',
            'Control': '#1976D2',
            'Combo': '#7B1FA2',
            'Ramp': '#00796B',
            'Other': '#757575'
        }
        return macro_colors.get(macro, '#757575')
    
    def save_visualization(self, fig: go.Figure, filename: str):
        """Save visualization to HTML file"""
        output_path = Path('data/cache') / filename
        fig.write_html(
            str(output_path),
            include_plotlyjs='cdn',
            config={
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': filename.replace('.html', ''),
                    'height': 1080,
                    'width': 1920,
                    'scale': 2
                }
            }
        )
        print(f"Saved visualization to: {output_path}")
        print(f"Open: file://{output_path.absolute()}")
        return output_path


def test_metagame_dynamics():
    """Test the metagame dynamics visualizer with sample data"""
    # Create sample data for testing
    dates = ['2025-07-01', '2025-07-05', '2025-07-10', '2025-07-15', '2025-07-20']
    
    sample_data = {
        '2025-07-01': {
            'Izzet Cauldron': {'percentage': 20, 'win_rate': 52, 'matches': 100},
            'Dimir Midrange': {'percentage': 18, 'win_rate': 51, 'matches': 90},
            'Mono White Caretaker': {'percentage': 5, 'win_rate': 48, 'matches': 25},
            'Esper Legends': {'percentage': 8, 'win_rate': 53, 'matches': 40},
            'Mono Red Aggro': {'percentage': 10, 'win_rate': 49, 'matches': 50}
        },
        '2025-07-05': {
            'Izzet Cauldron': {'percentage': 22, 'win_rate': 53, 'matches': 120},
            'Dimir Midrange': {'percentage': 17, 'win_rate': 50, 'matches': 85},
            'Mono White Caretaker': {'percentage': 6, 'win_rate': 49, 'matches': 30},
            'Esper Legends': {'percentage': 10, 'win_rate': 54, 'matches': 50},
            'Mono Red Aggro': {'percentage': 8, 'win_rate': 47, 'matches': 40},
            'Gruul Aggro': {'percentage': 3, 'win_rate': 51, 'matches': 15}  # New deck
        },
        '2025-07-10': {
            'Izzet Cauldron': {'percentage': 24, 'win_rate': 54, 'matches': 150},
            'Dimir Midrange': {'percentage': 16, 'win_rate': 49, 'matches': 80},
            'Mono White Caretaker': {'percentage': 7, 'win_rate': 50, 'matches': 35},
            'Esper Legends': {'percentage': 12, 'win_rate': 55, 'matches': 60},
            'Mono Red Aggro': {'percentage': 6, 'win_rate': 46, 'matches': 30},
            'Gruul Aggro': {'percentage': 5, 'win_rate': 52, 'matches': 25}
        },
        '2025-07-15': {
            'Izzet Cauldron': {'percentage': 23, 'win_rate': 53, 'matches': 140},
            'Dimir Midrange': {'percentage': 15, 'win_rate': 48, 'matches': 75},
            'Mono White Caretaker': {'percentage': 8, 'win_rate': 51, 'matches': 40},
            'Esper Legends': {'percentage': 14, 'win_rate': 56, 'matches': 70},
            'Mono Red Aggro': {'percentage': 5, 'win_rate': 45, 'matches': 25},
            'Gruul Aggro': {'percentage': 7, 'win_rate': 53, 'matches': 35},
            'Golgari Midrange': {'percentage': 4, 'win_rate': 52, 'matches': 20}  # New deck
        },
        '2025-07-20': {
            'Izzet Cauldron': {'percentage': 21, 'win_rate': 52, 'matches': 130},
            'Dimir Midrange': {'percentage': 14, 'win_rate': 47, 'matches': 70},
            'Mono White Caretaker': {'percentage': 9, 'win_rate': 52, 'matches': 45},
            'Esper Legends': {'percentage': 15, 'win_rate': 57, 'matches': 75},
            'Mono Red Aggro': {'percentage': 4, 'win_rate': 44, 'matches': 20},
            'Gruul Aggro': {'percentage': 10, 'win_rate': 54, 'matches': 50},  # Growing!
            'Golgari Midrange': {'percentage': 6, 'win_rate': 53, 'matches': 30}
        }
    }
    
    # Create visualizer
    viz = MetagameDynamicsVisualizer()
    
    # Create visualizations
    print("Creating animated sunburst...")
    sunburst = viz.create_animated_sunburst(sample_data)
    viz.save_visualization(sunburst, 'metagame_dynamics_sunburst.html')
    
    print("\nCreating stream graph...")
    stream = viz.create_stream_graph(sample_data)
    viz.save_visualization(stream, 'metagame_dynamics_stream.html')
    
    print("\nCreating emergence tracker...")
    emergence = viz.create_emergence_tracker(sample_data)
    viz.save_visualization(emergence, 'metagame_emergence_tracker.html')


if __name__ == "__main__":
    test_metagame_dynamics()