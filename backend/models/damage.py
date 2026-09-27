"""Damage model — database operations for the damage_records table."""

from utils.database import get_connection, get_cursor


def create(data):
    """Create a new damage record.

    Args:
        data: Dict with component_id, student_id, issue_id,
              damage_description, quantity_damaged.

    Returns:
        The created damage record dict.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """INSERT INTO damage_records
               (component_id, student_id, issue_id, damage_description, quantity_damaged)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING *""",
            (
                data["component_id"],
                data["student_id"],
                data.get("issue_id"),
                data["damage_description"],
                data.get("quantity_damaged", 1),
            ),
        )
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_by_id(damage_id):
    """Find a damage record by ID.

    Args:
        damage_id: The damage record's primary key.

    Returns:
        A dict representing the damage record, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM damage_records WHERE id = %s", (damage_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all(student_id=None, component_id=None):
    """Retrieve damage records, optionally filtered.

    Args:
        student_id: Filter by student ID, or None for all.
        component_id: Filter by component ID, or None for all.

    Returns:
        List of damage record dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        query = """
            SELECT dr.*, u.name AS student_name, u.email AS student_email,
                   c.name AS component_name, c.component_code
            FROM damage_records dr
            JOIN users u ON dr.student_id = u.id
            JOIN components c ON dr.component_id = c.id
            WHERE 1=1
        """
        params = []

        if student_id:
            query += " AND dr.student_id = %s"
            params.append(student_id)
        if component_id:
            query += " AND dr.component_id = %s"
            params.append(component_id)

        query += " ORDER BY dr.damage_date DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
