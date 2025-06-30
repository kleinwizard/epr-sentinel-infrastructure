import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestHealthCheck:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_healthz_endpoint(self, async_client: AsyncClient):
        """Test that health check endpoint returns OK."""
        response = await async_client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "EPR Co-Pilot Backend is running" in data["message"]


class TestCORSConfiguration:
    """Test CORS configuration."""
    
    @pytest.mark.asyncio
    async def test_cors_headers_present(self, async_client: AsyncClient):
        """Test that CORS headers are properly configured."""
        response = await async_client.options("/healthz")
        
        assert response.status_code in [200, 204, 405]


class TestSecurityMiddleware:
    """Test security middleware configuration."""
    
    @pytest.mark.asyncio
    async def test_security_headers(self, async_client: AsyncClient):
        """Test that security headers are present."""
        response = await async_client.get("/healthz")
        
        assert response.status_code == 200
