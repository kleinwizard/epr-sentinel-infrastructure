import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.schemas import User, Product, Material, Report
from app.auth import create_access_token
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def authenticated_user(client):
    """Create an authenticated user and return user data with auth headers"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"auth{unique_id}@example.com",
        "password": "authpassword123",
        "organization_name": "Auth Test Organization"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    user_response = response.json()

    return {
        "user": user_response,
        "headers": {"Authorization": f"Bearer {user_response['access_token']}"}
    }

@pytest.fixture
def auth_headers(authenticated_user):
    """Create authentication headers for testing"""
    return authenticated_user["headers"]

@pytest.fixture
def test_user(client):
    """Create a test user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test{unique_id}@example.com",
        "password": "testpassword123",
        "organization_name": "Test Organization"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    response_data = response.json()
    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "organization_name": user_data["organization_name"],
        "access_token": response_data["access_token"],
        "token_type": response_data["token_type"]
    }

@pytest.fixture
def test_product(client, auth_headers):
    """Create a test product"""
    import json
    product_data = {
        "name": "Test Product",
        "description": "A test product for integration testing",
        "category": "Electronics",
        "weight": 2.5,
        "material_composition": json.dumps({
            "plastic": 70,
            "metal": 30
        })
    }
    response = client.post("/api/products/", json=product_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()

class TestAuthEndpoints:
    """Test authentication and authorization endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "organization_name": "Test Organization"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user["email"],
            "password": "password123",
            "organization_name": "Another Organization"
        }
        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_valid_credentials(self, client, test_user):
        """Test login with valid credentials"""
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        login_data = {
            "email": test_user["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/products/")

        assert response.status_code == 403

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/products/", headers=headers)

        assert response.status_code == 401

class TestProductEndpoints:
    """Test product management endpoints"""

    def test_create_product(self, client, authenticated_user, auth_headers):
        """Test creating a new product"""
        product_data = {
            "name": "Integration Test Product",
            "sku": "TEST-PROD-001"
        }
        response = client.post("/api/products/", json=product_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["sku"] == product_data["sku"]
        assert "id" in data
        assert "created_at" in data
        assert "organization_id" in data

    def test_get_products_list(self, client, auth_headers, test_product):
        """Test retrieving products list"""
        response = client.get("/api/products/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        product_ids = [p["id"] for p in data]
        assert test_product["id"] in product_ids

    def test_get_product_by_id(self, client, auth_headers, test_product):
        """Test retrieving a specific product"""
        product_id = test_product["id"]
        response = client.get(f"/api/products/{product_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == test_product["name"]

    def test_get_nonexistent_product(self, client, auth_headers):
        """Test retrieving a non-existent product"""
        response = client.get("/api/products/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_product(self, client, auth_headers, test_product):
        """Test updating a product"""
        product_id = test_product["id"]
        update_data = {
            "name": "Updated Product Name",
            "description": "Updated description",
            "weight": 3.0
        }
        response = client.put(f"/api/products/{product_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["weight"] == update_data["weight"]

    def test_delete_product(self, client, auth_headers):
        """Test deleting a product"""
        import json
        product_data = {
            "name": "Product to Delete",
            "description": "This product will be deleted",
            "category": "Test",
            "weight": 1.0,
            "material_composition": json.dumps({"plastic": 100})
        }
        create_response = client.post("/api/products/", json=product_data, headers=auth_headers)
        product_id = create_response.json()["id"]

        response = client.delete(f"/api/products/{product_id}", headers=auth_headers)

        assert response.status_code == 204

        get_response = client.get(f"/api/products/{product_id}", headers=auth_headers)
        assert get_response.status_code == 404

class TestMaterialEndpoints:
    """Test material management endpoints"""

    def test_get_materials_list(self, client, auth_headers):
        """Test retrieving materials list"""
        response = client.get("/api/materials/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        material_names = [m["name"] for m in data]
        expected_materials = ["Paper (Label)", "Cardboard", "Plastic (PET)", "Glass", "Metal (Steel)"]
        for material in expected_materials:
            assert material in material_names

    def test_get_material_by_id(self, client, auth_headers):
        """Test retrieving a specific material"""
        list_response = client.get("/api/materials/", headers=auth_headers)
        materials = list_response.json()

        if materials:
            material_id = materials[0]["id"]
            response = client.get(f"/api/materials/{material_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == material_id

class TestFeeEndpoints:
    """Test EPR fee calculation endpoints"""

    def test_calculate_fees(self, client, auth_headers, test_product):
        """Test fee calculation for products"""
        params = {
            "products": [test_product["id"]],
            "period": "Q1-2024"
        }
        response = client.get("/api/fees/calculate", params=params, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_fee" in data
        assert "breakdown" in data
        assert isinstance(data["total_fee"], (int, float))
        assert data["total_fee"] >= 0

    def test_calculate_fees_multiple_products(self, client, auth_headers, test_product):
        """Test fee calculation for multiple products"""
        import json
        product_data = {
            "name": "Second Test Product",
            "description": "Another test product",
            "category": "Packaging",
            "weight": 1.0,
            "material_composition": json.dumps({"plastic": 50, "cardboard": 50})
        }
        second_product_response = client.post("/api/products/", json=product_data, headers=auth_headers)
        second_product = second_product_response.json()

        params = {
            "products": [test_product["id"], second_product["id"]],
            "period": "Q1-2024"
        }
        response = client.get("/api/fees/calculate", params=params, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_fee"] > 0
        assert len(data["breakdown"]) >= 2  # Should have breakdown for multiple materials

class TestReportEndpoints:
    """Test compliance report endpoints"""

    def test_get_reports_list(self, client, auth_headers):
        """Test retrieving reports list"""
        response = client.get("/api/reports/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_generate_report(self, client, auth_headers):
        """Test generating a new compliance report"""
        report_data = {
            "title": "Integration Test Report",
            "type": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        response = client.post("/api/reports/generate", json=report_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == report_data["title"]
        assert data["type"] == report_data["type"]
        assert "id" in data
        assert "status" in data

    def test_get_report_by_id(self, client, auth_headers):
        """Test retrieving a specific report"""
        report_data = {
            "title": "Test Report for Retrieval",
            "type": "quarterly",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31"
        }
        create_response = client.post("/api/reports/generate", json=report_data, headers=auth_headers)
        report_id = create_response.json()["id"]

        response = client.get(f"/api/reports/{report_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
        assert data["title"] == report_data["title"]

class TestHealthEndpoints:
    """Test health check and system status endpoints"""

    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_check(self, client):
        """Test readiness check endpoint"""
        response = client.get("/readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_json_payload(self, client, auth_headers):
        """Test handling of invalid JSON payload"""
        response = client.post(
            "/api/products/",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        incomplete_data = {
            "name": "Incomplete Product"
        }
        response = client.post("/api/products/", json=incomplete_data, headers=auth_headers)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_invalid_data_types(self, client, auth_headers):
        """Test handling of invalid data types"""
        invalid_data = {
            "name": "Test Product",
            "description": "Test description",
            "category": "Electronics",
            "weight": "invalid_weight",  # Should be a number
            "material_composition": {"plastic": 100}
        }
        response = client.post("/api/products/", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiting(self, client, auth_headers):
        """Test that rate limiting is enforced"""
        responses = []
        for i in range(100):  # Exceed rate limit
            response = client.get("/api/products/", headers=auth_headers)
            responses.append(response.status_code)
            if response.status_code == 429:  # Rate limited
                break

        assert 429 in responses

class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        response = client.options("/api/products/")

        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
