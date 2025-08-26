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
def test_create_payment(mock_kafka):
    payload = {
        "order_id": 1001,
        "amount": 99.99,
        "payment_method": "credit_card",
        "customer_id": 501
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == 1001
    assert data["amount"] == 99.99
    assert data["payment_method"] == "credit_card"
    assert data["customer_id"] == 501
    assert data["status"] == "successful"
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_payment_duplicate(mock_kafka):
    payload = {
        "order_id": 1002,
        "amount": 50.00,
        "payment_method": "paypal",
        "customer_id": 502
    }
    # First creation should succeed
    response1 = client.post("/payments", json=payload)
    assert response1.status_code == 201
    # Second creation with same order_id should fail (assuming idempotency)
    response2 = client.post("/payments", json=payload)
    assert response2.status_code in (400, 409)  # Depending on your implementation

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_payment_invalid_payload(mock_kafka):
    payload = {
        "order_id": 1003,
        # Missing amount
        "payment_method": "credit_card",
        "customer_id": 503
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_payments(mock_kafka):
    response = client.get("/payments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_payment(mock_kafka):
    payload = {
        "order_id": 1004,
        "amount": 75.50,
        "payment_method": "debit_card",
        "customer_id": 504
    }
    create_resp = client.post("/payments", json=payload)
    payment_id = create_resp.json()["id"]

    # Now fetch it
    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1004
    assert data["amount"] == 75.50

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_payment_not_found(mock_kafka):
    response = client.get("/payments/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_payment(mock_kafka):
    payload = {
        "order_id": 1005,
        "amount": 120.00,
        "payment_method": "upi",
        "customer_id": 505
    }
    create_resp = client.post("/payments", json=payload)
    payment_id = create_resp.json()["id"]

    # Update status to refunded
    update_payload = {"status": "refunded"}
    update_resp = client.put(f"/payments/{payment_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "refunded"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_payment_not_found(mock_kafka):
    update_payload = {"status": "failed"}
    response = client.put("/payments/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_payment(mock_kafka):
    payload = {
        "order_id": 1006,
        "amount": 10.00,
        "payment_method": "net_banking",
        "customer_id": 506
    }
    create_resp = client.post("/payments", json=payload)
    payment_id = create_resp.json()["id"]

    # Delete payment
    delete_resp = client.delete(f"/payments/{payment_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Payment deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_payment_not_found(mock_kafka):
    response = client.delete("/payments/999999")
    assert response.status_code == 404
