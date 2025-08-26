from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user():
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "ValidPass123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_register_user_duplicate():
    payload = {
        "username": "uniqueuser",
        "email": "uniqueuser@example.com",
        "password": "AnotherPass123"
    }
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/register", json=payload)
    assert response2.status_code in (400, 409)

def test_register_invalid_email():
    payload = {
        "username": "bademail",
        "email": "not-an-email",
        "password": "ValidPass123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422

def test_register_short_password():
    payload = {
        "username": "shortpass",
        "email": "shortpass@example.com",
        "password": "123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422

def test_register_long_password():
    payload = {
        "username": "longpass",
        "email": "longpass@example.com",
        "password": "a" * 129  # Assuming 128 is max allowed
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422

def test_register_missing_fields():
    payload = {
        "username": "missingfields"
        # Missing email and password
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422

def test_login_user():
    payload = {
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "MySecret123"
    }
    client.post("/register", json=payload)
    login_payload = {
        "username": "loginuser",
        "password": "MySecret123"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password():
    payload = {
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "RightPassword123"
    }
    client.post("/register", json=payload)
    login_payload = {
        "username": "wrongpassuser",
        "password": "WrongPassword"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code in (400, 401)

def test_login_nonexistent_user():
    login_payload = {
        "username": "nouser",
        "password": "irrelevant"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code in (400, 401)

def test_login_invalid_email_format():
    login_payload = {
        "username": "bademail",
        "password": "irrelevant"
    }
    # If your login expects email, adjust accordingly
    response = client.post("/login", json=login_payload)
    # Should be 422 if invalid email, else 400/401 if not found
    assert response.status_code in (400, 401, 422)

def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user():
    payload = {
        "username": "getuser",
        "email": "getuser@example.com",
        "password": "GetPass123"
    }
    create_resp = client.post("/register", json=payload)
    user_id = create_resp.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "getuser"
    assert data["email"] == "getuser@example.com"

def test_get_user_not_found():
    response = client.get("/users/999999")
    assert response.status_code == 404

def test_update_user():
    payload = {
        "username": "updateuser",
        "email": "updateuser@example.com",
        "password": "UpdatePass123"
    }
    create_resp = client.post("/register", json=payload)
    user_id = create_resp.json()["id"]

    update_payload = {"email": "newemail@example.com"}
    update_resp = client.put(f"/users/{user_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["email"] == "newemail@example.com"

def test_update_user_not_found():
    update_payload = {"email": "nouser@example.com"}
    response = client.put("/users/999999", json=update_payload)
    assert response.status_code == 404

def test_update_protected_fields():
    payload = {
        "username": "protecteduser",
        "email": "protecteduser@example.com",
        "password": "ProtectedPass123"
    }
    create_resp = client.post("/register", json=payload)
    user_id = create_resp.json()["id"]

    # Try to update username (should not be allowed)
    update_payload = {"username": "newusername"}
    update_resp = client.put(f"/users/{user_id}", json=update_payload)
    assert update_resp.status_code in (400, 403, 422)

def test_delete_user():
    payload = {
        "username": "deleteuser",
        "email": "deleteuser@example.com",
        "password": "DeletePass123"
    }
    create_resp = client.post("/register", json=payload)
    user_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "User deleted"

def test_delete_user_not_found():
    response = client.delete("/users/999999")
    assert response.status_code == 404
