"""Tests for request endpoints: creation, queue, approval, rejection."""

from tests.conftest import auth_header


class TestRequestCreation:
    """Tests for POST /api/requests."""

    def test_student_create_request(self, client, student_token):
        """Student creates a request for component 2 (Arduino Mega)."""
        resp = client.post("/api/requests", json={
            "component_id": 2,
        }, headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["success"] is True
        assert data["data"]["status"] == "pending"

    def test_duplicate_request(self, client, student_token):
        """Same student cannot request same component twice while pending."""
        resp = client.post("/api/requests", json={
            "component_id": 2,
        }, headers=auth_header(student_token))
        assert resp.status_code == 409

    def test_request_nonexistent_component(self, client, student_token):
        resp = client.post("/api/requests", json={
            "component_id": 99999,
        }, headers=auth_header(student_token))
        assert resp.status_code == 404

    def test_request_inactive_component(self, client, student_token):
        """Cannot request an inactive component."""
        # Component 11 (OLD-COMP-001) is inactive
        resp = client.post("/api/requests", json={
            "component_id": 11,
        }, headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 400

    def test_faculty_cannot_create_request(self, client, faculty_token):
        resp = client.post("/api/requests", json={
            "component_id": 1,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 403

    def test_request_missing_component_id(self, client, student_token):
        resp = client.post("/api/requests", json={},
                           headers=auth_header(student_token))
        assert resp.status_code == 400


class TestRequestListing:
    """Tests for GET /api/requests."""

    def test_student_sees_own_requests(self, client, student_token):
        resp = client.get("/api/requests",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert isinstance(data["data"], list)

    def test_faculty_sees_all_requests(self, client, faculty_token):
        resp = client.get("/api/requests",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert isinstance(data["data"], list)

    def test_filter_by_status(self, client, faculty_token):
        resp = client.get("/api/requests?status=pending",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        for req in data["data"]:
            assert req["status"] == "pending"


class TestRequestApproval:
    """Tests for PUT /api/requests/<id>/approve."""

    def test_faculty_approve_request(self, client, faculty_token):
        """Faculty approves a pending request."""
        # Find a pending request
        resp = client.get("/api/requests?status=pending",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        pending = data["data"]
        if not pending:
            return  # No pending requests to test

        request_id = pending[0]["id"]
        resp = client.put(f"/api/requests/{request_id}/approve",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["status"] == "approved"

    def test_student_cannot_approve(self, client, student_token):
        resp = client.put("/api/requests/1/approve",
                          headers=auth_header(student_token))
        assert resp.status_code == 403

    def test_approve_nonexistent_request(self, client, faculty_token):
        resp = client.put("/api/requests/99999/approve",
                          headers=auth_header(faculty_token))
        assert resp.status_code == 404


class TestRequestRejection:
    """Tests for PUT /api/requests/<id>/reject."""

    def test_faculty_reject_request(self, client, faculty_token, student_token):
        """Create a fresh request and reject it."""
        # Create a new request first
        create_resp = client.post("/api/requests", json={
            "component_id": 3,
        }, headers=auth_header(student_token))
        cdata = create_resp.get_json()
        if create_resp.status_code != 201:
            return

        request_id = cdata["data"]["id"]
        resp = client.put(f"/api/requests/{request_id}/reject",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["status"] == "rejected"

    def test_cannot_reject_already_rejected(self, client, faculty_token):
        """Cannot reject a non-pending request."""
        # Find a rejected request
        resp = client.get("/api/requests?status=rejected",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        if data["data"]:
            req_id = data["data"][0]["id"]
            resp = client.put(f"/api/requests/{req_id}/reject",
                              headers=auth_header(faculty_token))
            assert resp.status_code == 400
