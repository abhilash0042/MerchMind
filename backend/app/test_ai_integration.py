import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_trigger():
    with patch("app.routes.ai.trigger_simulation", new_callable=AsyncMock) as mock:
        yield mock

@pytest.mark.asyncio
async def test_simulate_ai_endpoint(mock_trigger):
    # Mock the response from the AI Agents API
    mock_trigger.return_value = {
        "status": "success",
        "seller_id": "TEST_SELLER",
        "executive_plan": {
            "summary": "This is a mock plan",
            "actions": []
        }
    }
    
    # We also need to mock `embedding_service.store_insight` since it connects to the DB
    with patch("app.routes.ai.embedding_service.store_insight", new_callable=AsyncMock) as mock_store:
        response = client.post(
            "/ai/simulate",
            headers={"X-API-Key": "dev-api-key"},
            json={
                "seller_id": "TEST_SELLER",
                "time_window_start": "2026-02-01",
                "time_window_end": "2026-02-15",
                "snapshot_data": {"test": "data"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "executive_plan" in data
        
        # Verify the mock was called correctly
        mock_trigger.assert_called_once_with(
            seller_id="TEST_SELLER",
            time_window_start="2026-02-01",
            time_window_end="2026-02-15",
            snapshot_data={"test": "data"}
        )
        # Verify it attempted to save the insight
        mock_store.assert_called_once()

@pytest.fixture
def mock_stream_trigger():
    with patch("app.routes.ai.trigger_simulation_stream") as mock:
        yield mock

@pytest.mark.asyncio
async def test_simulate_ai_stream_endpoint(mock_stream_trigger):
    # Mock an async generator
    async def mock_generator():
        yield b'data: {"content": "Hello"}\n\n'
        yield b'data: {"content": " World"}\n\n'
        yield b'data: {"status": "done"}\n\n'
        
    mock_stream_trigger.return_value = mock_generator()
    
    with client.stream("POST", "/ai/simulate/stream", 
                    headers={"X-API-Key": "dev-api-key"},
                    json={
                        "seller_id": "TEST_SELLER",
                        "time_window_start": "2026-02-01",
                        "time_window_end": "2026-02-15",
                        "snapshot_data": {}
                    }) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        chunks = list(response.iter_bytes())
        assert len(chunks) == 3
        assert b'Hello' in chunks[0]
        assert b'World' in chunks[1]
        assert b'done' in chunks[2]

@pytest.fixture
def mock_whatif_stream_trigger():
    with patch("app.routes.ai.trigger_whatif_stream") as mock:
        yield mock

@pytest.mark.asyncio
async def test_simulate_ai_whatif_stream_endpoint(mock_whatif_stream_trigger):
    # Mock an async generator
    async def mock_generator():
        yield b'data: {"content": "Simulation"}\n\n'
        yield b'data: {"content": " Results"}\n\n'
        yield b'data: {"status": "done"}\n\n'
        
    mock_whatif_stream_trigger.return_value = mock_generator()
    
    with client.stream("POST", "/ai/whatif", 
                    headers={"X-API-Key": "dev-api-key"},
                    json={
                        "seller_id": "TEST_SELLER",
                        "scenario": "What if I drop my price 10%?"
                    }) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Read the streamed chunks
        chunks = list(response.iter_bytes())
        assert len(chunks) == 3
        assert b'Simulation' in chunks[0]
        assert b'Results' in chunks[1]
        assert b'done' in chunks[2]
