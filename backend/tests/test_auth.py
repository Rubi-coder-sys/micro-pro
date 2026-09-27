"""Tests for authentication and profile endpoints."""

from tests.conftest import auth_header


class TestHealthCheck:
    """Tests for GET /api/health."""

    def test_health_check(self, client):
        resp = client.get("/api/health")
        data = resp.get_json()
        assert resp.status_code in (200, 503)
        assert "message" in data
        assert "database" in data


class TestLogin:
    """Tests for POST /api/login."""

    def test_login_success_student(self, client):
        resp = client.post("/api/login", json={
            "email": "alice@college.edu",
            "password": "password123",
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert "token" in data["data"]
        assert data["data"]["user"]["role"] == "student"

    def test_login_success_faculty(self, client):
        resp = client.post("/api/login", json={
            "email": "sarah.faculty@college.edu",
            "password": "password123",
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert data["data"]["user"]["role"] == "faculty"

    def test_login_wrong_password(self, client):
        resp = client.post("/api/login", json={
            "email": "alice@college.edu",
            "password": "wrongpassword",
        })
        data = resp.get_json()
        assert resp.status_code == 401
        assert data["success"] is False

    def test_login_nonexistent_email(self, client):
        resp = client.post("/api/login", json={
            "email": "nobody@college.edu",
            "password": "password123",
        })
        data = resp.get_json()
        assert resp.status_code == 401
        assert data["success"] is False

    def test_login_missing_fields(self, client):
        resp = client.post("/api/login", json={"email": "alice@college.edu"})
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["success"] is False

    def test_login_invalid_json(self, client):
        resp = client.post("/api/login", data="not json",
                           content_type="text/plain")
        data = resp.get_json()
        assert resp.status_code == 400

    def test_login_invalid_email_format(self, client):
        resp = client.post("/api/login", json={
            "email": "not-an-email",
            "password": "password123",
        })
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["success"] is False


class TestProfile:
    """Tests for GET /api/profile."""

    def test_profile_authenticated(self, client, student_token):
        resp = client.get("/api/profile", headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert "password_hash" not in data["data"]
        assert "email" in data["data"]
        assert "role" in data["data"]

    def test_profile_no_token(self, client):
        resp = client.get("/api/profile")
        data = resp.get_json()
        assert resp.status_code == 401

    def test_profile_invalid_token(self, client):
        resp = client.get("/api/profile",
                          headers={"Authorization": "Bearer invalidtoken"})
        data = resp.get_json()
        assert resp.status_code == 401
