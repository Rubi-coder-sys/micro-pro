"""Component routes: CRUD, search, and availability."""

from flask import Blueprint, request, g

from models.component import (
    get_all,
    find_by_id,
    search,
    create,
    update,
    update_status,
)
from utils.auth import login_required, faculty_required
from utils.responses import success_response, error_response
from utils.validators import validate_required_fields, validate_positive_integer, validate_status

component_bp = Blueprint("components", __name__)


def _serialize_component(comp):
    """Add computed borrowed_quantity to a component dict."""
    comp["borrowed_quantity"] = comp["total_quantity"] - comp["available_quantity"]
    # Convert datetimes to ISO strings for JSON
    for key in ("created_at", "updated_at"):
        if comp.get(key):
            comp[key] = comp[key].isoformat()
    return comp


@component_bp.route("/api/components", methods=["GET"])
@login_required
def list_components():
    """List all components with optional filters.

    Query params:
        status: Filter by status ('active'/'inactive').
        category: Filter by category.

    Returns:
        JSON list of components with computed borrowed_quantity.
    """
    status_filter = request.args.get("status")
    category_filter = request.args.get("category")

    components = get_all(status_filter=status_filter, category_filter=category_filter)
    serialized = [_serialize_component(c) for c in components]
    return success_response("Components retrieved", serialized)


@component_bp.route("/api/components/search", methods=["GET"])
@login_required
def search_components():
    """Search components by name, code, or category.

    Query params:
        q: Search query string.

    Returns:
        JSON list of matching components.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return error_response("Search query 'q' is required", 400)

    results = search(query)
    serialized = [_serialize_component(c) for c in results]
    return success_response("Search results", serialized)


@component_bp.route("/api/components/<int:component_id>", methods=["GET"])
@login_required
def get_component(component_id):
    """Get a single component by ID.

    Args:
        component_id: Component primary key from URL.

    Returns:
        JSON with component data and computed borrowed_quantity.
    """
    comp = find_by_id(component_id)
    if not comp:
        return error_response("Component not found", 404)

    return success_response("Component retrieved", _serialize_component(comp))


@component_bp.route("/api/components", methods=["POST"])
@login_required
@faculty_required
def create_component():
    """Create a new component (faculty only).

    Request JSON:
        component_code, name, category, total_quantity, available_quantity,
        description, status.

    Returns:
        JSON with created component data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    missing = validate_required_fields(data, ["component_code", "name", "total_quantity"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Validate quantities
    total, err = validate_positive_integer(data["total_quantity"], "total_quantity")
    if err:
        return error_response(err, 400)

    available = data.get("available_quantity", total)
    available, err = validate_positive_integer(available, "available_quantity")
    if err:
        return error_response(err, 400)

    if available > total:
        return error_response("available_quantity cannot exceed total_quantity", 400)

    # Validate status if provided
    status = data.get("status", "active")
    err = validate_status(status, ("active", "inactive"))
    if err:
        return error_response(err, 400)

    data["total_quantity"] = total
    data["available_quantity"] = available
    data["status"] = status

    try:
        comp = create(data)
        return success_response("Component created", _serialize_component(comp), 201)
    except Exception as e:
        error_msg = str(e)
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return error_response("A component with this code already exists", 409)
        return error_response("Failed to create component", 500)


@component_bp.route("/api/components/<int:component_id>", methods=["PUT"])
@login_required
@faculty_required
def update_component(component_id):
    """Update an existing component (faculty only).

    Args:
        component_id: Component primary key from URL.

    Request JSON:
        component_code, name, category, total_quantity, available_quantity,
        description, status.

    Returns:
        JSON with updated component data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    existing = find_by_id(component_id)
    if not existing:
        return error_response("Component not found", 404)

    missing = validate_required_fields(data, ["component_code", "name", "total_quantity"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    total, err = validate_positive_integer(data["total_quantity"], "total_quantity")
    if err:
        return error_response(err, 400)

    available = data.get("available_quantity", existing["available_quantity"])
    available, err = validate_positive_integer(available, "available_quantity")
    if err:
        return error_response(err, 400)

    if available > total:
        return error_response("available_quantity cannot exceed total_quantity", 400)

    status = data.get("status", existing["status"])
    err = validate_status(status, ("active", "inactive"))
    if err:
        return error_response(err, 400)

    data["total_quantity"] = total
    data["available_quantity"] = available
    data["status"] = status

    try:
        comp = update(component_id, data)
        if not comp:
            return error_response("Component not found", 404)
        return success_response("Component updated", _serialize_component(comp))
    except Exception as e:
        error_msg = str(e)
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return error_response("A component with this code already exists", 409)
        return error_response("Failed to update component", 500)


@component_bp.route("/api/components/<int:component_id>/status", methods=["PATCH"])
@login_required
@faculty_required
def change_component_status(component_id):
    """Change a component's status (faculty only).

    Args:
        component_id: Component primary key from URL.

    Request JSON:
        status: New status ('active' or 'inactive').

    Returns:
        JSON with updated component data.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    status = data.get("status")
    if not status:
        return error_response("Status is required", 400)

    err = validate_status(status, ("active", "inactive"))
    if err:
        return error_response(err, 400)

    comp = update_status(component_id, status)
    if not comp:
        return error_response("Component not found", 404)

    return success_response("Component status updated", _serialize_component(comp))
