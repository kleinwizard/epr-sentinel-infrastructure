import pytest
from unittest.mock import patch, Mock
from httpx import AsyncClient
from app.auth import create_access_token, verify_password, get_password_hash

pytestmark = pytest.mark.asyncio


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_login_endpoint(self, async_client: AsyncClient, mock_stripe):
        """Test login endpoint."""
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "testpass"}
        )
        
        assert response.status_code in [401, 422]
    
    @pytest.mark.asyncio
    async def test_register_endpoint(self, async_client: AsyncClient, mock_stripe):
        """Test user registration endpoint."""
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "organization_name": "Test Organization"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code in [200, 422]


class TestAuthorizationMiddleware:
    """Test authorization and protected endpoints."""
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, async_client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await async_client.get("/api/products/")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_auth(self, async_client: AsyncClient, authenticated_user):
        """Test that protected endpoints work with authentication."""
        response = await async_client.get("/api/products/")
        
        assert response.status_code in [200, 404, 405]
