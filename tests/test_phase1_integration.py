"""
Phase 1 Integration Testing: Final & Definitive Version using TestClient

This test file provides a robust, end-to-end validation of the WebSocket
communication pipeline. It uses the officially recommended `TestClient` from FastAPI,
which correctly handles the application lifecycle and provides a stable, in-process
testing environment.

This version tests the refactored application, which resolves the circular
import issue by using a shared module.
"""

import pytest
from fastapi.testclient import TestClient
import json

# Import the configured FastAPI app from the refactored server
from src.websocket.server import app

# --- Definitive TestClient Fixture ---
@pytest.fixture(scope="module")
def client():
    """Provides a TestClient that manages the app's lifespan."""
    with TestClient(app) as c:
        yield c

# --- Main Test Class ---
class TestPhase1Integration:
    """End-to-end integration tests using the definitive TestClient."""

    def test_connection_and_registration(self, client):
        """Tests successful client connection and reception of agent registrations."""
        with client.websocket_connect("/ws") as websocket:
            # 1. Connection established message
            conn_msg = websocket.receive_json()
            assert conn_msg["type"] == "connection_established"

            # 2. Three agent registration messages
            registrations = [websocket.receive_json() for _ in range(3)]
            agent_ids = {msg["payload"]["agent_id"] for msg in registrations}
            assert agent_ids == {"dental_agent", "demo_agent", "opendental_agent"}

    def test_agent_activity_broadcast(self, client):
        """Tests that a simulated agent activity is correctly broadcast."""
        with client.websocket_connect("/ws") as websocket:
            # Clear initial messages
            for _ in range(4): websocket.receive_json()

            # Trigger the activity via the test-only HTTP endpoint
            activity_data = {"agent_id": "dental_agent", "title": "Live Test"}
            response = client.post("/testing/trigger-activity", json=activity_data)
            assert response.status_code == 200

            # Collect the 3 expected messages from the WebSocket
            messages = [websocket.receive_json() for _ in range(3)]
            received_types = [msg["type"] for msg in messages]

            assert "agent_status_update" in received_types
            assert "agent_activity" in received_types
            
            # The last status update should be IDLE
            status_updates = [m for m in messages if m["type"] == "agent_status_update"]
            assert status_updates[-1]["payload"]["status"] == "idle"

    def test_human_handoff_broadcast(self, client):
        """Tests that a human handoff request is correctly broadcast."""
        with client.websocket_connect("/ws") as websocket:
            # Clear initial messages
            for _ in range(4): websocket.receive_json()

            # Trigger handoff via the test-only HTTP endpoint
            handoff_data = {"agent_id": "demo_agent", "reason": "Live handoff test"}
            response = client.post("/testing/trigger-handoff", json=handoff_data)
            assert response.status_code == 200

            # Collect the 2 expected messages
            messages = [websocket.receive_json() for _ in range(2)]

            handoff_status = next((m for m in messages if m["type"] == "agent_status_update" and m["payload"]["status"] == "human_handoff"), None)
            handoff_required = next((m for m in messages if m["type"] == "human_handoff_required"), None)

            assert handoff_status is not None
            assert handoff_required is not None
            assert handoff_required["payload"]["agent_id"] == "demo_agent"

