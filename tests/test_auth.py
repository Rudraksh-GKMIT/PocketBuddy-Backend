import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app
import uuid

# -------------------------------------------------------------------
# Setup a temporary test database (SQLite for simplicity)
# -------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @pytest.fixture(autouse=True)
# def reset_db():
#     """Drop and recreate all tables before each test"""
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------------
# Dependency override — use test DB instead of real DB
# -------------------------------------------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# TestClient for making API requests
client = TestClient(app)

# -------------------------------------------------------------------
# Test Data
# -------------------------------------------------------------------
REGISTER_DATA = {
    "name": "Test",
    "email": f"{uuid.uuid4()}@example.com",
    "password": "Test@123",
    "family_name": "TestFamily",
}

LOGIN_DATA = {
    "email": "rudraksh_test@example.com",
    "password": "Test@123",
}

# -------------------------------------------------------------------
# Test Cases
# -------------------------------------------------------------------


def test_register_admin():
    """✅ Test successful admin registration"""
    response = client.post("/api/users/register", json=REGISTER_DATA)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
    assert "family_id" in data


def test_duplicate_email_registration():
    """❌ Test duplicate email registration"""
    response = client.post("/api/users/register", json=REGISTER_DATA)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_user():
    """✅ Test login for registered user"""
    response = client.post("/api/users/login", json=LOGIN_DATA)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_user():
    """❌ Test login with invalid credentials"""
    bad_login = {"email": "wrong@example.com", "password": "wrongpass"}
    response = client.post("/api/users/login", json=bad_login)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
