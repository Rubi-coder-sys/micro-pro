"""Request routes: student requests, queue, faculty approval/rejection."""

from flask import Blueprint, request, g

from models.request import (
    create as create_request,
    find_by_id,
    get_all,
    has_active_request,
    get_next_queue_position,
    approve,
    reject,
)
from models.component import find_by_id as find_component
from utils.auth import login_required, faculty_required, student_required
from utils.responses import success_response, error_response

request_bp = Blueprint("requests", __name__)


def _serialize_request(req):
    """Convert datetime fields to ISO strings."""
    for key in ("request_date", "approved_at", "available_from"):
        if req.get(key):
            req[key] = req[key].isoformat()
    return req


@request_bp.route("/api/requests", methods=["POST"])
@login_required
@student_required
def create_new_request():
    """Create a new component request (student only).

    Request JSON:
        component_id (int): The component to request.

    Returns:
        JSON with created request data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    component_id = data.get("component_id")
    if not component_id:
        return error_response("component_id is required", 400)

    try:
        component_id = int(component_id)
    except (TypeError, ValueError):
        return error_response("component_id must be a valid integer", 400)

    # Verify component exists and is active
    component = find_component(component_id)
    if not component:
        return error_response("Component not found", 404)
    if component["status"] != "active":
        return error_response("Component is not active", 400)

    # Check for duplicate pending request
    student_id = g.user_id
    if has_active_request(student_id, component_id):
        return error_response("You already have a pending request for this component", 409)

    # Determine queue position
    queue_position = None
    if component["available_quantity"] <= 0:
        queue_position = get_next_queue_position(component_id)

    try:
        req = create_request(component_id, student_id, queue_position)
        return success_response("Request created", _serialize_request(req), 201)
    except Exception:
        return error_response("Failed to create request", 500)


@request_bp.route("/api/requests", methods=["GET"])
@login_required
def list_requests():
    """List component requests.

    Students see only their own requests.
    Faculty see all requests.

    Query params:
        status: Filter by status ('pending', 'approved', 'rejected').
        component_id: Filter by component ID.

    Returns:
        JSON list of requests.
    """
    status_filter = request.args.get("status")
    component_id = request.args.get("component_id")

    if g.user_role == "student":
        requests_list = get_all(
            student_id=g.user_id,
            status_filter=status_filter,
            component_id=component_id,
        )
    else:
        requests_list = get_all(
            status_filter=status_filter,
            component_id=component_id,
        )

    serialized = [_serialize_request(r) for r in requests_list]
    return success_response("Requests retrieved", serialized)


@request_bp.route("/api/requests/<int:request_id>", methods=["GET"])
@login_required
def get_request(request_id):
    """Get a single request by ID.

    Students can only view their own requests.

    Args:
        request_id: Request primary key from URL.

    Returns:
        JSON with request data.
    """
    req = find_by_id(request_id)
    if not req:
        return error_response("Request not found", 404)

    if g.user_role == "student" and req["student_id"] != g.user_id:
        return error_response("You can only view your own requests", 403)

    return success_response("Request retrieved", _serialize_request(req))


@request_bp.route("/api/requests/<int:request_id>/approve", methods=["PUT"])
@login_required
@faculty_required
def approve_request(request_id):
    """Approve a pending request (faculty only).

    Args:
        request_id: Request primary key from URL.

    Returns:
        JSON with approved request data.
    """
    req = find_by_id(request_id)
    if not req:
        return error_response("Request not found", 404)

    if req["status"] != "pending":
        return error_response(f"Request is already {req['status']}", 400)

    # Verify component is active
    component = find_component(req["component_id"])
    if not component:
        return error_response("Associated component not found", 404)
    if component["status"] != "active":
        return error_response("Component is not active", 400)

    updated = approve(request_id, g.user_id)
    if not updated:
        return error_response("Failed to approve request", 500)

    return success_response("Request approved", _serialize_request(updated))


@request_bp.route("/api/requests/<int:request_id>/reject", methods=["PUT"])
@login_required
@faculty_required
def reject_request(request_id):
    """Reject a pending request (faculty only).

    Args:
        request_id: Request primary key from URL.

    Returns:
        JSON with rejected request data.
    """
    req = find_by_id(request_id)
    if not req:
        return error_response("Request not found", 404)

    if req["status"] != "pending":
        return error_response(f"Request is already {req['status']}", 400)

    updated = reject(request_id, g.user_id)
    if not updated:
        return error_response("Failed to reject request", 500)

    return success_response("Request rejected", _serialize_request(updated))
