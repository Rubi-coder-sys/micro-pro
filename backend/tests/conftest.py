"""Shared test fixtures and helpers."""

import os
import sys
import pytest

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


@pytest.fixture(scope="session")
def app():
    """Create the Flask app for testing."""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="session")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def student_token(client):
    """Login as a student and return the JWT token."""
    resp = client.post("/api/login", json={
        "email": "alice@college.edu",
        "password": "password123",
    })
    data = resp.get_json()
    if data.get("success"):
        return data["data"]["token"]
    pytest.skip("Student login failed — database may not be seeded")


@pytest.fixture(scope="session")
def faculty_token(client):
    """Login as faculty and return the JWT token."""
    resp = client.post("/api/login", json={
        "email": "sarah.faculty@college.edu",
        "password": "password123",
    })
    data = resp.get_json()
    if data.get("success"):
        return data["data"]["token"]
    pytest.skip("Faculty login failed — database may not be seeded")


def auth_header(token):
    """Build an Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}
