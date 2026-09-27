"""Standardized API response helpers."""

from flask import jsonify


def success_response(message="Operation successful", data=None, status_code=200):
    """Build a success JSON response.

    Args:
        message: Human-readable success message.
        data: Payload data (dict, list, or None).
        status_code: HTTP status code (default 200).

    Returns:
        Flask Response tuple (body, status_code).
    """
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error_response(message="An error occurred", status_code=400):
    """Build an error JSON response.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code (default 400).

    Returns:
        Flask Response tuple (body, status_code).
    """
    return jsonify({"success": False, "message": message}), status_code
