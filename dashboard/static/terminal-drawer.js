// The web terminal drawer (P-001; Charter Article 18.7(c)(iii)): real shells on this machine, in xterm.js.
// Private view only. Each tab asks the server for a one-time token, then opens /ws/shell (same origin).
// Every session and typed line is recorded by the server; a closed session is never resumed, only replaced.
"use strict";
(function(){
if (new URLSearchParams(location.search).get("demo") === "1") return;       // no real shells in the simulation
const css = document.createElement("style");
css.textContent = `
.tdrawer{position:fixed;left:0;right:360px;bottom:0;height:42vh;min-height:180px;background:#0B0F24;border-top:1px solid var(--line);z-index:25;
  display:none;flex-direction:column;box-shadow:0 -10px 30px rgba(0,0,0,.45)}
.tdrawer.open{display:flex}.tdrawer.max{height:calc(100vh - 60px)}
.tgrip{height:6px;cursor:ns-resize;background:linear-gradient(var(--line),transparent)}
.tbar{display:flex;align-items:center;gap:6px;padding:4px 8px;border-bottom:1px solid var(--line);font:600 13px var(--display);color:var(--muted)}
.tbar .tab{padding:4px 10px;border-radius:8px 8px 0 0;cursor:pointer;color:var(--muted);border:1px solid transparent}
.tbar .tab.on{color:var(--text);border-color:var(--line);border-bottom-color:#0B0F24;background:#0B0F24}
.tbar .tab .x{margin-left:6px;opacity:.6}.tbar button{font:600 12.5px var(--display);background:none;border:1px solid var(--line);color:var(--text);border-radius:8px;padding:3px 9px;cursor:pointer}
.tbar .sp{flex:1}.tbar .warn{color:var(--wait);font-weight:500}
.tbody{flex:1;position:relative;min-height:0}.tpane{position:absolute;inset:4px 6px 6px;display:none}.tpane.on{display:block}
.tdead{position:absolute;inset:auto 12px 12px auto;background:#2B1F14;border:1px solid var(--wait);color:#FFD9A8;padding:8px 10px;border-radius:10px;font:500 13.5px var(--ui);z-index:3}
.tdead button{margin-left:8px;background:#F2B84B;border:0;border-radius:8px;padding:4px 10px;font:600 13px var(--display);cursor:pointer}
`;
document.head.appendChild(css);

let loaded = null;
function loadXterm(){
  if(loaded) return loaded;
  loaded = new Promise((res, rej) => {
    const l = document.createElement("link"); l.rel = "stylesheet"; l.href = "/vendor/xterm/xterm.css"; document.head.appendChild(l);
    const a = document.createElement("script"); a.src = "/vendor/xterm/xterm.js";
    a.onload = () => { const b = document.createElement("script"); b.src = "/vendor/xterm/addon-fit.js"; b.onload = res; b.onerror = rej; document.head.appendChild(b); };
    a.onerror = rej; document.head.appendChild(a);
  });
  return loaded;
}

const D = document.createElement("div"); D.className = "tdrawer"; D.setAttribute("role", "region"); D.setAttribute("aria-label", "Terminals");
D.innerHTML = `<div class="tgrip" title="Drag to resize"></div>
  <div class="tbar"><span>Terminals</span><span id="ttabs" style="display:flex;gap:4px"></span>
    <button id="t-shell" title="A login shell on this machine, in the Collective folder (recorded)">+ shell</button>
    <button id="t-herdr" title="The full herdr UI (recorded)">+ herdr</button><span class="warn">herdr may take over your own herdr window</span>
    <span class="sp"></span><span style="font-weight:500">Recorded: every session and typed line (passwords excepted)</span>
    <button id="t-max" title="Taller">▴</button><button id="t-close" title="Hide the drawer (terminals keep running)">✕</button></div>
  <div class="tbody" id="tbody"></div>`;
document.body.appendChild(D);
// keyboard stays in the terminal: the floor's shortcuts (Escape, agent keys) never fire while it has focus
D.addEventListener("keydown", e => e.stopPropagation());

const TABS = []; let active = null, n = 0;
function tabBar(){
  const bar = D.querySelector("#ttabs"); bar.innerHTML = "";
  for(const t of TABS){ const s = document.createElement("span"); s.className = "tab" + (t === active ? " on" : "");
    s.textContent = `${t.cmd} ${t.n}${t.dead ? " (ended)" : ""}`; const x = document.createElement("span"); x.className = "x"; x.textContent = "×"; x.title = "Close this terminal";
    x.onclick = e => { e.stopPropagation(); closeTab(t); }; s.appendChild(x); s.onclick = () => show(t); bar.appendChild(s); }
}
function show(t){ active = t; TABS.forEach(x => x.pane.classList.toggle("on", x === t)); tabBar(); if(t){ fit(t); t.term.focus(); } }
function fit(t){
  if(!t || !t.fitter) return;
  try { t.fitter.fit(); } catch(e) { return; }
  if(t.ws && t.ws.readyState === 1) t.ws.send(JSON.stringify({type:"resize", cols:t.term.cols, rows:t.term.rows}));
}
async function open(cmd){
  D.classList.add("open"); await loadXterm();
  const t = {cmd, n: ++n, dead:false}; const pane = document.createElement("div"); pane.className = "tpane"; D.querySelector("#tbody").appendChild(pane); t.pane = pane;
  t.term = new Terminal({cursorBlink:true, scrollback:5000, fontFamily:"ui-monospace, Menlo, monospace", fontSize:13.5,
                         theme:{background:"#0B0F24", foreground:"#E9ECF8", cursor:"#4FD1C5", selectionBackground:"#3A4C73"}});
  t.fitter = new FitAddon.FitAddon(); t.term.loadAddon(t.fitter); t.term.open(pane);
  t.term.onSelectionChange(() => { const s = t.term.getSelection(); if(s) navigator.clipboard?.writeText(s).catch(() => {}); });   // copy on selection
  TABS.push(t); show(t); connect(t);
}
async function connect(t){
  t.dead = false; t.pane.querySelector(".tdead")?.remove(); fit(t);
  let tok;
  try { tok = (await fetch("/api/shell/token", {cache:"no-store"}).then(r => r.json())).token; } catch(e) {}
  if(!tok){ t.term.write("\r\n\x1b[33mThe terminal is off here (public view, or the dashboard isn't reachable).\x1b[0m\r\n"); return dead(t); }
  const ws = new WebSocket(`ws://${location.host}/ws/shell?cmd=${t.cmd}&token=${encodeURIComponent(tok)}&cols=${t.term.cols}&rows=${t.term.rows}`);
  ws.binaryType = "arraybuffer"; t.ws = ws; const enc = new TextEncoder();
  ws.onopen = () => fit(t);
  ws.onmessage = e => t.term.write(typeof e.data === "string" ? e.data : new Uint8Array(e.data));
  ws.onclose = () => { if(t.ws === ws) dead(t); };
  t.inputSub?.dispose(); t.inputSub = t.term.onData(d => { if(ws.readyState === 1) ws.send(enc.encode(d)); });
}
function dead(t){
  t.dead = true; tabBar();
  const d = document.createElement("div"); d.className = "tdead";
  d.innerHTML = `This session has ended. <b>Reconnect</b> starts a new ${t.cmd === "herdr" ? "herdr" : "shell"}; it doesn't resume the old one.<button>Reconnect</button>`;
  d.querySelector("button").onclick = () => { t.term.write(`\r\n\x1b[90m--- a new ${t.cmd} session ---\x1b[0m\r\n`); connect(t); };
  t.pane.appendChild(d);
}
function closeTab(t){ try { t.ws?.close(); } catch(e) {} t.term.dispose(); t.pane.remove(); TABS.splice(TABS.indexOf(t), 1);
  if(active === t) show(TABS[TABS.length - 1] || null); tabBar(); if(!TABS.length) D.classList.remove("open"); }

D.querySelector("#t-shell").onclick = () => open("shell");
D.querySelector("#t-herdr").onclick = () => open("herdr");
D.querySelector("#t-close").onclick = () => D.classList.remove("open");
D.querySelector("#t-max").onclick = () => { D.classList.toggle("max"); D.querySelector("#t-max").textContent = D.classList.contains("max") ? "▾" : "▴"; setTimeout(() => fit(active), 60); };
// drag the grip to resize; the browser owns the size and tells the shell
const grip = D.querySelector(".tgrip");
grip.addEventListener("pointerdown", e => { grip.setPointerCapture(e.pointerId); const y0 = e.clientY, h0 = D.getBoundingClientRect().height;
  const move = ev => { D.classList.remove("max"); D.style.height = Math.max(160, Math.min(innerHeight - 60, h0 + (y0 - ev.clientY))) + "px"; fit(active); };
  const up = () => { grip.removeEventListener("pointermove", move); grip.removeEventListener("pointerup", up); fit(active); };
  grip.addEventListener("pointermove", move); grip.addEventListener("pointerup", up); });
window.addEventListener("resize", () => fit(active));

// the ⌨ button in the top bar opens the drawer (a new shell if none is open)
const hud = document.querySelector(".hud");
if(hud){ const b = document.createElement("button"); b.className = "hbtn"; b.style.background = "#0B0F24"; b.style.color = "var(--text)";
  b.textContent = "⌨ Terminal"; b.title = "A real terminal on this machine (private view, recorded)";
  b.onclick = () => { if(D.classList.contains("open") && TABS.length){ D.classList.remove("open"); return; } D.classList.add("open"); if(!TABS.length) open("shell"); else show(active || TABS[0]); };
  const after = document.querySelector("#reset-btn") || document.querySelector("#huddle-btn"); after ? after.after(b) : hud.appendChild(b); }
})();
