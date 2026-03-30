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


def test_status_endpoint() -> None:
    response = client.get("/api/status")
    assert response.status_code == 200

    payload = response.json()
    assert payload["app_name"] == "silode"
    assert isinstance(payload["models"], list)
    assert isinstance(payload["suggestions"], list)


def test_chat_endpoint() -> None:
    response = client.post(
        "/api/chat",
        json={
            "messages": [
                {"role": "user", "content": "Give me a clean one-line summary of Silode."}
            ]
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["message"]["role"] == "assistant"
    assert payload["message"]["content"]


def test_root_serves_desktop_ui() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Silode" in response.text
