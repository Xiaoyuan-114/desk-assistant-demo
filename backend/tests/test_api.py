import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.llm import clear_llm_overlay
from app.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AGENT_LLM_API_KEY", "")
    get_settings.cache_clear()
    init_db()
    db = SessionLocal()
    try:
        clear_llm_overlay(db)
    finally:
        db.close()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_health_is_demo_and_open(client: TestClient) -> None:
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["data"]["demo"] is True


def test_llm_status_empty_without_env_key(client: TestClient) -> None:
    res = client.get("/api/v1/settings/llm")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["configured"] is False
    assert data["source"] == "none"
    assert data["last4"] is None


def test_chat_without_key_is_503(client: TestClient) -> None:
    res = client.post(
        "/api/v1/agent/chat",
        json={"messages": [{"role": "user", "content": "今天营业额是多少"}]},
    )
    assert res.status_code == 503
    assert "密钥" in res.json()["error"]
