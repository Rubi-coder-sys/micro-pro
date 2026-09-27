"""Issue routes: issue components, return, and view records."""

from flask import Blueprint, request, g

from models.issue import (
    create as create_issue,
    find_by_id,
    get_all,
    return_component,
    has_active_issue_for_request,
)
from models.request import find_by_id as find_request
from models.component import find_by_id as find_component
from utils.auth import login_required, faculty_required
from utils.responses import success_response, error_response

issue_bp = Blueprint("issues", __name__)


def _serialize_issue(issue):
    """Convert datetime and numeric fields for JSON serialization."""
    for key in ("issue_date", "due_date", "return_date"):
        if issue.get(key):
            issue[key] = issue[key].isoformat()
    if issue.get("fine_amount") is not None:
        issue["fine_amount"] = float(issue["fine_amount"])
    return issue


@issue_bp.route("/api/issues", methods=["POST"])
@login_required
@faculty_required
def create_new_issue():
    """Issue a component to a student (faculty only).

    The request must be approved before issuing.

    Request JSON:
        request_id (int): The approved request ID.

    Returns:
        JSON with created issue record data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    request_id = data.get("request_id")
    if not request_id:
        return error_response("request_id is required", 400)

    try:
        request_id = int(request_id)
    except (TypeError, ValueError):
        return error_response("request_id must be a valid integer", 400)

    # Validate the request
    req = find_request(request_id)
    if not req:
        return error_response("Request not found", 404)

    if req["status"] != "approved":
        return error_response("Request must be approved before issuing", 400)

    # Check if already issued
    if has_active_issue_for_request(request_id):
        return error_response("An active issue already exists for this request", 409)

    # Validate component
    component = find_component(req["component_id"])
    if not component:
        return error_response("Component not found", 404)

    if component["status"] != "active":
        return error_response("Component is not active", 400)

    if component["available_quantity"] <= 0:
        return error_response("Component is not available for issue", 400)

    try:
        issue = create_issue(req["component_id"], req["student_id"], request_id)
        return success_response("Component issued successfully", _serialize_issue(issue), 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception:
        return error_response("Failed to issue component", 500)


@issue_bp.route("/api/issues", methods=["GET"])
@login_required
def list_issues():
    """List issue records.

    Students see only their own issues.
    Faculty see all issues.

    Query params:
        status: Filter by status ('issued', 'returned').

    Returns:
        JSON list of issue records.
    """
    status_filter = request.args.get("status")

    if g.user_role == "student":
        issues = get_all(student_id=g.user_id, status_filter=status_filter)
    else:
        issues = get_all(status_filter=status_filter)

    serialized = [_serialize_issue(i) for i in issues]
    return success_response("Issue records retrieved", serialized)


@issue_bp.route("/api/issues/<int:issue_id>", methods=["GET"])
@login_required
def get_issue(issue_id):
    """Get a single issue record by ID.

    Students can only view their own issues.

    Args:
        issue_id: Issue record primary key from URL.

    Returns:
        JSON with issue record data.
    """
    issue = find_by_id(issue_id)
    if not issue:
        return error_response("Issue record not found", 404)

    if g.user_role == "student" and issue["student_id"] != g.user_id:
        return error_response("You can only view your own issue records", 403)

    return success_response("Issue record retrieved", _serialize_issue(issue))


@issue_bp.route("/api/issues/<int:issue_id>/return", methods=["PUT"])
@login_required
def return_issue(issue_id):
    """Process a component return.

    Students can return their own issued components.
    Faculty can return any issued component.

    Args:
        issue_id: Issue record primary key from URL.

    Returns:
        JSON with updated issue record including fine_amount.
    """
    issue = find_by_id(issue_id)
    if not issue:
        return error_response("Issue record not found", 404)

    if issue["status"] == "returned":
        return error_response("Component has already been returned", 400)

    # Students can only return their own
    if g.user_role == "student" and issue["student_id"] != g.user_id:
        return error_response("You can only return your own issued components", 403)

    try:
        updated = return_component(issue_id)
        return success_response("Component returned successfully", _serialize_issue(updated))
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception:
        return error_response("Failed to process return", 500)
