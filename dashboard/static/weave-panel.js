// The Weave button and panel (P-005, edicts E-0107, E-0113): recent traced runs, every agent, and the eval
// scoreboard, fed by this dashboard's server (/api/weave/*). The browser never talks to W&B and never sees the
// key; deep links open wandb.ai in a new tab. Loaded by the floor, /scope, and /records. Private view only.
"use strict";
(function(){
if (window.weavePanel) return;
const css = document.createElement("style");
css.textContent = `
:root{--wv-bg:#121834;--wv-card:#1A2147;--wv-line:#2E3870;--wv-text:#E9ECF8;--wv-muted:#9AA3CF;--wv-ok:#4FD1C5;--wv-bad:#F07167;--wv-accent:#FFCC33;--wv-shadow:rgba(0,0,0,.5)}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]).wv-light{--wv-bg:#FFFFFF;--wv-card:#F4F5FB;--wv-line:#D8DCEC;--wv-text:#1B2046;--wv-muted:#5A607F;--wv-ok:#12806F;--wv-bad:#B3261E;--wv-accent:#9A6B00;--wv-shadow:rgba(20,24,60,.18)}}
.wv-btn{font:700 14px var(--display, system-ui);padding:8px 14px;border-radius:999px;border:1px solid var(--wv-line);background:#1B1407;color:#FFCC33;cursor:pointer;pointer-events:auto}
.wv-btn .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-left:7px;background:var(--wv-muted);vertical-align:middle}
.wv-btn .dot.on{background:#4FD1C5}.wv-btn .dot.off{background:#F07167}
.wv-float{position:fixed;top:12px;right:16px;z-index:44}
.wv-panel{position:fixed;top:0;right:0;bottom:0;width:min(460px,100vw);background:var(--wv-bg);color:var(--wv-text);border-left:1px solid var(--wv-line);
  box-shadow:-12px 0 32px var(--wv-shadow);z-index:46;display:flex;flex-direction:column;transform:translateX(105%);transition:transform .22s ease;font:14px/1.45 var(--ui, system-ui)}
.wv-panel.open{transform:none}
.wv-head{display:flex;align-items:center;gap:8px;padding:14px 16px 8px}.wv-head h2{margin:0;font:700 18px var(--display, system-ui);flex:1}
.wv-head button{background:none;border:0;color:var(--wv-muted);font:700 22px system-ui;cursor:pointer}
.wv-status{padding:0 16px 8px;color:var(--wv-muted);font-size:12.5px}
.wv-tabs{display:flex;gap:4px;padding:0 12px;border-bottom:1px solid var(--wv-line)}
.wv-tabs button{background:none;border:0;border-bottom:2px solid transparent;color:var(--wv-muted);font:600 13.5px var(--display, system-ui);padding:8px 10px;cursor:pointer}
.wv-tabs button[aria-selected="true"]{color:var(--wv-text);border-bottom-color:var(--wv-accent)}
.wv-body{flex:1;overflow:auto;padding:10px 12px 20px}
.wv-row{background:var(--wv-card);border:1px solid var(--wv-line);border-radius:10px;padding:8px 10px;margin:6px 0;display:grid;grid-template-columns:1fr auto;gap:2px 8px}
.wv-row .a{font:700 14px var(--display, system-ui)}.wv-row .m{color:var(--wv-muted);font-size:12.5px}.wv-row a{color:var(--wv-accent);font-size:12.5px;text-decoration:none}
.wv-row .pass{color:var(--wv-ok);font-weight:700}.wv-row .fail{color:var(--wv-bad);font-weight:700}
.wv-note{background:var(--wv-card);border:1px dashed var(--wv-line);border-radius:10px;padding:10px;color:var(--wv-muted);margin:6px 0}
.wv-note a,.wv-links a{color:var(--wv-accent)}.wv-links{display:flex;gap:12px;flex-wrap:wrap;padding:6px 16px 10px;font-size:13px}
.wv-filter{display:flex;gap:6px;align-items:center;margin:4px 0 8px;color:var(--wv-muted);font-size:13px}
.wv-filter select{background:var(--wv-card);color:var(--wv-text);border:1px solid var(--wv-line);border-radius:8px;padding:4px 6px}
.wv-glyph{pointer-events:none;animation:wvrise 2.6s ease-out forwards}
@keyframes wvrise{0%{opacity:0;transform:translateY(6px)}15%{opacity:1}100%{opacity:0;transform:translateY(-26px)}}
@media (prefers-reduced-motion:reduce){.wv-panel{transition:none}.wv-glyph{animation:none;opacity:.9}}
`;
document.head.appendChild(css);
if (!document.querySelector(".hud")) document.documentElement.classList.add("wv-light");   // /scope and /records follow the system theme

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const get = p => fetch(p, {cache:"no-store"}).then(r => r.json()).catch(() => ({live:false, error:"the dashboard didn't answer"}));
const ago = t => { if(!t) return "—"; const s = (Date.now() - new Date(t.endsWith("Z") || /[+-]\d\d:\d\d$/.test(t) ? t : t + "Z")) / 1000;
  return s < 90 ? `${Math.round(s)} s ago` : s < 5400 ? `${Math.round(s/60)} min ago` : s < 129600 ? `${Math.round(s/3600)} h ago` : `${Math.round(s/86400)} d ago`; };
const CASTS = () => (typeof CAST !== "undefined" ? CAST : {});   // the floor's cast, when there is one
const num = n => n == null ? "—" : n >= 1e6 ? (n/1e6).toFixed(1) + "M" : n >= 1e3 ? (n/1e3).toFixed(1) + "k" : String(n);

const P = document.createElement("aside"); P.className = "wv-panel"; P.setAttribute("aria-label", "Weave traces"); P.setAttribute("role", "dialog");
P.innerHTML = `<div class="wv-head"><h2>Weave</h2><button aria-label="Close">×</button></div>
  <div class="wv-status" id="wv-status">Checking the bridge…</div>
  <div class="wv-links" id="wv-links"></div>
  <div class="wv-tabs" role="tablist"><button role="tab" data-t="traces" aria-selected="true">Traces</button><button role="tab" data-t="agents" aria-selected="false">Agents</button><button role="tab" data-t="evals" aria-selected="false">Evals</button></div>
  <div class="wv-body" id="wv-body"></div>`;
document.body.appendChild(P);
P.addEventListener("keydown", e => { e.stopPropagation(); if(e.key === "Escape") close(); });
P.querySelector(".wv-head button").onclick = () => close();
let tab = "traces", agentFilter = "", STATUS = null;
P.querySelectorAll(".wv-tabs button").forEach(b => b.onclick = () => { tab = b.dataset.t; draw(); });

function links(L){ return L ? `<a href="${esc(L.agents)}" target="_blank" rel="noopener noreferrer">Agents ↗</a><a href="${esc(L.traces)}" target="_blank" rel="noopener noreferrer">Traces ↗</a><a href="${esc(L.evals)}" target="_blank" rel="noopener noreferrer">Evals ↗</a>` : ""; }
function offline(d){ return `<div class="wv-note">Weave isn't answering right now${d.error ? ` (${esc(d.error)})` : ""}. The links above still open the project on wandb.ai, and nothing here stops any agent.</div>`; }

async function status(){
  STATUS = await get("/api/weave/status");
  const s = STATUS, el = P.querySelector("#wv-status");
  if (s.error && !s.links){ el.textContent = s.error; return s; }
  el.innerHTML = !s.configured ? "Tracing isn't set up on this machine (no W&B key or no agents/.venv)."
    : `${s.bridge_running ? "Bridge running" : "Bridge not running"} · exported through event #${esc(s.last_exported_seq)} of #${esc(s.log_last_seq)}${s.waiting ? ` · ${esc(s.waiting)} waiting` : ""}${s.open_runs ? ` (${esc(s.open_runs)} runs still open)` : ""} · ${esc(num(s.exported_spans))} spans, ${esc(num(s.ops_sent))} ops · ${esc(s.mode)} mode${s.last_export ? ` · last export ${esc(ago(s.last_export))}` : ""}`;
  P.querySelector("#wv-links").innerHTML = links(s.links);
  document.querySelectorAll(".wv-btn .dot").forEach(d => { d.className = "dot " + (s.configured && s.bridge_running ? "on" : "off"); });
  return s;
}

async function draw(){
  P.querySelectorAll(".wv-tabs button").forEach(b => b.setAttribute("aria-selected", String(b.dataset.t === tab)));
  const body = P.querySelector("#wv-body"); body.innerHTML = `<div class="wv-note">Loading…</div>`;
  if (tab === "traces"){
    const d = await get(`/api/weave/recent?limit=30${agentFilter ? `&agent=${encodeURIComponent(agentFilter)}` : ""}`);
    const keys = [...new Set(Object.keys(CASTS()).concat(agentFilter ? [agentFilter] : []))].sort();
    body.innerHTML = `<div class="wv-filter">Agent <select id="wv-agent"><option value="">everyone</option>${keys.map(k => `<option value="${esc(k)}"${k === agentFilter ? " selected" : ""}>${esc(CASTS()[k]?.name || k)}</option>`).join("")}</select></div>` +
      (!d.live ? offline(d) : (d.runs || []).length ? d.runs.map(r => `<div class="wv-row"><span class="a">${esc(r.agent)}</span><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">Open ↗</a>
        <span class="m">${esc(ago(r.started))}${r.duration_s ? ` · ${esc(r.duration_s)} s` : ""}${r.model ? ` · ${esc(r.model)}` : ""}${r.output_tokens ? ` · ${esc(num(r.input_tokens))} in / ${esc(num(r.output_tokens))} out` : ""}</span><span class="m">${esc(r.status || "")}</span></div>`).join("")
        : `<div class="wv-note">No traced runs${agentFilter ? " for this agent" : ""} yet.</div>`);
    const sel = body.querySelector("#wv-agent"); if (sel) sel.onchange = () => { agentFilter = sel.value; draw(); };
  } else if (tab === "agents"){
    const d = await get("/api/weave/agents");
    body.innerHTML = !d.live ? offline(d) : (d.agents || []).sort((a, b) => (b.runs - a.runs)).map(a => `<div class="wv-row"><span class="a">${esc(CASTS()[a.agent]?.name || a.agent)}</span>
      <a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">View in Weave ↗</a><span class="m">${esc(a.runs)} turns · ${esc(num(a.spans))} spans · ${esc(num(a.output_tokens))} output tokens${a.errors ? ` · ${esc(a.errors)} errors` : ""}</span><span class="m">last ${esc(ago(a.last))}</span></div>`).join("");
  } else {
    const d = await get("/api/weave/evals");
    const E = d.evals || [];
    body.innerHTML = !d.live ? offline(d) : !E.length ? `<div class="wv-note">No eval results yet. Run <code>agents/bin/evals.sh</code>.</div>` :
      E.map(e => `<div class="wv-row"><span class="a">${esc(e.id)} · ${esc(e.name)}</span><span class="${e.passed ? "pass" : "fail"}">${e.passed ? "pass" : "FAIL"}</span>
        <span class="m">${esc(e.metric)} ${esc(e.value)}${e.ci ? ` (95% CI ${esc(e.ci[0])} to ${esc(e.ci[1])})` : ""} · threshold ${esc(e.threshold)} · n=${esc(e.n)}${e.dataset ? ` · ${esc(e.dataset)}` : ""}</span><span class="m">${esc(ago(e.ran_at))}</span></div>`).join("") +
      `<div class="wv-links"><a href="${esc(d.links?.evals || "")}" target="_blank" rel="noopener noreferrer">All evaluations in Weave ↗</a></div>`;
  }
}

function open(opts){ opts = opts || {}; if (opts.agent !== undefined){ agentFilter = opts.agent; tab = "traces"; } P.classList.add("open"); status(); draw(); P.querySelector(".wv-head button").focus(); }
function close(){ P.classList.remove("open"); }
window.weavePanel = {open, close, status};

// the button: in the floor's HUD, or floating on /scope and /records
function button(){
  if (document.querySelector(".wv-btn")) return;
  const b = document.createElement("button"); b.className = "wv-btn"; b.type = "button"; b.innerHTML = `Weave<span class="dot" aria-hidden="true"></span>`;
  b.title = "Traces, agents, and evals in W&B Weave (private view)"; b.onclick = () => P.classList.contains("open") ? close() : open();
  const hud = document.querySelector(".hud"), at = hud && (hud.querySelector('a[href="/scope"]') || null);
  if (hud){ at ? at.before(b) : hud.appendChild(b); } else { b.classList.add("wv-float"); document.body.appendChild(b); }
}
button(); status().then(s => { if (s && s.error && !s.links) document.querySelectorAll(".wv-btn").forEach(b => b.remove()); });   // public view: no button

// on the floor, a small Weave glyph rises over an agent when its run has just been exported
let lastSeq = null, lastCheck = new Date().toISOString();
async function watch(){
  if (!document.querySelector(".hud") || typeof AG === "undefined") return;
  const s = await get("/api/weave/status"); if (!s.configured) return;
  if (lastSeq !== null && s.last_exported_seq > lastSeq){
    const d = await get("/api/weave/recent?limit=15");
    for (const r of (d.runs || [])) if (r.started && r.started + "Z" > lastCheck && AG[r.agent]?.pos) glyph(r.agent);
  }
  lastSeq = s.last_exported_seq; lastCheck = new Date().toISOString();
}
function glyph(k){
  const p = AG[k].pos, NS = "http://www.w3.org/2000/svg", layer = document.querySelector("#whispers") || document.querySelector("#bubbles"); if (!layer) return;
  const g = document.createElementNS(NS, "g"); g.setAttribute("class", "wv-glyph"); g.setAttribute("aria-hidden", "true");
  g.innerHTML = `<circle cx="${p.x + 22}" cy="${p.y - 128}" r="10" fill="#1B1407" stroke="#FFCC33" stroke-width="1.5"/><text x="${p.x + 22}" y="${p.y - 124}" text-anchor="middle" font-size="11" font-weight="700" fill="#FFCC33" font-family="system-ui">W</text>`;
  layer.appendChild(g); setTimeout(() => g.remove(), 2700);
}
setInterval(watch, 30000); setTimeout(watch, 3000);
})();
