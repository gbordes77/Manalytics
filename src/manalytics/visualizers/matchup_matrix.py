"""
Generate visual matchup matrices and meta charts.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class MetaVisualizer:
    """Create visualizations for meta analysis."""
    
    def __init__(self):
        # Set style
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
        # Output directory
        self.output_dir = settings.OUTPUT_DIR / "visualizations"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_matchup_heatmap(self, matchup_data: Dict[str, Dict[str, float]], 
                              format_name: str, save: bool = True) -> Optional[Path]:
        """
        Create a heatmap visualization of matchup win rates.
        
        Args:
            matchup_data: Nested dict of {archetype: {opponent: win_rate}}
            format_name: MTG format name
            save: Whether to save the image
            
        Returns:
            Path to saved image if save=True
        """
        if not matchup_data:
            logger.warning("No matchup data provided")
            return None
        
        # Convert to DataFrame
        archetypes = sorted(matchup_data.keys())
        matrix = pd.DataFrame(index=archetypes, columns=archetypes, dtype=float)
        
        for arch1 in archetypes:
            for arch2 in archetypes:
                if arch1 == arch2:
                    matrix.loc[arch1, arch2] = 50.0  # Mirror matchup
                elif arch2 in matchup_data.get(arch1, {}):
                    matrix.loc[arch1, arch2] = matchup_data[arch1][arch2]
                else:
                    matrix.loc[arch1, arch2] = np.nan
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap
        mask = matrix.isna()
        sns.heatmap(
            matrix,
            mask=mask,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=50,
            vmin=30,
            vmax=70,
            square=True,
            linewidths=0.5,
            cbar_kws={'label': 'Win Rate %'},
            ax=ax
        )
        
        # Customize
        ax.set_title(f'{format_name.upper()} Matchup Matrix', fontsize=16, pad=20)
        ax.set_xlabel('Opponent', fontsize=12)
        ax.set_ylabel('Archetype', fontsize=12)
        
        # Rotate labels
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        plt.figtext(0.99, 0.01, f'Generated: {timestamp}', ha='right', fontsize=8, alpha=0.5)
        
        plt.tight_layout()
        
        if save:
            filename = f"matchup_matrix_{format_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            plt.close()
            logger.info(f"Saved matchup matrix to {filepath}")
            return filepath
        else:
            plt.show()
            return None
    
    def create_meta_pie_chart(self, meta_data: List[Dict[str, Any]], 
                             format_name: str, top_n: int = 8, save: bool = True) -> Optional[Path]:
        """
        Create a pie chart of meta distribution.
        
        Args:
            meta_data: List of dicts with 'archetype' and 'meta_share'
            format_name: MTG format name
            top_n: Number of top archetypes to show individually
            save: Whether to save the image
        """
        if not meta_data:
            return None
        
        # Prepare data
        df = pd.DataFrame(meta_data)
        df = df.sort_values('meta_share', ascending=False)
        
        # Group smaller archetypes
        if len(df) > top_n:
            top_archetypes = df.head(top_n)
            other_share = df.iloc[top_n:]['meta_share'].sum()
            
            if other_share > 0:
                other_row = pd.DataFrame([{
                    'archetype': 'Other',
                    'meta_share': other_share,
                    'deck_count': df.iloc[top_n:]['deck_count'].sum()
                }])
                df_plot = pd.concat([top_archetypes, other_row], ignore_index=True)
            else:
                df_plot = top_archetypes
        else:
            df_plot = df
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart
        colors = sns.color_palette("husl", len(df_plot))
        wedges, texts, autotexts = ax1.pie(
            df_plot['meta_share'],
            labels=df_plot['archetype'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Enhance text
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title(f'{format_name.upper()} Meta Distribution', fontsize=14, pad=20)
        
        # Bar chart for deck counts
        ax2.barh(df_plot['archetype'], df_plot['deck_count'], color=colors)
        ax2.set_xlabel('Number of Decks', fontsize=12)
        ax2.set_title('Deck Counts by Archetype', fontsize=14, pad=20)
        ax2.invert_yaxis()
        
        # Add values on bars
        for i, (archetype, count) in enumerate(zip(df_plot['archetype'], df_plot['deck_count'])):
            ax2.text(count + 1, i, str(count), va='center', fontsize=10)
        
        # Add stats
        total_decks = df_plot['deck_count'].sum()
        unique_archetypes = len(df)
        
        stats_text = f"Total Decks: {total_decks}\nUnique Archetypes: {unique_archetypes}"
        fig.text(0.02, 0.02, stats_text, fontsize=10, alpha=0.7, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.5))
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        fig.text(0.98, 0.02, f'Generated: {timestamp}', ha='right', fontsize=8, alpha=0.5)
        
        plt.tight_layout()
        
        if save:
            filename = f"meta_distribution_{format_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            plt.close()
            logger.info(f"Saved meta distribution to {filepath}")
            return filepath
        else:
            plt.show()
            return None
    
    def create_trend_chart(self, trend_data: List[Dict], format_name: str, 
                          top_n: int = 6, save: bool = True) -> Optional[Path]:
        """
        Create a line chart showing archetype trends over time.
        
        Args:
            trend_data: List of period data with archetype percentages
            format_name: MTG format name
            top_n: Number of top archetypes to track
            save: Whether to save the image
        """
        if not trend_data:
            return None
        
        # Convert to time series format
        dates = []
        archetype_series = {}
        
        for period in trend_data:
            dates.append(pd.to_datetime(period['period']))
            
            for arch_data in period['archetypes']:
                arch_name = arch_data['name']
                if arch_name not in archetype_series:
                    archetype_series[arch_name] = []
                
                archetype_series[arch_name].append(arch_data['percentage'])
        
        # Calculate average presence to find top archetypes
        avg_presence = {
            arch: np.mean(values) 
            for arch, values in archetype_series.items()
        }
        top_archetypes = sorted(avg_presence.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot lines for top archetypes
        for arch_name, _ in top_archetypes:
            # Pad series to match dates length
            values = archetype_series[arch_name]
            if len(values) < len(dates):
                values.extend([0] * (len(dates) - len(values)))
            
            ax.plot(dates, values[:len(dates)], marker='o', linewidth=2.5, 
                   label=arch_name, markersize=6)
        
        # Customize
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Meta Share %', fontsize=12)
        ax.set_title(f'{format_name.upper()} Meta Trends', fontsize=16, pad=20)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, 
                 fancybox=True, shadow=True)
        
        # Format x-axis
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        plt.figtext(0.99, 0.01, f'Generated: {timestamp}', ha='right', fontsize=8, alpha=0.5)
        
        plt.tight_layout()
        
        if save:
            filename = f"meta_trends_{format_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            plt.close()
            logger.info(f"Saved meta trends to {filepath}")
            return filepath
        else:
            plt.show()
            return None
    
    def create_performance_radar(self, archetype_stats: Dict[str, Dict], 
                                format_name: str, save: bool = True) -> Optional[Path]:
        """
        Create a radar chart comparing archetype performance metrics.
        
        Args:
            archetype_stats: Dict of {archetype: {metric: value}}
            format_name: MTG format name
            save: Whether to save the image
        """
        if not archetype_stats:
            return None
        
        # Define metrics to plot
        metrics = ['win_rate', 'top_8_conversion', 'entries_per_tournament']
        metric_labels = ['Win Rate %', 'Top 8 %', 'Popularity']
        
        # Filter archetypes with all metrics
        valid_archetypes = {
            arch: stats for arch, stats in archetype_stats.items()
            if all(m in stats and stats[m] is not None for m in metrics)
        }
        
        if not valid_archetypes:
            logger.warning("No archetypes with complete metrics")
            return None
        
        # Limit to top 6 by total entries
        sorted_archs = sorted(
            valid_archetypes.items(), 
            key=lambda x: x[1].get('total_entries', 0), 
            reverse=True
        )[:6]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Number of variables
        num_vars = len(metrics)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        # Plot each archetype
        for arch_name, stats in sorted_archs:
            values = []
            for metric in metrics:
                value = stats[metric]
                # Normalize popularity to 0-100 scale
                if metric == 'entries_per_tournament':
                    max_val = max(s[1]['entries_per_tournament'] for s in sorted_archs)
                    value = (value / max_val) * 100 if max_val > 0 else 0
                values.append(value)
            
            values += values[:1]  # Complete the circle
            
            ax.plot(angles, values, 'o-', linewidth=2, label=arch_name)
            ax.fill(angles, values, alpha=0.15)
        
        # Fix axis to go in the right order and start at the top
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels, size=12)
        
        # Set y-axis limits and labels
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80])
        ax.set_yticklabels(['20', '40', '60', '80'], size=10)
        
        # Add title and legend
        ax.set_title(f'{format_name.upper()} Archetype Performance Comparison', 
                    size=16, pad=30, weight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), frameon=True, 
                 fancybox=True, shadow=True)
        
        # Grid
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        plt.figtext(0.99, 0.01, f'Generated: {timestamp}', ha='right', fontsize=8, alpha=0.5)
        
        plt.tight_layout()
        
        if save:
            filename = f"performance_radar_{format_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            plt.close()
            logger.info(f"Saved performance radar to {filepath}")
            return filepath
        else:
            plt.show()
            return None
    
    def create_diversity_timeline(self, diversity_data: List[Dict], 
                                 format_name: str, save: bool = True) -> Optional[Path]:
        """
        Create a timeline showing meta diversity metrics.
        
        Args:
            diversity_data: List of {date, hhi, viable_archetypes, top_8_concentration}
            format_name: MTG format name
            save: Whether to save the image
        """
        if not diversity_data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(diversity_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        
        # 1. HHI Index
        ax1.plot(df['date'], df['hhi'], 'o-', color='#ff6b6b', linewidth=2.5, markersize=8)
        ax1.fill_between(df['date'], df['hhi'], alpha=0.3, color='#ff6b6b')
        ax1.set_ylabel('Herfindahl Index', fontsize=12)
        ax1.set_title(f'{format_name.upper()} Meta Diversity Over Time', fontsize=16, pad=20)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Add diversity zones
        ax1.axhspan(0, 1000, alpha=0.1, color='green', label='Highly Diverse')
        ax1.axhspan(1000, 1500, alpha=0.1, color='yellow', label='Diverse')
        ax1.axhspan(1500, 2500, alpha=0.1, color='orange', label='Concentrated')
        ax1.axhspan(2500, 10000, alpha=0.1, color='red', label='Highly Concentrated')
        ax1.legend(loc='upper left', frameon=True)
        
        # 2. Viable Archetypes
        ax2.bar(df['date'], df['viable_archetypes'], width=1, color='#4ecdc4', alpha=0.8)
        ax2.plot(df['date'], df['viable_archetypes'], 'o-', color='#45b7aa', linewidth=2)
        ax2.set_ylabel('Viable Archetypes (>2%)', fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # 3. Top 8 Concentration
        ax3.plot(df['date'], df['top_8_concentration'], 'o-', color='#ffe66d', 
                linewidth=2.5, markersize=8)
        ax3.fill_between(df['date'], df['top_8_concentration'], alpha=0.3, color='#ffe66d')
        ax3.set_ylabel('Top 8 Concentration %', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.grid(True, alpha=0.3, linestyle='--')
        
        # Format x-axis
        import matplotlib.dates as mdates
        ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        plt.figtext(0.99, 0.01, f'Generated: {timestamp}', ha='right', fontsize=8, alpha=0.5)
        
        plt.tight_layout()
        
        if save:
            filename = f"diversity_timeline_{format_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            plt.close()
            logger.info(f"Saved diversity timeline to {filepath}")
            return filepath
        else:
            plt.show()
            return None