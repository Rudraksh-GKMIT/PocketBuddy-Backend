
from fastapi.testclient import TestClient
  # adjust if your main file is in a different path
from ..main import app
client = TestClient(app)

def test_login_invalid_password():
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
