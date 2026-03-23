import pytest
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.anyio
async def test_health_check_success(client: AsyncClient):
    """Test health check returns 200 and OK status when DB is available."""
    # The integration test client uses an in-memory database which should be available
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


@pytest.mark.anyio
async def test_health_check_database_failure(client: AsyncClient):
    """Test health check returns 503 when database connection fails."""
    with patch("app.main.ping_database", return_value=False):
        response = await client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["detail"] == "Database connection unavailable"
