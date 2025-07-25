import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MetaAnalyzer:
    """Analyzes metagame data from the database."""

    def __init__(self, db_connection):
        self.db = db_connection

    def get_meta_breakdown(self, format_name: str, days_back: int = 30) -> List[Dict[str, Any]]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
            SELECT
                a.name as archetype,
                a.display_name as archetype_name,
                COUNT(d.id)::int as deck_count,
                (COUNT(d.id) * 100.0 / SUM(COUNT(d.id)) OVER ()) as meta_share
            FROM decklists d
            JOIN archetypes a ON d.archetype_id = a.id
            JOIN tournaments t ON d.tournament_id = t.id
            JOIN formats f ON t.format_id = f.id
            WHERE f.name = %(format)s AND t.date BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY a.name, a.display_name
            HAVING COUNT(d.id) > 1
            ORDER BY deck_count DESC;
        """
        
        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, {"format": format_name, "start_date": start_date, "end_date": end_date})
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
            return df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Failed to get meta breakdown: {e}")
            return []