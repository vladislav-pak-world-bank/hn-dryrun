<!-- HERO:START -->
# Clearpay

Decides whether a supplier invoice should be paid, held, or disputed, and shows why.
<!-- HERO:END -->

## Run it

```bash
cp .env.example .env        # add OPENAI_API_KEY
uv sync
uv run uvicorn app:app --reload
# open http://localhost:8000
```

## How it works

- `core/engine.py` sends the case to the model with a strict JSON schema and returns an outcome, a confidence, and the evidence behind it.
- `engine.baseline()` is a simple rule a busy analyst would use. The screen shows both.
- `eval/evaluate.py` scores the model and the baseline on the labeled cases in `data/samples.json` and writes the number shown at the bottom of the screen.

```bash
uv run python eval/evaluate.py
uv run pytest -q
```

## What existed before the event

A generic FastAPI and static-page skeleton (server, fallback handling, evaluation runner, page layout) with no domain logic. The problem framing, schema, prompts, labeled data, baseline rule, and interface for this challenge were written during the hackathon. The commit history shows when.

## Deploy

```bash
vercel link --yes
vercel env add OPENAI_API_KEY production
vercel deploy --prod
```
