const $ = (id) => document.getElementById(id);
let cfg = null;
let activeSample = null;

async function getJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${url} ${r.status}`);
  return r.json();
}

async function boot() {
  cfg = await getJSON("/api/config");
  document.title = cfg.name;
  $("name").textContent = cfg.name;
  $("tagline").textContent = cfg.tagline;
  $("input-label").textContent = cfg.input_label;
  $("input").placeholder = cfg.input_placeholder;

  const h = await getJSON("/api/health");
  $("health").textContent = h.llm ? `Model: live · ${h.frozen ? "samples frozen" : "all live"}` : "Model: offline (no API key)";

  const samples = await getJSON("/api/samples");
  for (const s of samples) {
    const b = document.createElement("button");
    b.textContent = s.title;
    b.onclick = () => {
      document.querySelectorAll(".samples button").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      activeSample = s.id;
      $("input").value = s.text;
    };
    $("samples").appendChild(b);
  }
  $("input").addEventListener("input", () => { activeSample = null; });

  const ev = await getJSON("/api/eval");
  if (ev.n) {
    const pct = (k) => Math.round((100 * ev[k]) / ev.n);
    $("eval").innerHTML =
      `<span>Model <b>${ev.model_correct}/${ev.n}</b> (${pct("model_correct")}%)</span>` +
      `<span>Rule baseline <b>${ev.baseline_correct}/${ev.n}</b> (${pct("baseline_correct")}%)</span>` +
      `<span>${ev.model}</span><span>Labeled set, scored ${ev.run_at}</span>`;
  }

  if (cfg.eleven_agent_id) {
    const el = document.createElement("elevenlabs-convai");
    el.setAttribute("agent-id", cfg.eleven_agent_id);
    $("voice-slot").appendChild(el);
    const sc = document.createElement("script");
    sc.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
    sc.async = true;
    document.body.appendChild(sc);
  }
}

async function run() {
  const text = $("input").value;
  if (!text.trim()) return;
  $("run").disabled = true;
  $("served").textContent = "Running";
  try {
    const r = await getJSON("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, sample_id: activeSample }),
    });
    render(r);
  } catch (e) {
    $("served").textContent = "Request failed. Check the server log.";
  } finally {
    $("run").disabled = false;
  }
}

function render(r) {
  $("empty").hidden = true;
  $("result").hidden = false;
  const o = $("outcome");
  o.textContent = r.outcome;
  o.className = `outcome o${Math.max(0, cfg.outcomes.indexOf(r.outcome))}`;
  $("confidence").textContent = r.confidence ? `${Math.round(r.confidence * 100)}% confidence` : "";
  $("summary").textContent = r.summary;
  $("evidence").innerHTML = "";
  for (const e of r.evidence || []) {
    const tr = document.createElement("tr");
    for (const [cls, val] of [["", e.factor], ["", e.detail], ["dir", e.direction]]) {
      const td = document.createElement("td");
      if (cls) td.className = cls;
      td.textContent = val;
      tr.appendChild(td);
    }
    $("evidence").appendChild(tr);
  }
  $("baseline").textContent = r.baseline;
  $("served").textContent = r.served_from === "precomputed" ? "Served from the frozen evaluation run" : `Live · ${r.mode}`;
}

$("run").onclick = run;
boot();
