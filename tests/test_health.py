from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True
