from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert "default_model" in payload


def test_tags_endpoint() -> None:
    response = client.get("/api/tags")
    assert response.status_code == 200

    payload = response.json()
    assert "models" in payload
    assert isinstance(payload["models"], list)


def test_generate_endpoint() -> None:
    response = client.post(
        "/api/generate",
        json={
            "prompt": "Say hello in one sentence.",
            "stream": False,
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["done"] is True
    assert payload["response"]
