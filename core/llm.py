import json
import os

from openai import OpenAI


def available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def structured(system: str, user: str, schema: dict, cheap: bool = False) -> dict:
    """One call, JSON out, validated against `schema` by the API (strict mode)."""
    model = os.getenv("OPENAI_MODEL_CHEAP" if cheap else "OPENAI_MODEL") or ("gpt-6-luna" if cheap else "gpt-6.1-sol")
    client = OpenAI(timeout=45)
    resp = client.responses.create(
        model=model,
        instructions=system,
        input=user,
        text={"format": {"type": "json_schema", "name": "result", "schema": schema, "strict": True}},
    )
    data = json.loads(resp.output_text)
    data["_model"] = model
    return data
