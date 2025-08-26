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
def test_create_product(mock_kafka):
    payload = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 19.99,
        "category": "Test Category",
        "stock": 100
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 19.99
    assert data["stock"] == 100
    assert mock_kafka.called

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_product_duplicate_name(mock_kafka):
    payload = {
        "name": "Unique Product",
        "description": "First instance",
        "price": 29.99,
        "category": "Unique",
        "stock": 10
    }
    response1 = client.post("/products", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/products", json=payload)
    assert response2.status_code in (400, 409)  # Depending on implementation

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_create_product_invalid_payload(mock_kafka):
    payload = {
        "name": "Invalid Product"
        # Missing required fields like price, stock, etc.
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_list_products(mock_kafka):
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_product(mock_kafka):
    payload = {
        "name": "Get Product",
        "description": "Get this product",
        "price": 49.99,
        "category": "Get",
        "stock": 20
    }
    create_resp = client.post("/products", json=payload)
    product_id = create_resp.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Product"
    assert data["price"] == 49.99

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_get_product_not_found(mock_kafka):
    response = client.get("/products/999999")
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_product(mock_kafka):
    payload = {
        "name": "Update Product",
        "description": "To be updated",
        "price": 59.99,
        "category": "Update",
        "stock": 15
    }
    create_resp = client.post("/products", json=payload)
    product_id = create_resp.json()["id"]

    update_payload = {"price": 79.99, "stock": 30}
    update_resp = client.put(f"/products/{product_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["price"] == 79.99
    assert data["stock"] == 30

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_update_product_not_found(mock_kafka):
    update_payload = {"price": 99.99}
    response = client.put("/products/999999", json=update_payload)
    assert response.status_code == 404

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_product(mock_kafka):
    payload = {
        "name": "Delete Product",
        "description": "To be deleted",
        "price": 9.99,
        "category": "Delete",
        "stock": 5
    }
    create_resp = client.post("/products", json=payload)
    product_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/products/{product_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Product deleted"

@patch("src.kafka_producer.kafka.send_event", side_effect=mock_send_event)
def test_delete_product_not_found(mock_kafka):
    response = client.delete("/products/999999")
    assert response.status_code == 404
