"""Complaint model — database operations for the complaints table."""

from utils.database import get_connection, get_cursor


def create(student_id, component_id, description):
    """Create a new complaint.

    Args:
        student_id: The complaining student's ID.
        component_id: The related component's ID (optional, can be None).
        description: The complaint text.

    Returns:
        The created complaint dict.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """INSERT INTO complaints (student_id, component_id, description, status)
               VALUES (%s, %s, %s, 'open')
               RETURNING *""",
            (student_id, component_id, description),
        )
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_by_id(complaint_id):
    """Find a complaint by ID.

    Args:
        complaint_id: The complaint's primary key.

    Returns:
        A dict representing the complaint, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM complaints WHERE id = %s", (complaint_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all(student_id=None, status_filter=None):
    """Retrieve complaints, optionally filtered.

    Args:
        student_id: Filter by student ID, or None for all.
        status_filter: Filter by status, or None for all.

    Returns:
        List of complaint dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        query = """
            SELECT co.*, u.name AS student_name, u.email AS student_email,
                   c.name AS component_name, c.component_code
            FROM complaints co
            JOIN users u ON co.student_id = u.id
            LEFT JOIN components c ON co.component_id = c.id
            WHERE 1=1
        """
        params = []

        if student_id:
            query += " AND co.student_id = %s"
            params.append(student_id)
        if status_filter:
            query += " AND co.status = %s"
            params.append(status_filter)

        query += " ORDER BY co.id DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_status(complaint_id, status):
    """Update a complaint's status.

    Args:
        complaint_id: The complaint's primary key.
        status: New status ('open' or 'resolved').

    Returns:
        The updated complaint dict, or None if not found.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE complaints SET status = %s WHERE id = %s RETURNING *""",
            (status, complaint_id),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
