"""Optional Supabase logging over the REST API. A no-op unless both env vars are set.

Create the table once in the Supabase SQL editor:
    create table runs (id bigserial primary key, created_at timestamptz default now(), input text, result jsonb);
"""

import os

import httpx


def save_run(text: str, result: dict) -> None:
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    if not (url and key):
        return
    try:
        httpx.post(
            f"{url}/rest/v1/runs",
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "return=minimal"},
            json={"input": text, "result": result},
            timeout=10,
        )
    except httpx.HTTPError:
        pass
