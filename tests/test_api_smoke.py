import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("LLM_PROVIDER", "demo")
os.environ.setdefault("AZURE_SQL_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=ragdb;Uid=user;Pwd=password;")

from fastapi.testclient import TestClient  # noqa: E402
from api import app  # noqa: E402


def test_home_endpoint_returns_expected_metadata():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"].startswith("Agente IA RAG")
    assert data["docs"] == "/docs"
    assert data["ask"] == "/ask"
