# tests/test_api.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_ticket():
    data = {
        "user_request": "Our supplier stopped deliveries despite the agreement.",
        "user_id": "123"
    }
    # New unified endpoint
    response = requests.post(f"{BASE_URL}/agent", json=data)
    assert response.status_code == 200
    assert response.json()["action"] == "CREATE_TICKET"