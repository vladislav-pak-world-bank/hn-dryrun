import inspect
import json

from fastapi.testclient import TestClient
from openai.resources.responses import Responses

import app as app_module
from core import engine, llm

client = TestClient(app_module.app)


def test_pages_and_config():
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json()["ok"] is True
    assert client.get("/api/config").json()["outcomes"]
    assert len(client.get("/api/samples").json()) >= 3


def test_run_offline_falls_back_to_baseline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DEMO_FROZEN", "0")
    r = client.post("/api/run", json={"text": "Invoice adds a late fee"}).json()
    assert r["outcome"] == "DISPUTE" and r["mode"] == "offline"


def test_run_never_500s_when_model_errors(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("DEMO_FROZEN", "0")
    monkeypatch.setattr(llm, "structured", lambda *a, **k: (_ for _ in ()).throw(TimeoutError()))
    r = client.post("/api/run", json={"text": "anything"})
    assert r.status_code == 200 and r.json()["mode"] == "fallback"


def test_llm_call_shape_matches_installed_sdk(monkeypatch):
    params = inspect.signature(Responses.create).parameters
    assert {"model", "instructions", "input", "text"} <= set(params)

    seen = {}

    class FakeResp:
        output_text = json.dumps({"outcome": "PAY", "confidence": 0.9, "summary": "ok", "evidence": []})

    class FakeClient:
        def __init__(self, **kw):
            self.responses = self

        def create(self, **kw):
            seen.update(kw)
            return FakeResp()

    monkeypatch.setattr(llm, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    out = engine.analyze("Invoice matches contract")
    assert out["outcome"] == "PAY" and out["mode"] == "live"
    assert seen["text"]["format"]["type"] == "json_schema" and seen["text"]["format"]["strict"] is True
