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
def test_create_billing(mock_kafka):
    payload = {
        "order_id": 2001,
        "customer_id": 801,
        "amount": 199.99,
        "status": "pending"
    }
    response = client.post("/billings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == 2001
    assert data["customer_id"] == 801
    assert data["amount"] == 199.99
    assert data["status"] == "pending"
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_billing_duplicate_order_id(mock_kafka):
    payload = {
        "order_id": 2002,
        "customer_id": 802,
        "amount": 99.99,
        "status": "pending"
    }
    response1 = client.post("/billings", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/billings", json=payload)
    assert response2.status_code in (400, 409)  # Depending on your implementation

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_billing_invalid_payload(mock_kafka):
    payload = {
        "order_id": 2003,
        # Missing customer_id and amount
        "status": "pending"
    }
    response = client.post("/billings", json=payload)
    assert response.status_code == 422

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_billings(mock_kafka):
    response = client.get("/billings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_billing(mock_kafka):
    payload = {
        "order_id": 2004,
        "customer_id": 804,
        "amount": 150.00,
        "status": "pending"
    }
    create_resp = client.post("/billings", json=payload)
    billing_id = create_resp.json()["id"]

    response = client.get(f"/billings/{billing_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 2004
    assert data["customer_id"] == 804

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_billing_not_found(mock_kafka):
    response = client.get("/billings/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_billing(mock_kafka):
    payload = {
        "order_id": 2005,
        "customer_id": 805,
        "amount": 175.00,
        "status": "pending"
    }
    create_resp = client.post("/billings", json=payload)
    billing_id = create_resp.json()["id"]

    update_payload = {"status": "paid"}
    update_resp = client.put(f"/billings/{billing_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "paid"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_billing_not_found(mock_kafka):
    update_payload = {"status": "cancelled"}
    response = client.put("/billings/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_billing(mock_kafka):
    payload = {
        "order_id": 2006,
        "customer_id": 806,
        "amount": 60.00,
        "status": "pending"
    }
    create_resp = client.post("/billings", json=payload)
    billing_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/billings/{billing_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Billing deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_billing_not_found(mock_kafka):
    response = client.delete("/billings/999999")
    assert response.status_code == 404
