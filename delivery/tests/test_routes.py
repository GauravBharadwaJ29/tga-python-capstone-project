from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

# Patch kafka.send_event for all tests to avoid real Kafka calls
def mock_send_event(*args, **kwargs):
    return None

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_health_check(mock_kafka):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_delivery(mock_kafka):
    payload = {
        "order_id": 201,
        "customer_id": 601,
        "delivery_address": "123 Main St, Test City",
        "items": [
            {"product_id": "P100", "quantity": 2, "price": 25.0},
            {"product_id": "P200", "quantity": 1, "price": 50.0}
        ]
    }
    response = client.post("/deliveries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == 201
    assert data["customer_id"] == 601
    assert data["delivery_address"] == "123 Main St, Test City"
    assert len(data["items"]) == 2
    assert data["status"] == "pending"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_delivery_duplicate_order_id(mock_kafka):
    payload = {
        "order_id": 202,
        "customer_id": 602,
        "delivery_address": "111 Duplicate St",
        "items": [{"product_id": "P101", "quantity": 1, "price": 20.0}]
    }
    # First creation should succeed
    response1 = client.post("/deliveries", json=payload)
    assert response1.status_code == 201
    # Second creation with same order_id should fail
    response2 = client.post("/deliveries", json=payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_delivery_invalid_payload(mock_kafka):
    payload = {
        "order_id": 203,
        # Missing customer_id
        "delivery_address": "No Customer St"
    }
    response = client.post("/deliveries", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_deliveries(mock_kafka):
    response = client.get("/deliveries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_delivery(mock_kafka):
    payload = {
        "order_id": 204,
        "customer_id": 604,
        "delivery_address": "456 Another St, Test City",
        "items": [
            {"product_id": "P101", "quantity": 1, "price": 30.0}
        ]
    }
    create_resp = client.post("/deliveries", json=payload)
    delivery_id = create_resp.json()["id"]

    # Now fetch it
    response = client.get(f"/deliveries/{delivery_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 204
    assert data["customer_id"] == 604

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_delivery_not_found(mock_kafka):
    response = client.get("/deliveries/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Delivery not found"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_delivery(mock_kafka):
    payload = {
        "order_id": 205,
        "customer_id": 605,
        "delivery_address": "789 Update Ave, Test City",
        "items": [
            {"product_id": "P102", "quantity": 3, "price": 10.0}
        ]
    }
    create_resp = client.post("/deliveries", json=payload)
    delivery_id = create_resp.json()["id"]

    # Update status and assigned_to
    update_payload = {"status": "shipped", "assigned_to": "driver_1"}
    update_resp = client.put(f"/deliveries/{delivery_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "shipped"
    assert data["assigned_to"] == "driver_1"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_delivery_not_found(mock_kafka):
    update_payload = {"status": "delivered", "assigned_to": "driver_x"}
    response = client.put("/deliveries/999999", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Delivery not found"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_delivery(mock_kafka):
    payload = {
        "order_id": 206,
        "customer_id": 606,
        "delivery_address": "321 Delete Rd, Test City",
        "items": [
            {"product_id": "P103", "quantity": 1, "price": 15.0}
        ]
    }
    create_resp = client.post("/deliveries", json=payload)
    delivery_id = create_resp.json()["id"]

    # Delete delivery
    delete_resp = client.delete(f"/deliveries/{delivery_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Delivery deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_delivery_not_found(mock_kafka):
    response = client.delete("/deliveries/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Delivery not found"
