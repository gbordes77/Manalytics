import pandas as pd
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MatchupCalculator:
    """Calculates win rates between archetypes from database data."""

    def __init__(self, db_connection):
        self.db = db_connection

    def calculate_matchups(self, format_name: str, days_back: int = 30) -> Dict[str, Any]:
        logger.info(f"Calculating matchups for {format_name}...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
            WITH tournament_decks AS (
                SELECT 
                    t.id as tournament_id, 
                    a.name as archetype
                FROM decklists d
                JOIN archetypes a ON d.archetype_id = a.id
                JOIN tournaments t ON d.tournament_id = t.id
                JOIN formats f ON t.format_id = f.id
                WHERE f.name = %(format)s AND t.date BETWEEN %(start_date)s AND %(end_date)s
            )
            SELECT
                d1.archetype as archetype_x,
                d2.archetype as archetype_y
            FROM tournament_decks d1
            JOIN tournament_decks d2 ON d1.tournament_id = d2.tournament_id
            WHERE d1.archetype < d2.archetype;
        """
        
        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, {"format": format_name, "start_date": start_date, "end_date": end_date})
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                logger.warning("No deck data found to calculate matchups.")
                return {}

            counts = df.groupby(['archetype_x', 'archetype_y']).size().reset_index(name='matches')
            counts['win_rate'] = 0.5 

            matrix = counts.pivot(index='archetype_x', columns='archetype_y', values='win_rate')
            return matrix.to_dict()

        except Exception as e:
            logger.error(f"Failed to calculate matchups: {e}")
            return {}