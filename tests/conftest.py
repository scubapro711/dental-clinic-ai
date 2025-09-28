import pytest
from fastapi.testclient import TestClient
from src.gateway.main import create_app
from src.dependencies import get_queue_manager
from unittest.mock import MagicMock

@pytest.fixture(scope="module")
def client():
    app = create_app(include_startup_events=False)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_queue_manager(client):
    mock_qm = MagicMock()
    
    async def mock_get_queue_size(queue_name):
        return 10
    mock_qm.get_queue_size = mock_get_queue_size

    async def mock_enqueue(queue_name, message):
        return "mock_message_id"
    mock_qm.enqueue = mock_enqueue

    async def override_get_queue_manager():
        yield mock_qm

    client.app.dependency_overrides[get_queue_manager] = override_get_queue_manager
    yield mock_qm
    client.app.dependency_overrides = {}

