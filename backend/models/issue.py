"""Issue model — database operations for the issue_records table."""

from datetime import datetime, timedelta, timezone

from config import Config
from utils.database import get_connection, get_cursor


def create(component_id, student_id, request_id):
    """Create a new issue record and decrease component availability.

    This operation runs inside a transaction to ensure atomicity.

    Args:
        component_id: The component's ID.
        student_id: The student's ID.
        request_id: The approved request's ID.

    Returns:
        The created issue record dict.

    Raises:
        ValueError: If inventory update fails.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        due_date = datetime.now(timezone.utc) + timedelta(days=Config.DEFAULT_ISSUE_DAYS)

        # Decrease available_quantity atomically
        cur.execute(
            """UPDATE components
               SET available_quantity = available_quantity - 1,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
                 AND available_quantity > 0
               RETURNING *""",
            (component_id,),
        )
        component_row = cur.fetchone()
        if not component_row:
            conn.rollback()
            raise ValueError("Component not available for issue")

        # Create issue record
        cur.execute(
            """INSERT INTO issue_records
               (component_id, student_id, request_id, issue_date, due_date, status)
               VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, 'issued')
               RETURNING *""",
            (component_id, student_id, request_id, due_date),
        )
        issue = dict(cur.fetchone())
        conn.commit()
        return issue
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_by_id(issue_id):
    """Find an issue record by ID.

    Args:
        issue_id: The issue record's primary key.

    Returns:
        A dict representing the issue, or None.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute("SELECT * FROM issue_records WHERE id = %s", (issue_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all(student_id=None, status_filter=None):
    """Retrieve issue records, optionally filtered.

    Args:
        student_id: Filter by student ID, or None for all.
        status_filter: Filter by status, or None for all.

    Returns:
        List of issue record dicts.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        query = """
            SELECT ir.*, u.name AS student_name, u.email AS student_email,
                   c.name AS component_name, c.component_code
            FROM issue_records ir
            JOIN users u ON ir.student_id = u.id
            JOIN components c ON ir.component_id = c.id
            WHERE 1=1
        """
        params = []

        if student_id:
            query += " AND ir.student_id = %s"
            params.append(student_id)
        if status_filter:
            query += " AND ir.status = %s"
            params.append(status_filter)

        query += " ORDER BY ir.issue_date DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def return_component(issue_id):
    """Process a component return: update issue, increase inventory, calculate fine.

    This operation runs inside a transaction to ensure atomicity.

    Args:
        issue_id: The issue record's primary key.

    Returns:
        The updated issue record dict.

    Raises:
        ValueError: If the issue is not found or already returned.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        # Lock and fetch the issue record
        cur.execute(
            "SELECT * FROM issue_records WHERE id = %s FOR UPDATE",
            (issue_id,),
        )
        issue = cur.fetchone()
        if not issue:
            conn.rollback()
            raise ValueError("Issue record not found")

        issue = dict(issue)
        if issue["status"] == "returned":
            conn.rollback()
            raise ValueError("Component has already been returned")

        # Calculate fine
        now = datetime.now(timezone.utc)
        fine_amount = 0.0
        if issue["due_date"]:
            due = issue["due_date"]
            # Make due_date offset-aware if it isn't
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if now > due:
                late_days = (now - due).days
                if late_days > 0:
                    fine_amount = late_days * Config.FINE_PER_DAY

        # Update issue record
        cur.execute(
            """UPDATE issue_records
               SET return_date = CURRENT_TIMESTAMP,
                   status = 'returned',
                   fine_amount = %s
               WHERE id = %s
               RETURNING *""",
            (fine_amount, issue_id),
        )
        updated_issue = dict(cur.fetchone())

        # Increase available_quantity (with safety check)
        cur.execute(
            """UPDATE components
               SET available_quantity = available_quantity + 1,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
                 AND available_quantity + 1 <= total_quantity
               RETURNING *""",
            (issue["component_id"],),
        )
        comp_row = cur.fetchone()
        if not comp_row:
            conn.rollback()
            raise ValueError("Inventory update failed — available_quantity would exceed total_quantity")

        conn.commit()
        return updated_issue
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def has_active_issue_for_request(request_id):
    """Check if a request already has an active (issued) issue record.

    Args:
        request_id: The request's ID.

    Returns:
        True if an issued record exists for this request.
    """
    conn = get_connection()
    try:
        cur = get_cursor(conn)
        cur.execute(
            "SELECT id FROM issue_records WHERE request_id = %s AND status = 'issued'",
            (request_id,),
        )
        return cur.fetchone() is not None
    finally:
        conn.close()
