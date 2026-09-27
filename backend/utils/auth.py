"""Authentication utilities: JWT token creation, verification, and decorators."""

import functools
from datetime import datetime, timedelta, timezone

import jwt
from flask import request, g

from config import Config


def generate_token(user_id, role):
    """Generate a JWT token for the given user.

    Args:
        user_id: The user's database ID.
        role: The user's role ('student' or 'faculty').

    Returns:
        Encoded JWT string.
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token):
    """Decode and validate a JWT token.

    Args:
        token: The JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])


def login_required(f):
    """Decorator that enforces JWT authentication on a route.

    Sets g.user_id and g.user_role from the token payload.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"success": False, "message": "Authorization header is missing"}, 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return {"success": False, "message": "Invalid authorization header format. Use: Bearer <token>"}, 401

        token = parts[1]
        try:
            payload = decode_token(token)
            g.user_id = payload["user_id"]
            g.user_role = payload["role"]
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}, 401

        return f(*args, **kwargs)

    return decorated


def faculty_required(f):
    """Decorator that enforces faculty role. Must be used after @login_required."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if g.user_role != "faculty":
            return {"success": False, "message": "Faculty access required"}, 403
        return f(*args, **kwargs)

    return decorated


def student_required(f):
    """Decorator that enforces student role. Must be used after @login_required."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if g.user_role != "student":
            return {"success": False, "message": "Student access required"}, 403
        return f(*args, **kwargs)

    return decorated
