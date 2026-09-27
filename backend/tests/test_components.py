"""Tests for component endpoints."""

from tests.conftest import auth_header


class TestComponentListing:
    """Tests for GET /api/components."""

    def test_list_components(self, client, student_token):
        resp = client.get("/api/components", headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_list_components_with_borrowed_quantity(self, client, student_token):
        resp = client.get("/api/components", headers=auth_header(student_token))
        data = resp.get_json()
        for comp in data["data"]:
            assert "borrowed_quantity" in comp
            assert comp["borrowed_quantity"] == comp["total_quantity"] - comp["available_quantity"]

    def test_list_components_filter_status(self, client, student_token):
        resp = client.get("/api/components?status=active",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        for comp in data["data"]:
            assert comp["status"] == "active"

    def test_list_components_unauthenticated(self, client):
        resp = client.get("/api/components")
        assert resp.status_code == 401


class TestComponentSearch:
    """Tests for GET /api/components/search."""

    def test_search_components(self, client, student_token):
        resp = client.get("/api/components/search?q=Arduino",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data["data"]) > 0

    def test_search_empty_query(self, client, student_token):
        resp = client.get("/api/components/search?q=",
                          headers=auth_header(student_token))
        assert resp.status_code == 400

    def test_search_no_results(self, client, student_token):
        resp = client.get("/api/components/search?q=zzzznonexistent",
                          headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data["data"]) == 0


class TestComponentById:
    """Tests for GET /api/components/<id>."""

    def test_get_component(self, client, student_token):
        resp = client.get("/api/components/1", headers=auth_header(student_token))
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["id"] == 1

    def test_get_component_not_found(self, client, student_token):
        resp = client.get("/api/components/99999",
                          headers=auth_header(student_token))
        assert resp.status_code == 404


class TestComponentCreation:
    """Tests for POST /api/components."""

    def test_create_component_faculty(self, client, faculty_token):
        resp = client.post("/api/components", json={
            "component_code": "TEST-CREATE-001",
            "name": "Test Component",
            "category": "Testing",
            "total_quantity": 10,
            "available_quantity": 10,
            "description": "Created by test",
            "status": "active",
        }, headers=auth_header(faculty_token))
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["success"] is True

    def test_create_component_student_forbidden(self, client, student_token):
        resp = client.post("/api/components", json={
            "component_code": "TEST-STU-001",
            "name": "Student Component",
            "total_quantity": 5,
        }, headers=auth_header(student_token))
        assert resp.status_code == 403

    def test_create_component_duplicate_code(self, client, faculty_token):
        resp = client.post("/api/components", json={
            "component_code": "TEST-CREATE-001",
            "name": "Duplicate",
            "total_quantity": 5,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 409

    def test_create_component_invalid_quantity(self, client, faculty_token):
        resp = client.post("/api/components", json={
            "component_code": "TEST-INV-001",
            "name": "Invalid Qty",
            "total_quantity": 5,
            "available_quantity": 10,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 400

    def test_create_component_missing_fields(self, client, faculty_token):
        resp = client.post("/api/components", json={
            "category": "Testing",
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 400


class TestComponentUpdate:
    """Tests for PUT /api/components/<id>."""

    def test_update_component_faculty(self, client, faculty_token):
        # First find the test component
        resp = client.get("/api/components/search?q=TEST-CREATE-001",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        if data["data"]:
            comp_id = data["data"][0]["id"]
            resp = client.put(f"/api/components/{comp_id}", json={
                "component_code": "TEST-CREATE-001",
                "name": "Updated Test Component",
                "category": "Testing",
                "total_quantity": 15,
                "available_quantity": 15,
                "description": "Updated by test",
                "status": "active",
            }, headers=auth_header(faculty_token))
            assert resp.status_code == 200

    def test_update_component_not_found(self, client, faculty_token):
        resp = client.put("/api/components/99999", json={
            "component_code": "NOEXIST",
            "name": "Does Not Exist",
            "total_quantity": 5,
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 404


class TestComponentStatus:
    """Tests for PATCH /api/components/<id>/status."""

    def test_deactivate_component(self, client, faculty_token):
        resp = client.get("/api/components/search?q=TEST-CREATE-001",
                          headers=auth_header(faculty_token))
        data = resp.get_json()
        if data["data"]:
            comp_id = data["data"][0]["id"]
            resp = client.patch(f"/api/components/{comp_id}/status", json={
                "status": "inactive",
            }, headers=auth_header(faculty_token))
            assert resp.status_code == 200
            rdata = resp.get_json()
            assert rdata["data"]["status"] == "inactive"

            # Re-activate for other tests
            client.patch(f"/api/components/{comp_id}/status", json={
                "status": "active",
            }, headers=auth_header(faculty_token))

    def test_invalid_status(self, client, faculty_token):
        resp = client.patch("/api/components/1/status", json={
            "status": "broken",
        }, headers=auth_header(faculty_token))
        assert resp.status_code == 400

    def test_student_cannot_change_status(self, client, student_token):
        resp = client.patch("/api/components/1/status", json={
            "status": "inactive",
        }, headers=auth_header(student_token))
        assert resp.status_code == 403
