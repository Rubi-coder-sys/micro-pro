"""Tests for damage record endpoints."""

from tests.conftest import auth_header


class TestDamageCreation:
    """Tests for POST /api/damages."""

    def test_create_damage_record(self, client, faculty_token):
        """Faculty creates a damage record."""
        resp = client.post("/api/damages", json={
            "component_id": 1,
            "student_id": 1,
            "damage_description": "Board connector broken during test",
            "quantity_damaged": 1,
        }, headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["success"] is True

    def test_student_cannot_create_damage(self, client, student_token):
        resp = client.post("/api/damages", json={
            "component_id": 1,
            "student_id": 1,
            "damage_description": "Test",
            "quantity_damaged": 1,
        }, headers=auth_header(student_token))
        assert resp.status_code == 403

    def test_create_damage_missing_fields(self, client, faculty_token):
        resp = client.post("/api/damages", json={
            "component_id": 1,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 400

    def test_create_damage_invalid_component(self, client, faculty_token):
        resp = client.post("/api/damages", json={
            "component_id": 99999,
            "student_id": 1,
            "damage_description": "Test",
            "quantity_damaged": 1,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 404

    def test_create_damage_invalid_student(self, client, faculty_token):
        resp = client.post("/api/damages", json={
            "component_id": 1,
            "student_id": 99999,
            "damage_description": "Test",
            "quantity_damaged": 1,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 404


class TestDamageListing:
    """Tests for GET /api/damages."""

    def test_list_damages_faculty(self, client, faculty_token):
        resp = client.get("/api/damages", headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert isinstance(data["data"], list)

    def test_list_damages_student(self, client, student_token):
        resp = client.get("/api/damages", headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200

    def test_get_damage_not_found(self, client, faculty_token):
        resp = client.get("/api/damages/99999",
                          headers=auth_header(faculty_token))
        assert resp.status_code == 404
