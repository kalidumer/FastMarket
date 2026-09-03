import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token"
    return {"Authorization": f"Bearer {mock_token}"}