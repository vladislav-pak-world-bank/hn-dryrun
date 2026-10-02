"""The product. `analyze` is what the judge watches; `baseline` is what you beat."""

import re

from core import config, llm

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["outcome", "confidence", "summary", "evidence"],
    "properties": {
        "outcome": {"type": "string", "enum": config.OUTCOMES},
        "confidence": {"type": "number"},
        "summary": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["factor", "detail", "direction"],
                "properties": {
                    "factor": {"type": "string"},
                    "detail": {"type": "string"},
                    "direction": {"type": "string", "enum": ["supports", "against"]},
                },
            },
        },
    },
}


def baseline(text: str) -> str:
    """The dumb rule a busy human would use. Keep it honest: it is the number you compare against."""
    t = text.lower()
    if re.search(r"\b(fee|surcharge|penalty)\b", t):
        return "DISPUTE"
    if "missing" in t or "tbd" in t:
        return "HOLD"
    return "PAY"


def analyze(text: str) -> dict:
    if not llm.available():
        return {
            "outcome": baseline(text),
            "confidence": 0.0,
            "summary": "No OPENAI_API_KEY set, so this is the rule-based baseline, not the model.",
            "evidence": [],
            "mode": "offline",
        }
    result = llm.structured(config.SYSTEM_PROMPT, text, SCHEMA)
    result["mode"] = "live"
    return result
