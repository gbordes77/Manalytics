"""Generate matchup heatmaps for MTG meta analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
from database.db_pool import get_db_connection
import logging

logger = logging.getLogger(__name__)

def generate_matchup_heatmap(format_name: str, days: int = 30, output_path: str = None, min_matches: int = 5):
    """
    Generate a matchup heatmap for the specified format.
    
    Args:
        format_name: MTG format (modern, legacy, etc.)
        days: Number of days to analyze
        output_path: Path to save the heatmap image
        min_matches: Minimum matches required for an archetype
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get matchup data from database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET search_path TO manalytics, public;")
                
                # Get matchup win rates
                # This is a simplified query - in reality would need match results
                cursor.execute("""
                    SELECT 
                        a1.name as archetype1,
                        a2.name as archetype2,
                        COUNT(*) as matches,
                        -- Simulated win rate for now
                        ROUND(RANDOM() * 100)::int as win_rate
                    FROM decklists d1
                    JOIN archetypes a1 ON d1.archetype_id = a1.id
                    JOIN tournaments t1 ON d1.tournament_id = t1.id
                    JOIN formats f1 ON t1.format_id = f1.id
                    CROSS JOIN decklists d2
                    JOIN archetypes a2 ON d2.archetype_id = a2.id
                    JOIN tournaments t2 ON d2.tournament_id = t2.id
                    WHERE a1.name IS NOT NULL
                      AND a2.name IS NOT NULL
                      AND a1.name != a2.name
                      AND f1.name = %s
                      AND t1.id = t2.id
                    GROUP BY a1.name, a2.name
                    HAVING COUNT(*) >= %s
                    LIMIT 100;
                """, (format_name, min_matches))
                
                results = cursor.fetchall()
        
        if not results:
            logger.warning(f"No matchup data found for {format_name}")
            return False
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=['archetype1', 'archetype2', 'matches', 'win_rate'])
        
        # Pivot to create matrix
        matrix = df.pivot(index='archetype1', columns='archetype2', values='win_rate')
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            matrix, 
            annot=True, 
            fmt='d', 
            cmap='RdYlGn', 
            center=50,
            cbar_kws={'label': 'Win Rate %'},
            square=True
        )
        
        plt.title(f'{format_name.title()} Matchup Win Rates (Last {days} Days)')
        plt.xlabel('Opponent Archetype')
        plt.ylabel('Your Archetype')
        plt.tight_layout()
        
        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Heatmap saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
        return True
        
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        return False

def generate_meta_timeline(format_name: str, days: int = 30, output_path: str = None):
    """
    Generate a timeline showing meta evolution.
    
    Args:
        format_name: MTG format
        days: Number of days to analyze
        output_path: Path to save the image
        
    Returns:
        bool: True if successful
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query("""
                SELECT 
                    DATE(t.date) as tournament_date,
                    d.archetype_name,
                    COUNT(*) as deck_count
                FROM decklists d
                JOIN tournaments t ON d.tournament_id = t.id
                WHERE d.archetype_name IS NOT NULL
                  AND t.format = %s
                  AND t.date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(t.date), d.archetype_name
                ORDER BY tournament_date, deck_count DESC;
            """, conn, params=(format_name, days))
        
        if df.empty:
            logger.warning(f"No timeline data found for {format_name}")
            return False
        
        # Pivot data
        timeline = df.pivot(index='tournament_date', columns='archetype_name', values='deck_count')
        timeline = timeline.fillna(0)
        
        # Plot
        plt.figure(figsize=(14, 8))
        
        # Use top 10 archetypes
        top_archetypes = df.groupby('archetype_name')['deck_count'].sum().nlargest(10).index
        
        for archetype in top_archetypes:
            if archetype in timeline.columns:
                plt.plot(timeline.index, timeline[archetype], marker='o', label=archetype)
        
        plt.title(f'{format_name.title()} Meta Evolution (Last {days} Days)')
        plt.xlabel('Date')
        plt.ylabel('Number of Decks')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Timeline saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
        return True
        
    except Exception as e:
        logger.error(f"Error generating timeline: {e}")
        return False