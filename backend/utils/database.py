"""Database utility module for PostgreSQL connection management."""

import psycopg2
import psycopg2.extras
from config import Config


def get_connection():
    """Create and return a new PostgreSQL database connection."""
    return psycopg2.connect(Config.get_db_dsn())


def get_cursor(conn, dict_cursor=True):
    """Return a cursor from the given connection.

    Args:
        conn: psycopg2 connection object.
        dict_cursor: If True, return a RealDictCursor (rows as dicts).

    Returns:
        A psycopg2 cursor.
    """
    if dict_cursor:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn.cursor()


def check_db_connection():
    """Check if the database is reachable.

    Returns:
        True if connected, False otherwise.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception:
        return False
