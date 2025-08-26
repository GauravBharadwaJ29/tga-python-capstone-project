from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_api_key_missing():
    response = client.get("/products")
    assert response.status_code == 422  # FastAPI will complain about missing header

def test_api_key_invalid():
    response = client.get("/products", headers={"x-api-key": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"]["error"]["code"] == 401
