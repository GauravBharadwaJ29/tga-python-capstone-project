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
def test_create_inventory_item(mock_kafka):
    payload = {
        "product_id": "P5001",
        "quantity": 100,
        "warehouse": "Main Warehouse"
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == "P5001"
    assert data["quantity"] == 100
    assert data["warehouse"] == "Main Warehouse"
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_inventory_item_duplicate(mock_kafka):
    payload = {
        "product_id": "P5002",
        "quantity": 50,
        "warehouse": "Secondary Warehouse"
    }
    response1 = client.post("/inventory", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/inventory", json=payload)
    assert response2.status_code in (400, 409)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_inventory_item_invalid_payload(mock_kafka):
    payload = {
        # Missing product_id
        "quantity": 25,
        "warehouse": "Missing Product"
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 422

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_inventory(mock_kafka):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_inventory_item(mock_kafka):
    payload = {
        "product_id": "P5003",
        "quantity": 75,
        "warehouse": "Get Warehouse"
    }
    create_resp = client.post("/inventory", json=payload)
    item_id = create_resp.json()["id"]

    response = client.get(f"/inventory/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "P5003"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_inventory_item_not_found(mock_kafka):
    response = client.get("/inventory/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_inventory_item(mock_kafka):
    payload = {
        "product_id": "P5004",
        "quantity": 120,
        "warehouse": "Update Warehouse"
    }
    create_resp = client.post("/inventory", json=payload)
    item_id = create_resp.json()["id"]

    update_payload = {"quantity": 200}
    update_resp = client.put(f"/inventory/{item_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["quantity"] == 200

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_inventory_item_not_found(mock_kafka):
    update_payload = {"quantity": 10}
    response = client.put("/inventory/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_inventory_item(mock_kafka):
    payload = {
        "product_id": "P5005",
        "quantity": 15,
        "warehouse": "Delete Warehouse"
    }
    create_resp = client.post("/inventory", json=payload)
    item_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/inventory/{item_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Inventory item deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_inventory_item_not_found(mock_kafka):
    response = client.delete("/inventory/999999")
    assert response.status_code == 404
