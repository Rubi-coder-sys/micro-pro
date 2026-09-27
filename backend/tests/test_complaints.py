"""Tests for complaint endpoints."""

from tests.conftest import auth_header


class TestComplaintCreation:
    """Tests for POST /api/complaints."""

    def test_student_create_complaint(self, client, student_token):
        resp = client.post("/api/complaints", json={
            "component_id": 1,
            "description": "Arduino board resets randomly during use",
        }, headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["success"] is True
        assert data["data"]["status"] == "open"
        TestComplaintCreation.complaint_id = data["data"]["id"]

    def test_faculty_cannot_create_complaint(self, client, faculty_token):
        resp = client.post("/api/complaints", json={
            "description": "Faculty complaint",
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 403

    def test_create_complaint_missing_description(self, client, student_token):
        resp = client.post("/api/complaints", json={
            "component_id": 1,
        }, headers=auth_header(student_token))
        assert resp.status_code == 400

    def test_create_complaint_invalid_component(self, client, student_token):
        resp = client.post("/api/complaints", json={
            "component_id": 99999,
            "description": "Test complaint",
        }, headers=auth_header(student_token))
        assert resp.status_code == 404


class TestComplaintListing:
    """Tests for GET /api/complaints."""

    def test_list_complaints_student(self, client, student_token):
        resp = client.get("/api/complaints",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert isinstance(data["data"], list)

    def test_list_complaints_faculty(self, client, faculty_token):
        resp = client.get("/api/complaints",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200

    def test_get_complaint_not_found(self, client, student_token):
        resp = client.get("/api/complaints/99999",
                          headers=auth_header(student_token))
        assert resp.status_code == 404


class TestComplaintResolution:
    """Tests for PUT /api/complaints/<id>."""

    def test_faculty_resolve_complaint(self, client, faculty_token):
        complaint_id = getattr(TestComplaintCreation, "complaint_id", None)
        if not complaint_id:
            return

        resp = client.put(f"/api/complaints/{complaint_id}", json={
            "status": "resolved",
        }, headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["status"] == "resolved"

    def test_student_cannot_resolve(self, client, student_token):
        complaint_id = getattr(TestComplaintCreation, "complaint_id", None)
        if not complaint_id:
            return

        resp = client.put(f"/api/complaints/{complaint_id}", json={
            "status": "resolved",
        }, headers=auth_header(student_token))
        assert resp.status_code == 403

    def test_invalid_status(self, client, faculty_token):
        complaint_id = getattr(TestComplaintCreation, "complaint_id", None)
        if not complaint_id:
            return

        resp = client.put(f"/api/complaints/{complaint_id}", json={
            "status": "invalid_status",
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 400
