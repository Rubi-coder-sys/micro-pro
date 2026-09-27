"""Component model — database operations for the components table."""

from utils.database import get_connection, get_cursor


def get_all(status_filter=None, category_filter=None):
    """Retrieve all components, optionally filtered.

    Args:
        status_filter: Filter by status ('active'/'inactive') or None for all.
        category_filter: Filter by category or None for all.

    Returns:
        List of component dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        query = "SELECT * FROM components WHERE 1=1"
        params = []

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        if category_filter:
            query += " AND category = %s"
            params.append(category_filter)

        query += " ORDER BY id"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def find_by_id(component_id):
    """Find a component by ID.

    Args:
        component_id: The component's primary key.

    Returns:
        A dict representing the component, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM components WHERE id = %s", (component_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def search(query_str):
    """Search components by name, component_code, or category.

    Args:
        query_str: Search term.

    Returns:
        List of matching component dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        like_pattern = f"%{query_str}%"
        cur.execute(
            """SELECT * FROM components
               WHERE name ILIKE %s
                  OR component_code ILIKE %s
                  OR category ILIKE %s
               ORDER BY id""",
            (like_pattern, like_pattern, like_pattern),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create(data):
    """Create a new component.

    Args:
        data: Dict with component fields.

    Returns:
        The created component dict.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """INSERT INTO components
               (component_code, name, category, total_quantity, available_quantity, description, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING *""",
            (
                data["component_code"],
                data["name"],
                data.get("category", ""),
                data["total_quantity"],
                data["available_quantity"],
                data.get("description", ""),
                data.get("status", "active"),
            ),
        )
        component = dict(cur.fetchone())
        conn.commit()
        return component
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update(component_id, data):
    """Update an existing component.

    Args:
        component_id: The component's primary key.
        data: Dict with fields to update.

    Returns:
        The updated component dict, or None if not found.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE components
               SET component_code = %s,
                   name = %s,
                   category = %s,
                   total_quantity = %s,
                   available_quantity = %s,
                   description = %s,
                   status = %s,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING *""",
            (
                data["component_code"],
                data["name"],
                data.get("category", ""),
                data["total_quantity"],
                data["available_quantity"],
                data.get("description", ""),
                data.get("status", "active"),
                component_id,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_status(component_id, status):
    """Update only the status of a component.

    Args:
        component_id: The component's primary key.
        status: New status ('active' or 'inactive').

    Returns:
        The updated component dict, or None if not found.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE components
               SET status = %s, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING *""",
            (status, component_id),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_available_quantity(component_id, delta, conn=None):
    """Atomically adjust available_quantity by delta.

    Args:
        component_id: The component's primary key.
        delta: Integer to add (positive) or subtract (negative).
        conn: Optional existing connection (for transactions).

    Returns:
        The updated component dict.

    Raises:
        ValueError: If the resulting quantity would be invalid.
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE components
               SET available_quantity = available_quantity + %s,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
                 AND available_quantity + %s >= 0
                 AND available_quantity + %s <= total_quantity
               RETURNING *""",
            (delta, component_id, delta, delta),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Quantity update would result in invalid inventory state")
        if own_conn:
            conn.commit()
        return dict(row)
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()
