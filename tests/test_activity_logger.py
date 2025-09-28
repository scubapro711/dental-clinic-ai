"""
Component 2.1 Test Suite: Aggressive Testing for Activity Logger

This test suite provides comprehensive, aggressive testing for the
Activity Logger backend component.

Test Coverage:
-   **Unit Tests:** Validate data models and individual functions.
-   **Integration Tests:** Ensure the API endpoints work correctly with the database.
-   **Performance Tests:** Stress test the logging endpoint to ensure it can handle
    a high volume of requests.
-   **Error Handling Tests:** Verify that the system handles invalid data gracefully.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import time

# Import the FastAPI app and other components from the main file
from src.activity_logger.main import app, Base, get_db

# --- Test Database Configuration ---
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Test Setup and Teardown ---
@pytest.fixture(scope="module")
def setup_database():
    """Create a fresh database for the test module."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"): 
        os.remove("./test.db")

@pytest.fixture(scope="function")
def db_session(setup_database):
    """Provide a database session for a single test function."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Provide a TestClient with an overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]

# --- Test Cases ---
class TestActivityLogger:
    """Test suite for the Activity Logger component."""

    def test_create_activity_log_success(self, client):
        """Tests successful creation of a single activity log."""
        activity_data = {
            "activity_id": "test-act-123",
            "agent_id": "test-agent-007",
            "activity_type": "DATA_ANALYSIS",
            "title": "Test Analysis",
            "description": "A successful test log entry.",
            "confidence_score": 0.99
        }
        response = client.post("/activities/log", json=activity_data)
        assert response.status_code == 200
        data = response.json()
        assert data["activity_id"] == "test-act-123"
        assert data["agent_id"] == "test-agent-007"
        assert "id" in data
        assert "timestamp" in data

    def test_get_agent_logs(self, client):
        """Tests retrieving logs for a specific agent."""
        # First, create some logs
        client.post("/activities/log", json={"activity_id": "ag1-1", "agent_id": "agent-1", "activity_type": "T1", "title": "T", "description": "D"})
        client.post("/activities/log", json={"activity_id": "ag2-1", "agent_id": "agent-2", "activity_type": "T1", "title": "T", "description": "D"})
        client.post("/activities/log", json={"activity_id": "ag1-2", "agent_id": "agent-1", "activity_type": "T2", "title": "T", "description": "D"})

        # Retrieve logs for agent-1
        response = client.get("/activities/logs/agent-1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert {log["activity_id"] for log in data} == {"ag1-1", "ag1-2"}

    def test_create_log_invalid_data(self, client):
        """Tests that the endpoint rejects requests with missing required fields."""
        invalid_data = {
            "agent_id": "test-agent-007",
            "title": "Invalid Log"
        }
        response = client.post("/activities/log", json=invalid_data)
        assert response.status_code == 422 # Unprocessable Entity

    @pytest.mark.performance
    def test_logging_performance(self, client):
        """Aggressive performance test: Log 100 activities in under 2 seconds."""
        start_time = time.time()
        for i in range(100):
            activity_data = {
                "activity_id": f"perf-test-{i}",
                "agent_id": "perf-agent",
                "activity_type": "PERF_TEST",
                "title": f"Performance Test {i}",
                "description": "High-volume logging test."
            }
            response = client.post("/activities/log", json=activity_data)
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n[Performance] Logged 100 activities in {duration:.2f} seconds.")
        assert duration < 2.0, "Logging 100 activities took too long!"

