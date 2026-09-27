"""Damage routes: create and view damage records."""

from flask import Blueprint, request, g

from models.damage import create as create_damage, find_by_id, get_all
from models.component import find_by_id as find_component
from models.user import find_by_id as find_user
from models.issue import find_by_id as find_issue
from utils.auth import login_required, faculty_required
from utils.responses import success_response, error_response
from utils.validators import validate_required_fields, validate_positive_integer

damage_bp = Blueprint("damages", __name__)


def _serialize_damage(dmg):
    """Convert datetime fields to ISO strings."""
    if dmg.get("damage_date"):
        dmg["damage_date"] = dmg["damage_date"].isoformat()
    return dmg


@damage_bp.route("/api/damages", methods=["POST"])
@login_required
@faculty_required
def create_damage_record():
    """Create a new damage record (faculty only).

    Request JSON:
        component_id (int): The damaged component.
        student_id (int): The student responsible.
        issue_id (int): Related issue record.
        damage_description (str): Description of damage.
        quantity_damaged (int): Number of units damaged.

    Returns:
        JSON with created damage record data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    missing = validate_required_fields(data, ["component_id", "student_id", "damage_description"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Validate component
    try:
        component_id = int(data["component_id"])
    except (TypeError, ValueError):
        return error_response("component_id must be a valid integer", 400)

    component = find_component(component_id)
    if not component:
        return error_response("Component not found", 404)

    # Validate student
    try:
        student_id = int(data["student_id"])
    except (TypeError, ValueError):
        return error_response("student_id must be a valid integer", 400)

    student = find_user(student_id)
    if not student:
        return error_response("Student not found", 404)

    # Validate issue if provided
    issue_id = data.get("issue_id")
    if issue_id is not None:
        try:
            issue_id = int(issue_id)
        except (TypeError, ValueError):
            return error_response("issue_id must be a valid integer", 400)

        issue = find_issue(issue_id)
        if not issue:
            return error_response("Issue record not found", 404)

        # Verify issue belongs to the student and component
        if issue["student_id"] != student_id:
            return error_response("Issue does not belong to the specified student", 400)
        if issue["component_id"] != component_id:
            return error_response("Issue does not match the specified component", 400)

    # Validate quantity_damaged
    qty = data.get("quantity_damaged", 1)
    qty, err = validate_positive_integer(qty, "quantity_damaged")
    if err:
        return error_response(err, 400)
    if qty <= 0:
        return error_response("quantity_damaged must be greater than 0", 400)

    data["component_id"] = component_id
    data["student_id"] = student_id
    data["issue_id"] = issue_id
    data["quantity_damaged"] = qty

    try:
        damage = create_damage(data)
        return success_response("Damage record created", _serialize_damage(damage), 201)
    except Exception:
        return error_response("Failed to create damage record", 500)


@damage_bp.route("/api/damages", methods=["GET"])
@login_required
def list_damages():
    """List damage records.

    Faculty see all records.
    Students see only their own.

    Query params:
        component_id: Filter by component ID.

    Returns:
        JSON list of damage records.
    """
    component_id = request.args.get("component_id")

    if g.user_role == "student":
        damages = get_all(student_id=g.user_id, component_id=component_id)
    else:
        damages = get_all(component_id=component_id)

    serialized = [_serialize_damage(d) for d in damages]
    return success_response("Damage records retrieved", serialized)


@damage_bp.route("/api/damages/<int:damage_id>", methods=["GET"])
@login_required
def get_damage(damage_id):
    """Get a single damage record by ID.

    Args:
        damage_id: Damage record primary key from URL.

    Returns:
        JSON with damage record data.
    """
    damage = find_by_id(damage_id)
    if not damage:
        return error_response("Damage record not found", 404)

    if g.user_role == "student" and damage["student_id"] != g.user_id:
        return error_response("You can only view your own damage records", 403)

    return success_response("Damage record retrieved", _serialize_damage(damage))
