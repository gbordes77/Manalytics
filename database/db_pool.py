import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None

def init_db_pool(minconn=1, maxconn=10):
    """Initialize the database connection pool."""
    global _connection_pool
    try:
        _connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=settings.DATABASE_URL
        )
        logger.info(f"Database connection pool initialized with {minconn}-{maxconn} connections")
    except psycopg2.Error as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise

def get_connection():
    """Get a connection from the pool."""
    if _connection_pool is None:
        init_db_pool()
    return _connection_pool.getconn()

def put_connection(conn):
    """Return a connection to the pool."""
    if _connection_pool is not None:
        _connection_pool.putconn(conn)

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = get_connection()
        # Set the search path to use manalytics schema
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO manalytics, public;")
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            put_connection(conn)

def close_db_pool():
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        logger.info("Database connection pool closed")
        _connection_pool = None