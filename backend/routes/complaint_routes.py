"""Complaint routes: create, view, and resolve complaints."""

from flask import Blueprint, request, g

from models.complaint import (
    create as create_complaint,
    find_by_id,
    get_all,
    update_status,
)
from models.component import find_by_id as find_component
from utils.auth import login_required, faculty_required, student_required
from utils.responses import success_response, error_response
from utils.validators import validate_required_fields, validate_status

complaint_bp = Blueprint("complaints", __name__)


@complaint_bp.route("/api/complaints", methods=["POST"])
@login_required
@student_required
def create_new_complaint():
    """Create a new complaint (student only).

    Request JSON:
        component_id (int, optional): Related component.
        description (str): Complaint description.

    Returns:
        JSON with created complaint data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    missing = validate_required_fields(data, ["description"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    component_id = data.get("component_id")
    if component_id is not None:
        try:
            component_id = int(component_id)
        except (TypeError, ValueError):
            return error_response("component_id must be a valid integer", 400)

        component = find_component(component_id)
        if not component:
            return error_response("Component not found", 404)

    try:
        complaint = create_complaint(g.user_id, component_id, data["description"])
        return success_response("Complaint created", complaint, 201)
    except Exception:
        return error_response("Failed to create complaint", 500)


@complaint_bp.route("/api/complaints", methods=["GET"])
@login_required
def list_complaints():
    """List complaints.

    Students see only their own complaints.
    Faculty see all complaints.

    Query params:
        status: Filter by status ('open', 'resolved').

    Returns:
        JSON list of complaints.
    """
    status_filter = request.args.get("status")

    if g.user_role == "student":
        complaints = get_all(student_id=g.user_id, status_filter=status_filter)
    else:
        complaints = get_all(status_filter=status_filter)

    return success_response("Complaints retrieved", complaints)


@complaint_bp.route("/api/complaints/<int:complaint_id>", methods=["GET"])
@login_required
def get_complaint(complaint_id):
    """Get a single complaint by ID.

    Students can only view their own complaints.

    Args:
        complaint_id: Complaint primary key from URL.

    Returns:
        JSON with complaint data.
    """
    complaint = find_by_id(complaint_id)
    if not complaint:
        return error_response("Complaint not found", 404)

    if g.user_role == "student" and complaint["student_id"] != g.user_id:
        return error_response("You can only view your own complaints", 403)

    return success_response("Complaint retrieved", complaint)


@complaint_bp.route("/api/complaints/<int:complaint_id>", methods=["PUT"])
@login_required
@faculty_required
def resolve_complaint(complaint_id):
    """Update a complaint status (faculty only).

    Request JSON:
        status (str): New status ('open' or 'resolved').

    Args:
        complaint_id: Complaint primary key from URL.

    Returns:
        JSON with updated complaint data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    status = data.get("status")
    if not status:
        return error_response("status is required", 400)

    err = validate_status(status, ("open", "resolved"))
    if err:
        return error_response(err, 400)

    existing = find_by_id(complaint_id)
    if not existing:
        return error_response("Complaint not found", 404)

    try:
        updated = update_status(complaint_id, status)
        return success_response("Complaint updated", updated)
    except Exception:
        return error_response("Failed to update complaint", 500)
