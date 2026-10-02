"""Score the model and the baseline on the labeled samples, and freeze the model's answers for the demo.

    uv run python eval/evaluate.py

Writes data/eval.json (the number on screen) and data/precomputed.json (what the demo serves when DEMO_FROZEN=1).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from core import engine  # noqa: E402

samples = json.loads((ROOT / "data/samples.json").read_text())
precomputed, rows = {}, []

for s in samples:
    result = engine.analyze(s["text"])
    base = engine.baseline(s["text"])
    precomputed[s["id"]] = result
    rows.append({"id": s["id"], "label": s["label"], "model": result["outcome"], "baseline": base})
    mark = "ok " if result["outcome"] == s["label"] else "MISS"
    print(f"{mark} {s['id']:<8} label={s['label']:<8} model={result['outcome']:<8} baseline={base}")

n = len(rows)
summary = {
    "n": n,
    "model_correct": sum(r["model"] == r["label"] for r in rows),
    "baseline_correct": sum(r["baseline"] == r["label"] for r in rows),
    "model": precomputed[samples[0]["id"]].get("_model", "offline baseline"),
    "mode": precomputed[samples[0]["id"]]["mode"],
    "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "rows": rows,
}
(ROOT / "data/eval.json").write_text(json.dumps(summary, indent=2))
(ROOT / "data/precomputed.json").write_text(json.dumps(precomputed, indent=2))
print(f"\nmodel {summary['model_correct']}/{n}   baseline {summary['baseline_correct']}/{n}   ({summary['mode']})")
