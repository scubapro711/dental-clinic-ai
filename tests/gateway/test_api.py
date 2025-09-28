import pytest


def test_get_queue_stats(client, mock_queue_manager):
    response = client.get("/api/queue/stats/test_queue")
    assert response.status_code == 200
    data = response.json()
    assert data["queue_name"] == "test_queue"
    assert data["pending"] == 10

def test_search_patients(client):
    response = client.post("/api/search_patients", json={"query": "test"})
    assert response.status_code == 200
    assert response.json() == {"message": "Search results for patients"}

def test_get_providers(client):
    response = client.post("/api/get_providers", json={})
    assert response.status_code == 200
    assert response.json() == {"message": "List of providers"}

def test_get_available_slots(client):
    response = client.post("/api/get_available_slots", json={"provider_id": 1, "date_str": "2025-10-01"})
    assert response.status_code == 200
    assert response.json() == {"message": "Available slots"}

def test_book_appointment(client):
    response = client.post("/api/book_appointment", json={"patient_id": 1, "provider_id": 1, "datetime_str": "2025-10-01T10:00:00", "treatment_type": "General Checkup"})
    assert response.status_code == 200
    assert response.json() == {"message": "Appointment booked"}




def test_get_message_status(client, mock_queue_manager):
    response = client.get("/api/queue/status/test_message_id")
    assert response.status_code == 200
    assert response.json() == {"status": "completed"}

def test_process_message(client, mock_queue_manager):
    response = client.post("/api/queue/process", json={"text": "test"})
    assert response.status_code == 200
    assert response.json() == {"message_id": "mock_message_id"}

