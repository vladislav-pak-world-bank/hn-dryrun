import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

from core import config, engine, llm, store, voice  # noqa: E402

app = FastAPI(title=config.PRODUCT_NAME)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


def _load(name: str, default):
    path = ROOT / "data" / name
    return json.loads(path.read_text()) if path.exists() else default


class RunIn(BaseModel):
    text: str
    sample_id: str | None = None


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True, "llm": llm.available(), "voice": voice.available(), "frozen": os.getenv("DEMO_FROZEN", "1") == "1"}


@app.get("/api/config")
def get_config():
    return {
        "name": config.PRODUCT_NAME,
        "tagline": config.TAGLINE,
        "user": config.USER,
        "outcomes": config.OUTCOMES,
        "input_label": config.INPUT_LABEL,
        "input_placeholder": config.INPUT_PLACEHOLDER,
        "sponsor_tool": config.SPONSOR_TOOL,
        "eleven_agent_id": os.getenv("ELEVENLABS_AGENT_ID", ""),
    }


@app.get("/api/samples")
def samples():
    return [{k: s[k] for k in ("id", "title", "text")} for s in _load("samples.json", [])]


@app.get("/api/eval")
def eval_summary():
    data = _load("eval.json", {})
    data.pop("rows", None)
    return data


@app.post("/api/run")
def run(body: RunIn):
    if not body.text.strip():
        raise HTTPException(400, "Empty input")
    frozen = _load("precomputed.json", {}) if os.getenv("DEMO_FROZEN", "1") == "1" else {}
    if body.sample_id and frozen.get(body.sample_id, {}).get("mode") == "live":
        result = {**frozen[body.sample_id], "served_from": "precomputed"}
    else:
        try:
            result = engine.analyze(body.text)
        except Exception as e:  # the demo must never show a stack trace
            result = {"outcome": engine.baseline(body.text), "confidence": 0.0, "evidence": [],
                      "summary": f"Model call failed ({type(e).__name__}). Showing the rule baseline.", "mode": "fallback"}
        result["served_from"] = "live"
    result["baseline"] = engine.baseline(body.text)
    store.save_run(body.text, result)
    return result


class SpeakIn(BaseModel):
    text: str


@app.post("/api/speak")
def speak(body: SpeakIn):
    if not voice.available():
        raise HTTPException(503, "ElevenLabs not configured")
    return Response(voice.speak(body.text), media_type="audio/mpeg")
