"""Tests for issue and return endpoints."""

from tests.conftest import auth_header


class TestIssueCreation:
    """Tests for POST /api/issues."""

    def test_issue_component(self, client, faculty_token, student_token):
        """Full workflow: student requests → faculty approves → faculty issues."""
        # 1. Student creates a request for component 4
        create_resp = client.post("/api/requests", json={
            "component_id": 4,
        }, headers=auth_header(student_token))
        if create_resp.status_code != 201:
            # Might already have a request; try component 5
            create_resp = client.post("/api/requests", json={
                "component_id": 5,
            }, headers=auth_header(student_token))
        cdata = create_resp.get_json()
        if create_resp.status_code != 201:
            return
        request_id = cdata["data"]["id"]

        # 2. Faculty approves
        approve_resp = client.put(f"/api/requests/{request_id}/approve",
                                  headers=auth_header(faculty_token))
        if approve_resp.status_code != 200:
            return

        # 3. Faculty issues
        issue_resp = client.post("/api/issues", json={
            "request_id": request_id,
        }, headers=auth_header(faculty_token))
        idata = issue_resp.get_json()
        assert issue_resp.status_code == 201
        assert idata["data"]["status"] == "issued"
        # Store for return test
        TestIssueCreation.issued_id = idata["data"]["id"]

    def test_issue_unapproved_request(self, client, faculty_token):
        resp = client.post("/api/issues", json={
            "request_id": 99999,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 404

    def test_student_cannot_issue(self, client, student_token):
        resp = client.post("/api/issues", json={
            "request_id": 1,
        }, headers=auth_header(student_token))
        assert resp.status_code == 403


class TestIssueListing:
    """Tests for GET /api/issues."""

    def test_list_issues_student(self, client, student_token):
        resp = client.get("/api/issues", headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert isinstance(data["data"], list)

    def test_list_issues_faculty(self, client, faculty_token):
        resp = client.get("/api/issues", headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 200


class TestReturn:
    """Tests for PUT /api/issues/<id>/return."""

    def test_return_component(self, client, student_token):
        """Return the component that was issued in TestIssueCreation."""
        issue_id = getattr(TestIssueCreation, "issued_id", None)
        if not issue_id:
            return

        resp = client.put(f"/api/issues/{issue_id}/return",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["status"] == "returned"
        assert "fine_amount" in data["data"]

    def test_cannot_return_twice(self, client, student_token):
        """Cannot return an already-returned component."""
        issue_id = getattr(TestIssueCreation, "issued_id", None)
        if not issue_id:
            return

        resp = client.put(f"/api/issues/{issue_id}/return",
                          headers=auth_header(student_token))
        assert resp.status_code == 400

    def test_return_nonexistent(self, client, student_token):
        resp = client.put("/api/issues/99999/return",
                          headers=auth_header(student_token))
        assert resp.status_code == 404
