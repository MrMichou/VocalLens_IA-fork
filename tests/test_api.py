import pytest
from httpx import AsyncClient
from src.api.main import app

@pytest.mark.asyncio
async def test_query_validation():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/query", json={})
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_query_empty_question():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/query", json={"question": ""})
        assert response.status_code == 400  # Bad request