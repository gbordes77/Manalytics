"""
SQLite database for cache metadata and indexing.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from contextlib import contextmanager

from .models import CachedTournament


class CacheDatabase:
    """Manages SQLite database for cache metadata"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path("data/cache/tournaments.db")
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tournaments (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    format TEXT NOT NULL,
                    type TEXT,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    players INTEGER,
                    raw_file TEXT,
                    cache_file TEXT,
                    processed_at TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_date ON tournaments(date);
                CREATE INDEX IF NOT EXISTS idx_format ON tournaments(format);
                CREATE INDEX IF NOT EXISTS idx_platform ON tournaments(platform);
                
                CREATE TABLE IF NOT EXISTS cache_status (
                    tournament_id TEXT PRIMARY KEY,
                    colors_detected BOOLEAN DEFAULT FALSE,
                    archetypes_detected BOOLEAN DEFAULT FALSE,
                    cache_version TEXT,
                    last_updated TIMESTAMP,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
                );
            """)
            conn.commit()
    
    def insert_tournament(self, tournament: CachedTournament):
        """Insert or update tournament metadata"""
        with self._get_connection() as conn:
            # Insert tournament
            conn.execute("""
                INSERT OR REPLACE INTO tournaments 
                (id, platform, format, type, name, date, players, raw_file, cache_file, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tournament.id,
                tournament.platform,
                tournament.format,
                tournament.type,
                tournament.name,
                tournament.date.strftime('%Y-%m-%d'),
                tournament.players,
                tournament.raw_file,
                tournament.cache_file,
                tournament.processed_at.isoformat() if tournament.processed_at else None
            ))
            
            # Update cache status
            conn.execute("""
                INSERT OR REPLACE INTO cache_status
                (tournament_id, colors_detected, archetypes_detected, cache_version, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (
                tournament.id,
                tournament.colors_detected,
                tournament.archetypes_detected,
                tournament.cache_version,
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def get_tournament(self, tournament_id: str) -> Optional[CachedTournament]:
        """Get tournament by ID"""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT t.*, cs.colors_detected, cs.archetypes_detected, cs.cache_version
                FROM tournaments t
                LEFT JOIN cache_status cs ON t.id = cs.tournament_id
                WHERE t.id = ?
            """, (tournament_id,)).fetchone()
            
            if row:
                return self._row_to_tournament(row)
            return None
    
    def get_unprocessed_tournaments(self) -> List[CachedTournament]:
        """Get tournaments that haven't been fully processed"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT t.*, cs.colors_detected, cs.archetypes_detected, cs.cache_version
                FROM tournaments t
                LEFT JOIN cache_status cs ON t.id = cs.tournament_id
                WHERE cs.tournament_id IS NULL 
                   OR cs.colors_detected = 0 
                   OR cs.archetypes_detected = 0
                ORDER BY t.date DESC
            """).fetchall()
            
            return [self._row_to_tournament(row) for row in rows]
    
    def get_tournaments_by_format(self, format: str, 
                                 start_date: datetime = None,
                                 end_date: datetime = None) -> List[CachedTournament]:
        """Get tournaments by format and date range"""
        query = """
            SELECT t.*, cs.colors_detected, cs.archetypes_detected, cs.cache_version
            FROM tournaments t
            LEFT JOIN cache_status cs ON t.id = cs.tournament_id
            WHERE t.format = ?
        """
        params = [format]
        
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date.strftime('%Y-%m-%d'))
        
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date.strftime('%Y-%m-%d'))
        
        query += " ORDER BY t.date DESC"
        
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_tournament(row) for row in rows]
    
    def _row_to_tournament(self, row: sqlite3.Row) -> CachedTournament:
        """Convert database row to CachedTournament"""
        return CachedTournament(
            id=row['id'],
            platform=row['platform'],
            format=row['format'],
            type=row['type'],
            name=row['name'],
            date=datetime.strptime(row['date'], '%Y-%m-%d'),
            players=row['players'],
            raw_file=row['raw_file'],
            cache_file=row['cache_file'],
            processed_at=datetime.fromisoformat(row['processed_at']) if row['processed_at'] else None,
            colors_detected=bool(row['colors_detected']) if 'colors_detected' in row.keys() else False,
            archetypes_detected=bool(row['archetypes_detected']) if 'archetypes_detected' in row.keys() else False,
            cache_version=row['cache_version'] if 'cache_version' in row.keys() else "1.0"
        )
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._get_connection() as conn:
            stats = {}
            
            # Total tournaments
            stats['total_tournaments'] = conn.execute(
                "SELECT COUNT(*) FROM tournaments"
            ).fetchone()[0]
            
            # By platform
            platform_stats = conn.execute("""
                SELECT platform, COUNT(*) as count 
                FROM tournaments 
                GROUP BY platform
            """).fetchall()
            stats['by_platform'] = {row['platform']: row['count'] for row in platform_stats}
            
            # By format
            format_stats = conn.execute("""
                SELECT format, COUNT(*) as count 
                FROM tournaments 
                GROUP BY format
            """).fetchall()
            stats['by_format'] = {row['format']: row['count'] for row in format_stats}
            
            # Processing status
            stats['fully_processed'] = conn.execute("""
                SELECT COUNT(*) FROM cache_status 
                WHERE colors_detected = 1 AND archetypes_detected = 1
            """).fetchone()[0]
            
            return stats