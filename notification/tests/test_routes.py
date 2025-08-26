from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_notification():
    payload = {
        "recipient": "user@example.com",
        "message": "Your order has shipped!",
        "type": "email"
    }
    response = client.post("/notifications", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["recipient"] == "user@example.com"
    assert data["message"] == "Your order has shipped!"
    assert data["type"] == "email"

def test_create_notification_invalid_payload():
    payload = {
        # Missing recipient
        "message": "Missing recipient",
        "type": "email"
    }
    response = client.post("/notifications", json=payload)
    assert response.status_code == 422

def test_list_notifications():
    response = client.get("/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_notification():
    payload = {
        "recipient": "getuser@example.com",
        "message": "Get this notification",
        "type": "sms"
    }
    create_resp = client.post("/notifications", json=payload)
    notification_id = create_resp.json()["id"]

    response = client.get(f"/notifications/{notification_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["recipient"] == "getuser@example.com"
    assert data["type"] == "sms"

def test_get_notification_not_found():
    response = client.get("/notifications/999999")
    assert response.status_code == 404

def test_update_notification():
    payload = {
        "recipient": "updateuser@example.com",
        "message": "To be updated",
        "type": "push"
    }
    create_resp = client.post("/notifications", json=payload)
    notification_id = create_resp.json()["id"]

    update_payload = {"message": "Updated message"}
    update_resp = client.put(f"/notifications/{notification_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["message"] == "Updated message"

def test_update_notification_not_found():
    update_payload = {"message": "Should not exist"}
    response = client.put("/notifications/999999", json=update_payload)
    assert response.status_code == 404

def test_delete_notification():
    payload = {
        "recipient": "deleteuser@example.com",
        "message": "To be deleted",
        "type": "email"
    }
    create_resp = client.post("/notifications", json=payload)
    notification_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/notifications/{notification_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Notification deleted"

def test_delete_notification_not_found():
    response = client.delete("/notifications/999999")
    assert response.status_code == 404
