from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


def test_get_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []
