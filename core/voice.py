"""ElevenLabs text-to-speech. Delete this file if the brief has no voice component."""

import os

import httpx


def available() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY") and os.getenv("ELEVENLABS_VOICE_ID"))


def speak(text: str) -> bytes:
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]
    r = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "accept": "audio/mpeg"},
        json={"text": text, "model_id": os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")},
        timeout=60,
    )
    r.raise_for_status()
    return r.content
