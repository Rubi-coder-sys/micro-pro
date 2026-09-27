"""Authentication routes: login and profile."""

from flask import Blueprint, request, g
from werkzeug.security import check_password_hash

from models.user import find_by_email, get_profile
from utils.auth import generate_token, login_required
from utils.responses import success_response, error_response
from utils.validators import validate_required_fields, validate_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """Authenticate a user and return a JWT token.

    Request JSON:
        email (str): User's email address.
        password (str): User's plaintext password.

    Returns:
        JSON with token and user info on success, or error on failure.
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON", 400)

    missing = validate_required_fields(data, ["email", "password"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    email = data["email"].strip().lower()
    password = data["password"]

    if not validate_email(email):
        return error_response("Invalid email format", 400)

    user = find_by_email(email)
    if not user:
        return error_response("Invalid email or password", 401)

    if not user.get("is_active", True):
        return error_response("Account is deactivated. Contact administration.", 403)

    if not check_password_hash(user["password_hash"], password):
        return error_response("Invalid email or password", 401)

    token = generate_token(user["id"], user["role"])

    return success_response("Login successful", {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    })


@auth_bp.route("/api/profile", methods=["GET"])
@login_required
def profile():
    """Get the authenticated user's profile.

    Returns:
        JSON with user profile data (password_hash excluded).
    """
    user = get_profile(g.user_id)
    if not user:
        return error_response("User not found", 404)

    return success_response("Profile retrieved", user)
