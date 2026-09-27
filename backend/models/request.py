"""Request model — database operations for the component_requests table."""

from utils.database import get_connection, get_cursor


def create(component_id, student_id, queue_position=None):
    """Create a new component request.

    Args:
        component_id: ID of the requested component.
        student_id: ID of the requesting student.
        queue_position: Optional queue position (for queued requests).

    Returns:
        The created request dict.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """INSERT INTO component_requests
               (component_id, student_id, queue_position, status)
               VALUES (%s, %s, %s, 'pending')
               RETURNING *""",
            (component_id, student_id, queue_position),
        )
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_by_id(request_id):
    """Find a request by ID.

    Args:
        request_id: The request's primary key.

    Returns:
        A dict representing the request, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM component_requests WHERE id = %s", (request_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all(student_id=None, status_filter=None, component_id=None):
    """Retrieve requests, optionally filtered.

    Args:
        student_id: Filter by student ID, or None for all.
        status_filter: Filter by status, or None for all.
        component_id: Filter by component ID, or None for all.

    Returns:
        List of request dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        query = """
            SELECT cr.*, u.name AS student_name, u.email AS student_email,
                   c.name AS component_name, c.component_code
            FROM component_requests cr
            JOIN users u ON cr.student_id = u.id
            JOIN components c ON cr.component_id = c.id
            WHERE 1=1
        """
        params = []

        if student_id:
            query += " AND cr.student_id = %s"
            params.append(student_id)
        if status_filter:
            query += " AND cr.status = %s"
            params.append(status_filter)
        if component_id:
            query += " AND cr.component_id = %s"
            params.append(component_id)

        query += " ORDER BY cr.request_date ASC"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def has_active_request(student_id, component_id):
    """Check if student already has a pending request for this component.

    Args:
        student_id: The student's ID.
        component_id: The component's ID.

    Returns:
        True if an active (pending) request exists.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """SELECT id FROM component_requests
               WHERE student_id = %s AND component_id = %s AND status = 'pending'""",
            (student_id, component_id),
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


def get_next_queue_position(component_id):
    """Get the next queue position for a component.

    Args:
        component_id: The component's ID.

    Returns:
        The next queue position integer.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """SELECT COALESCE(MAX(queue_position), 0) + 1 AS next_pos
               FROM component_requests
               WHERE component_id = %s AND status = 'pending' AND queue_position IS NOT NULL""",
            (component_id,),
        )
        row = cur.fetchone()
        return row["next_pos"]
    finally:
        conn.close()


def approve(request_id, faculty_id):
    """Approve a pending request.

    Args:
        request_id: The request's primary key.
        faculty_id: The approving faculty member's ID.

    Returns:
        The updated request dict, or None if not found.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE component_requests
               SET status = 'approved',
                   approved_by = %s,
                   approved_at = CURRENT_TIMESTAMP
               WHERE id = %s AND status = 'pending'
               RETURNING *""",
            (faculty_id, request_id),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reject(request_id, faculty_id):
    """Reject a pending request.

    Args:
        request_id: The request's primary key.
        faculty_id: The rejecting faculty member's ID.

    Returns:
        The updated request dict, or None if not found.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            """UPDATE component_requests
               SET status = 'rejected',
                   approved_by = %s,
                   approved_at = CURRENT_TIMESTAMP
               WHERE id = %s AND status = 'pending'
               RETURNING *""",
            (faculty_id, request_id),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
