"""User model — database operations for the users table."""

from utils.database import get_connection, get_cursor


def find_by_email(email):
    """Find a user by email address.

    Args:
        email: The user's email.

    Returns:
        A dict representing the user row, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def find_by_id(user_id):
    """Find a user by ID.

    Args:
        user_id: The user's primary key.

    Returns:
        A dict representing the user row, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def get_profile(user_id):
    """Get a user's profile (excluding password_hash).

    Args:
        user_id: The user's primary key.

    Returns:
        A dict with profile fields, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """SELECT id, name, enrollment_number, register_number,
                      department, email, role, is_active
               FROM users WHERE id = %s""",
            (user_id,),
        )
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()
