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
def test_create_order(mock_kafka):
    payload = {
        "customer_id": 301,
        "items": [
            {"product_id": "P100", "quantity": 2, "price": 25.0},
            {"product_id": "P200", "quantity": 1, "price": 50.0}
        ],
        "delivery_address": "123 Main St, Test City"
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == 301
    assert data["delivery_address"] == "123 Main St, Test City"
    assert len(data["items"]) == 2
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_order_invalid_payload(mock_kafka):
    payload = {
        # Missing customer_id
        "items": [{"product_id": "P101", "quantity": 1, "price": 20.0}],
        "delivery_address": "Missing Customer St"
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 422

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_orders(mock_kafka):
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_order(mock_kafka):
    payload = {
        "customer_id": 302,
        "items": [{"product_id": "P102", "quantity": 1, "price": 30.0}],
        "delivery_address": "456 Another St, Test City"
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["id"]

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 302

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_order_not_found(mock_kafka):
    response = client.get("/orders/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_order(mock_kafka):
    payload = {
        "customer_id": 303,
        "items": [{"product_id": "P103", "quantity": 2, "price": 15.0}],
        "delivery_address": "789 Update Ave, Test City"
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["id"]

    update_payload = {"status": "shipped"}
    update_resp = client.put(f"/orders/{order_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "shipped"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_order_not_found(mock_kafka):
    update_payload = {"status": "cancelled"}
    response = client.put("/orders/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_order(mock_kafka):
    payload = {
        "customer_id": 304,
        "items": [{"product_id": "P104", "quantity": 1, "price": 10.0}],
        "delivery_address": "321 Delete Rd, Test City"
    }
    create_resp = client.post("/orders", json=payload)
    order_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/orders/{order_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Order deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_order_not_found(mock_kafka):
    response = client.delete("/orders/999999")
    assert response.status_code == 404
