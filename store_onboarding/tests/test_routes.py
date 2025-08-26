from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

def mock_send_event(*args, **kwargs):
    return None

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_health_check(mock_kafka):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_store(mock_kafka):
    payload = {
        "name": "Test Store",
        "owner": "Alice",
        "address": "123 Market St",
        "contact": "alice@example.com",
        "status": "pending"
    }
    response = client.post("/stores", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Store"
    assert data["owner"] == "Alice"
    assert data["status"] == "pending"
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_store_duplicate_name(mock_kafka):
    payload = {
        "name": "Unique Store",
        "owner": "Bob",
        "address": "456 Unique Ave",
        "contact": "bob@example.com",
        "status": "pending"
    }
    response1 = client.post("/stores", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/stores", json=payload)
    assert response2.status_code in (400, 409)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_store_invalid_payload(mock_kafka):
    payload = {
        # Missing name
        "owner": "Charlie",
        "address": "789 Invalid Rd",
        "contact": "charlie@example.com"
    }
    response = client.post("/stores", json=payload)
    assert response.status_code == 422

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_stores(mock_kafka):
    response = client.get("/stores")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_store(mock_kafka):
    payload = {
        "name": "Get Store",
        "owner": "Diana",
        "address": "101 Get St",
        "contact": "diana@example.com",
        "status": "pending"
    }
    create_resp = client.post("/stores", json=payload)
    store_id = create_resp.json()["id"]

    response = client.get(f"/stores/{store_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Store"
    assert data["owner"] == "Diana"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_store_not_found(mock_kafka):
    response = client.get("/stores/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_store(mock_kafka):
    payload = {
        "name": "Update Store",
        "owner": "Eve",
        "address": "202 Update Ave",
        "contact": "eve@example.com",
        "status": "pending"
    }
    create_resp = client.post("/stores", json=payload)
    store_id = create_resp.json()["id"]

    update_payload = {"status": "approved"}
    update_resp = client.put(f"/stores/{store_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "approved"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_store_not_found(mock_kafka):
    update_payload = {"status": "rejected"}
    response = client.put("/stores/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_store(mock_kafka):
    payload = {
        "name": "Delete Store",
        "owner": "Frank",
        "address": "303 Delete Rd",
        "contact": "frank@example.com",
        "status": "pending"
    }
    create_resp = client.post("/stores", json=payload)
    store_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/stores/{store_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Store deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_store_not_found(mock_kafka):
    response = client.delete("/stores/999999")
    assert response.status_code == 404
