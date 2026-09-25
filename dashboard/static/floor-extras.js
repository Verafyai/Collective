// The floor, version 003 (P-001): idle motion and blinking, status icons, drag and drop between rooms,
// "Open terminal", the Permissions tab, cleaner chats (avatars, summaries, Advanced, your comments),
// floating speech bubbles, whiteboards with kanban boards, the coffee machine and huddles, and a
// clearly labeled demo mode (?demo=1). Loaded after floor.html's own script; it extends its functions.
// Everything from the records is escaped (esc) or set as text; the only writes are the ones Charter
// Article 18.7 allows, and the server refuses them in public view.
"use strict";
(function(){
const DEMO = new URLSearchParams(location.search).get("demo") === "1";
const post = (p, body) => DEMO ? Promise.resolve({ok:false, error:"Simulation: nothing is written in demo mode."})
  : fetch(p, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body||{})}).then(r => r.json());
const NEUTRAL = new Set(["scribe","lawyer","auditor"]);
const STATE_ICON = {busy:["⚙️","Busy"], blocked:["⛔","Blocked"], approval:["✋","Awaiting approval"], instructions:["❓","Needs instructions"], scheduled:["⏰","Awaiting its next scheduled run"]};

// ---------- styles ----------
const css = document.createElement("style");
css.textContent = `
@media (prefers-reduced-motion:no-preference){
  .agent:not(.paused):not(.ghost):not(.working) .fig{animation:idlebob 3.4s ease-in-out infinite}
}
@keyframes idlebob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.5px)}}
.agent .eye{transition:ry .06s}
.agent.dragging{cursor:grabbing;transition:none!important;opacity:.92}
.agent.dragging .fig{animation:none}
.flag{cursor:help}.flag .lbl{opacity:0;transition:opacity .15s;pointer-events:none}
.agent:hover .flag .lbl,.flag:hover .lbl,.flag:focus .lbl{opacity:1}
.floater{pointer-events:none;animation:floatup 7s ease-out forwards}
@keyframes floatup{0%{opacity:0;transform:translateY(8px)}8%{opacity:1;transform:translateY(0)}80%{opacity:1}100%{opacity:0;transform:translateY(-18px)}}
.toast{position:fixed;left:50%;bottom:110px;transform:translateX(-50%);background:#161D3E;border:1px solid var(--line);color:var(--text);
  padding:10px 16px;border-radius:12px;font:500 14px var(--ui);z-index:40;box-shadow:0 8px 24px rgba(0,0,0,.4);max-width:min(560px,90vw)}
.toast.bad{border-color:var(--fail)}
.perm{display:grid;grid-template-columns:22px 1fr;gap:2px 8px;align-items:start;padding:8px 0;border-bottom:1px solid var(--line)}
.perm input{margin-top:3px}.perm .n{font:600 14px var(--display)}.perm .d{grid-column:2;font-size:12.5px;color:var(--muted)}
.perm.locked .n{color:var(--muted)}
.confirmbar{background:rgba(242,184,75,.12);border:1px solid var(--wait);border-radius:10px;padding:10px;margin:8px 0;font-size:13.5px}
.confirmbar .row{display:flex;gap:8px;margin-top:8px}
select.rank{background:#0F1430;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font:600 14px var(--display)}
.grouppick{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}.grouppick label{font-size:13px;display:flex;gap:4px;align-items:center}
.mini{width:30px;height:30px;flex:none}
.bub .sum{display:block}.bub details{margin-top:4px}.bub details summary{cursor:pointer;font-size:12.5px;color:#0A84FF;list-style:none}
.ph-row.me .bub details summary{color:#DDEBFF}.bub details summary::-webkit-details-marker{display:none}
.bub details pre{white-space:pre-wrap;font:12.5px/1.45 ui-monospace,Menlo,monospace;margin:6px 0 0;max-height:260px;overflow:auto}
.ph-compose{display:flex;flex-direction:column;gap:6px;width:100%}
.ph-compose textarea{width:100%;min-height:38px;max-height:120px;border:1px solid #D1D1D6;border-radius:18px;padding:8px 12px;font:15px var(--ui);resize:vertical;box-sizing:border-box}
.ph-compose .row{display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:#555}
.ph-compose button{background:#0A84FF;color:#fff;border:0;border-radius:16px;padding:6px 14px;font:600 14px var(--display);cursor:pointer}
.kanban{position:fixed;inset:0;background:rgba(6,9,24,.62);display:flex;align-items:center;justify-content:center;z-index:35;padding:16px}
.kb{width:min(1100px,100%);max-height:calc(100vh - 32px);overflow:auto;background:#F7F7F2;color:#1B2046;border-radius:14px;padding:16px 18px;border:10px solid #CFC9B8;box-shadow:0 20px 50px rgba(0,0,0,.5)}
.kb h3{margin:0 0 4px;font:700 20px var(--display)}.kb .sub{color:#5A607F;font-size:13px;margin-bottom:10px}
.kb table{border-collapse:separate;border-spacing:6px;width:100%}.kb th{font:700 13px var(--display);text-align:left;color:#5A607F}
.kb td{vertical-align:top;background:rgba(27,32,70,.04);border-radius:8px;min-width:120px;padding:4px}
.kb .lane{font:700 13px var(--display);background:none;white-space:nowrap}
.kb .card{background:#FFF9C4;border-radius:4px;padding:6px 8px;margin:4px 0;font-size:12.5px;box-shadow:0 1px 2px rgba(0,0,0,.15);transform:rotate(-.6deg)}
.kb .card:nth-child(2n){background:#D8F3FF;transform:rotate(.5deg)}.kb .card b{font-family:var(--display)}
.kb .x{float:right;background:none;border:0;font:700 20px var(--display);cursor:pointer;color:#5A607F}
.demo-badge{position:fixed;top:12px;left:50%;transform:translateX(-50%);background:#F2B84B;color:#0F1430;font:700 13px var(--display);letter-spacing:.06em;
  padding:6px 14px;border-radius:999px;z-index:50;box-shadow:0 4px 14px rgba(0,0,0,.4)}
.hbtn{font:700 14px var(--display);padding:8px 14px;border-radius:999px;border:1px solid var(--line);background:#2B1F14;color:#FFD9A8;cursor:pointer}
.hbtn.on{background:#F2B84B;color:#0F1430}
`;
document.head.appendChild(css);

function toast(msg, bad){ const t = document.createElement("div"); t.className = "toast" + (bad ? " bad" : ""); t.textContent = msg; t.setAttribute("role","status");
  document.body.appendChild(t); setTimeout(() => t.remove(), 4200); }

// ---------- idle motion and blinking (E-0067) ----------
function decorate(k){
  const a = AG[k]; if(!a || a.decorated) return;
  const fig = a.g.querySelector(".fig");
  fig.style.animationDelay = (-Math.random() * 3.4).toFixed(2) + "s";      // everyone bobs at their own rhythm
  fig.querySelectorAll("circle").forEach(c => {                               // the two eyes become ellipses that can close
    if(c.getAttribute("r") === "1.6"){ const e = document.createElementNS(NS, "ellipse");
      for(const at of ["cx","cy","fill"]) e.setAttribute(at, c.getAttribute(at)); e.setAttribute("rx", 1.6); e.setAttribute("ry", 1.6);
      e.setAttribute("class", "eye"); c.replaceWith(e); }
  });
  a.decorated = true; wireDrag(k);
}
const _makeAgent = makeAgent;
makeAgent = function(k){ _makeAgent(k); decorate(k); };
Object.keys(AG).forEach(decorate);
(function blinkLoop(){
  const keys = Object.keys(AG).filter(k => !AG[k].g.classList.contains("paused"));
  if(keys.length && !matchMedia("(prefers-reduced-motion: reduce)").matches){
    const k = keys[Math.floor(Math.random() * keys.length)], eyes = AG[k].g.querySelectorAll(".eye");
    eyes.forEach(e => e.setAttribute("ry", .25)); setTimeout(() => eyes.forEach(e => e.setAttribute("ry", 1.6)), 130);
    if(Math.random() < .2) setTimeout(() => { eyes.forEach(e => e.setAttribute("ry", .25)); setTimeout(() => eyes.forEach(e => e.setAttribute("ry", 1.6)), 110); }, 260);
  }
  setTimeout(blinkLoop, 700 + Math.random() * 1600);
})();

// ---------- rooms: where each agent stands follows the roster's room (E-0066) ----------
const roomOf = p => Object.keys(ROOMS).find(r => { const R = ROOMS[r]; return p.x >= R.x && p.x < R.x + R.w && p.y >= R.y && p.y < R.y + R.d; });
const _adopt = adoptRoster;
adoptRoster = function(roster){
  _adopt(roster);
  const taken = () => Object.keys(HOME).filter(k => AG[k]).map(k => iso(HOME[k].x, HOME[k].y));
  for(const a of roster) if(a.status !== "retired" && HOME[a.key] && a.room && roomOf(HOME[a.key]) !== a.room){
    const others = Object.keys(HOME).filter(k => k !== a.key && AG[k]).map(k => iso(HOME[k].x, HOME[k].y));
    HOME[a.key] = freeSlot(a.room, others);
  }
};

// ---------- drag and drop (E-0066; Article 18.7(c)) ----------
let drag = null, justDragged = false;
function svgPoint(ev){ const pt = svg.createSVGPoint(); pt.x = ev.clientX; pt.y = ev.clientY; return pt.matrixTransform(svg.getScreenCTM().inverse()); }
function wireDrag(k){
  const g = AG[k].g;
  g.addEventListener("pointerdown", ev => {
    if(ev.button !== 0 || huddleOpen() || (L && L.sprint && GOV.includes(L.sprint.phase))) return;
    drag = {k, start: svgPoint(ev), moved: false, id: ev.pointerId}; g.setPointerCapture(ev.pointerId);
  });
  g.addEventListener("pointermove", ev => {
    if(!drag || drag.k !== k) return;
    const p = svgPoint(ev);
    if(!drag.moved && Math.hypot(p.x - drag.start.x, p.y - drag.start.y) < 6) return;
    drag.moved = true; g.classList.add("dragging");
    g.style.transform = `translate(${p.x}px, ${p.y + 20}px) scale(1.4)`;
    const r = roomOf(toTile(p.x, p.y + 20)); highlightRoom(r);
  });
  g.addEventListener("pointerup", async ev => {
    if(!drag || drag.k !== k) return;
    const d = drag; drag = null; g.classList.remove("dragging"); highlightRoom(null);
    if(!d.moved) return;
    justDragged = true; setTimeout(() => justDragged = false, 50);
    const p = svgPoint(ev), room = roomOf(toTile(p.x, p.y + 20));
    if(!room || room === CAST[k].room){ render(); if(!room) toast("Drop an agent inside a room."); return; }
    const r = await post(`/api/agents/${k}/move`, {room});
    if(r.ok){ CAST[k].room = room; const others = Object.keys(HOME).filter(x => x !== k && AG[x]).map(x => iso(HOME[x].x, HOME[x].y));
      HOME[k] = freeSlot(room, others); const ro = (L.roster||[]).find(a => a.key === k); if(ro) ro.room = room;
      render(); toast(`${CAST[k].name} moved to the ${ROOMS[room].label}.`); }
    else { render(); toast(r.error || r.message || "Couldn't move the agent.", true); }
  });
  g.addEventListener("click", ev => { if(justDragged){ ev.stopImmediatePropagation(); ev.preventDefault(); } }, true);
}
let hl = null;
function highlightRoom(r){
  if(hl){ hl.remove(); hl = null; } if(!r) return;
  const R = ROOMS[r], a = iso(R.x, R.y), b = iso(R.x + R.w, R.y), c = iso(R.x + R.w, R.y + R.d), d = iso(R.x, R.y + R.d);
  hl = el("polygon", {points:[a,b,c,d].map(p => `${p.x},${p.y}`).join(" "), fill:"#fff", opacity:.08, stroke:"#fff", "stroke-width":2, "stroke-dasharray":"6 6"});
  svg.insertBefore(hl, $("#links"));
}

// ---------- status icons over heads (E-0073) ----------
function drawFlags(){
  for(const o of (L?.offices || [])){
    const a = AG[o.key]; if(!a) continue;
    a.g.querySelectorAll(".flag").forEach(f => f.remove());
    const fl = (o.flags || []).slice(0, 3);
    fl.forEach((f, i) => {
      const [icon, label] = STATE_ICON[f.kind] || ["•", f.kind];
      const x = (i - (fl.length - 1) / 2) * 22, g = el("g", {class:"flag", tabindex:0, transform:`translate(${x},-100)`}, a.g.querySelector(".fig"));
      el("circle", {r:10, fill:"#0F1430", stroke:"#fff", "stroke-opacity":.5}, g);
      const t = el("text", {y:4.5, "text-anchor":"middle", "font-size":12}, g); t.textContent = icon;
      const lb = el("g", {class:"lbl"}, g), txt = f.note || label, w = Math.min(260, txt.length * 6.4 + 16);
      el("rect", {x:-w/2, y:-40, width:w, height:22, rx:6, fill:"#0F1430", stroke:"var(--line)"}, lb);
      const tt = el("text", {y:-25, "text-anchor":"middle", fill:"#E9ECF8", "font-size":11.5, "font-family":"Barlow"}, lb); tt.textContent = txt.length > 40 ? txt.slice(0, 39) + "…" : txt;
      const ti = el("title", {}, g); ti.textContent = txt;
    });
  }
}

// ---------- the coffee machine and huddles (E-0076) ----------
const COFFEE = {x: 7.6, y: 10.9};
const huddleOpen = () => !!(L && L.huddle && L.huddle.open);
function drawCoffee(){
  const g = el("g", {id:"coffee", tabindex:0, role:"button", "aria-label":"Coffee machine: call a huddle", style:"cursor:pointer"});
  svg.insertBefore(g, $("#agents"));
  box(COFFEE.x - .3, COFFEE.y - .3, .6, .6, 30, "#5B4636", "#3A2C22", "#4A392C", g);
  const top = iso(COFFEE.x, COFFEE.y, 36);
  el("rect", {x:top.x - 7, y:top.y - 4, width:14, height:10, rx:2, fill:"#E8E2D6"}, g);
  const steam = el("text", {x:top.x, y:top.y - 10, "text-anchor":"middle", "font-size":18}, g); steam.textContent = "☕";
  const lab = iso(COFFEE.x + .7, COFFEE.y + .7); const t = el("text", {x:lab.x, y:lab.y + 16, "text-anchor":"middle", fill:"#FFD9A8", "font-family":"Barlow Semi Condensed", "font-size":13, "font-weight":700, opacity:.85}, g);
  t.textContent = "Coffee (huddle)";
  const ti = el("title", {}, g); ti.textContent = "Call a huddle: every agent answers here first on its next run";
  g.addEventListener("click", callHuddle); g.addEventListener("keydown", e => { if(e.key === "Enter" || e.key === " "){ e.preventDefault(); callHuddle(); } });
}
function huddleButton(){
  const hud = document.querySelector(".hud"); if(!hud || $("#huddle-btn")) return;
  const b = document.createElement("button"); b.id = "huddle-btn"; b.className = "hbtn"; b.textContent = "☕ Huddle";
  b.addEventListener("click", () => huddleOpen() ? closeHuddle() : callHuddle());
  const spacer = hud.querySelector(".spacer"); spacer ? spacer.after(b) : hud.appendChild(b);
}
async function callHuddle(){
  if(huddleOpen()){ openChat(L.huddle.id); return; }
  const topic = await ask("Call a huddle", "Everyone heads to the coffee machine and answers here first on their next run. What's it about?", "Quick huddle: where do things stand?");
  if(topic === null) return;
  const r = await post("/api/huddle", {topic});
  toast(r.ok ? r.message : (r.error || "Couldn't call the huddle."), !r.ok);
  if(r.ok){ await pollLive(); pollConvos(); }
}
async function closeHuddle(){ const r = await post("/api/huddle/close", {}); toast(r.ok ? r.message : (r.error || "Couldn't close it."), !r.ok); if(r.ok) pollLive(); }
function huddleSpot(i, n){   // a ring around the coffee machine, in screen space so nobody overlaps
  const c = iso(COFFEE.x, COFFEE.y), ang = (i / n) * Math.PI * 2 - Math.PI / 2, rx = 225, ry = 120;
  return toTile(c.x + Math.cos(ang) * rx, c.y + Math.sin(ang) * ry + 30);
}

// ---------- render: flags, huddle seating, whiteboards ----------
const _render = render;
render = function(){
  _render();
  if(!L) return;
  if(huddleOpen()){
    const keys = L.offices.map(o => o.key).filter(k => AG[k]);
    keys.forEach((k, i) => place(k, huddleSpot(i, keys.length), true)); sortDepth();
  }
  const hb = $("#huddle-btn"); if(hb){ hb.classList.toggle("on", huddleOpen()); hb.textContent = huddleOpen() ? "☕ Huddle open · close" : "☕ Huddle"; }
  drawFlags();
};

// ---------- whiteboards and the kanban (E-0075) ----------
const BOARD_AT = {council:{x:.5, y:3.4}, lab:{x:3.2, y:17.5}, studio:{x:17.5, y:3.2}, workshop:{x:17.5, y:14.4}};
function drawWhiteboards(){
  for(const [room, p] of Object.entries(BOARD_AT)){
    const g = el("g", {class:"wb", tabindex:0, role:"button", "aria-label":`${ROOMS[room].label} whiteboard: open the task board`, style:"cursor:pointer"});
    svg.insertBefore(g, $("#agents"));
    const along = p.x > 17 ? {w:.2, d:1.8} : {w:1.8, d:.2};
    box(p.x - along.w/2, p.y - along.d/2, along.w, along.d, 30, "#F4F6FF", "#AEB9CF", "#C7D0E2", g);
    const t = iso(p.x, p.y, 38); const tx = el("text", {x:t.x, y:t.y, "text-anchor":"middle", "font-size":13}, g); tx.textContent = "📋";
    const ti = el("title", {}, g); ti.textContent = "Task board (kanban)";
    g.addEventListener("click", () => openKanban(room)); g.addEventListener("keydown", e => { if(e.key === "Enter" || e.key === " "){ e.preventDefault(); openKanban(room); } });
  }
}
const COLS = [["open","Backlog"],["ready","Approved"],["started","In progress"],["blocked","Blocked"],["review","Review"],["done","Done"]];
async function openKanban(room){
  let tasks = [];
  try { tasks = await api("/api/tasks"); } catch(e) {}
  const inRoom = Object.keys(CAST).filter(k => CAST[k].room === room);
  const lanes = [...new Set(inRoom.concat(tasks.map(t => t.office || "unassigned")))].filter(k => tasks.some(t => (t.office || "unassigned") === k) || inRoom.includes(k));
  const w = document.createElement("div"); w.className = "kanban"; w.setAttribute("role","dialog"); w.setAttribute("aria-modal","true");
  w.innerHTML = `<div class="kb"><button class="x" aria-label="Close">×</button><h3>${esc(ROOMS[room].label)} whiteboard: the task board</h3>
    <div class="sub">${DEMO ? "SIMULATED tasks (demo mode). " : "Live from tsk (org/tasks). "}Columns are task states; lanes are offices, this room's first. ${tasks.length} task${tasks.length===1?"":"s"}.</div>
    <table><tr><th></th>${COLS.map(([,h]) => `<th>${h}</th>`).join("")}</tr>
    ${lanes.map(k => `<tr><td class="lane">${esc(CAST[k]?.icon || "")} ${esc(nm(k))}</td>${COLS.map(([s]) => `<td>${tasks.filter(t => (t.office || "unassigned") === k && t.state === s)
      .map(t => `<div class="card" title="${esc(t.notes)}"><b>T${esc(t.n)}</b> ${esc(t.title)}</div>`).join("")}</td>`).join("")}</tr>`).join("")
      || `<tr><td colspan="7" style="padding:20px">No tasks yet.</td></tr>`}</table></div>`;
  const close = () => w.remove();
  w.addEventListener("click", e => { if(e.target === w) close(); }); w.querySelector(".x").addEventListener("click", close);
  document.addEventListener("keydown", function esc1(e){ if(e.key === "Escape"){ close(); document.removeEventListener("keydown", esc1); } });
  document.body.appendChild(w); w.querySelector(".x").focus();
}

// ---------- a small, safe prompt (no browser dialogs) ----------
function ask(title, note, value){
  return new Promise(res => {
    const w = document.createElement("div"); w.className = "kanban";
    w.innerHTML = `<div class="kb" style="max-width:520px"><h3>${esc(title)}</h3><div class="sub">${esc(note)}</div>
      <textarea style="width:100%;min-height:80px;font:15px var(--ui);border-radius:8px;border:1px solid #CFC9B8;padding:8px;box-sizing:border-box"></textarea>
      <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:10px"><button class="btn ghost" style="color:#1B2046">Cancel</button><button class="btn">Call the huddle</button></div></div>`;
    const ta = w.querySelector("textarea"); ta.value = value || "";
    const [cancel, ok] = w.querySelectorAll("button");
    cancel.onclick = () => { w.remove(); res(null); }; ok.onclick = () => { const v = ta.value.trim(); w.remove(); res(v); };
    document.body.appendChild(w); ta.focus(); ta.select();
  });
}

// ---------- the bio: Open terminal and the Permissions tab (A-0021 18.8; A-0023) ----------
const PERMS = {}; let pending = null;
async function loadPerms(k){ try { PERMS[k] = await api(`/api/agents/${k}/permissions`); } catch(e) { PERMS[k] = {error:"Couldn't load permissions."}; } if(selected === k) side(); }
function permsHtml(k){
  const P = PERMS[k]; if(!P){ loadPerms(k); return `<p class="none">Loading permissions…</p>`; }
  if(P.error) return `<p class="none">${esc(P.error)}</p>`;
  const active = (L.roster || []).filter(a => a.status === "active" && a.key !== k && !NEUTRAL.has(a.key));
  const conf = pending && pending.k === k ? `<div class="confirmbar"><b>Ratify?</b> ${esc(pending.what)}. Your click is the Steward's ratification (Article 7.6): it's recorded as an edict, applied to ${esc(CAST[k].name)}'s tools, and noted for the Scribe.
      <div class="row"><button class="btn" id="perm-ok">Ratify</button><button class="btn ghost" id="perm-no">Cancel</button></div></div>` : "";
  return `${conf}<h2>Rank</h2>
    <p style="margin:4px 0"><select class="rank" id="rank-sel" ${P.rank_locked ? "disabled" : ""} aria-label="Rank">${Object.entries(P.ranks).map(([v, l]) => `<option value="${esc(v)}" ${v === P.rank ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>
      ${P.rank_locked ? `<span class="none"> Locked: the neutral officers don't supervise (Article 3.7).</span>` : ""}</p>
    <div id="group-pick" ${P.rank === "manager" ? "" : "hidden"}><div class="none" style="font-size:12.5px">Manager's group:</div><div class="grouppick">${active.map(a => `<label><input type="checkbox" value="${esc(a.key)}" ${P.group.includes(a.key) ? "checked" : ""}>${esc(a.name)}</label>`).join("")}</div></div>
    ${P.supervises.length ? `<p class="none" style="font-size:12.5px">Supervises: ${P.supervises.map(x => esc(nm(x))).join(", ")}</p>` : ""}
    <h2>May do</h2>${Object.entries(P.capabilities).map(([c, v]) => `<label class="perm ${v.locked ? "locked" : ""}"><input type="checkbox" data-cap="${esc(c)}" ${v.on ? "checked" : ""} ${v.locked ? "disabled" : ""}>
      <span class="n">${esc(v.label)}</span><span class="d">${esc(v.note)}</span></label>`).join("")}`;
}
function wirePerms(k){
  const P = PERMS[k]; if(!P || P.error) return;
  document.querySelectorAll("#side input[data-cap]").forEach(i => i.addEventListener("change", () => {
    const c = i.dataset.cap, on = i.checked, label = P.capabilities[c].label;
    pending = {k, body:{capability:c, on}, what:`${on ? "Grant" : "Revoke"} "${label}" ${on ? "to" : "from"} ${CAST[k].name}`}; side();
  }));
  const rs = $("#rank-sel"), gp = $("#group-pick");
  if(rs) rs.addEventListener("change", () => { gp.hidden = rs.value !== "manager"; if(rs.value !== "manager") askRank(); });
  if(gp) gp.addEventListener("change", askRank);
  function askRank(){ const rank = rs.value, group = [...gp.querySelectorAll("input:checked")].map(x => x.value);
    pending = {k, body:{rank, group}, what:`Set ${CAST[k].name}'s rank to ${P.ranks[rank]}${rank === "manager" && group.length ? `, supervising ${group.map(nm).join(", ")}` : ""}`}; side(); }
  const ok = $("#perm-ok"), no = $("#perm-no");
  if(ok) ok.addEventListener("click", async () => { const b = pending.body; pending = null;
    const r = await post(`/api/agents/${k}/permissions`, b); toast(r.message || r.error || (r.ok ? "Done." : "Refused."), !r.ok); delete PERMS[k]; delete BIO[k]; side(); });
  if(no) no.addEventListener("click", () => { pending = null; side(); });
}
async function openTerminal(k, standalone){
  const r = await post(`/api/agents/${k}/terminal`, {standalone:!!standalone});
  toast(r.message || r.error || (r.ok ? "Opened." : "Couldn't open a terminal."), !r.ok);
}
window.openTerminal = openTerminal;
const _side = side;
side = function(){
  _side();
  if(!selected || !L) return;
  const c = CAST[selected], proposed = c.status === "proposed";
  const tabs = document.querySelector("#side .tabs2");
  if(tabs && !tabs.querySelector('[data-t="perms"]')){
    const b = document.createElement("button"); b.setAttribute("role","tab"); b.dataset.t = "perms"; b.textContent = "Permissions";
    b.setAttribute("aria-selected", String(tab === "perms")); b.addEventListener("click", () => { tab = "perms"; side(); }); tabs.appendChild(b);
    if(tab === "perms"){ tabs.querySelectorAll("button").forEach(x => x.setAttribute("aria-selected", String(x === b)));
      let n = tabs.nextSibling; while(n){ const nx = n.nextSibling; n.remove(); n = nx; }
      tabs.insertAdjacentHTML("afterend", permsHtml(selected)); wirePerms(selected); }
  }
  if(!proposed && !document.querySelector("#side .term-btns")){
    const box = document.createElement("div"); box.className = "term-btns"; box.style.cssText = "display:flex;gap:6px;flex-wrap:wrap;margin:6px 0";
    box.innerHTML = `<button class="btn" title="Talk with this agent in a new herdr tab (recorded)">Open terminal</button><button class="btn ghost" title="Talk in a standalone Terminal window (recorded)">Standalone</button>`;
    const [a, b] = box.querySelectorAll("button"); a.onclick = () => openTerminal(selected, false); b.onclick = () => openTerminal(selected, true);
    const anchor = document.querySelector("#side .tabs2"); anchor ? anchor.before(box) : document.querySelector("#side").appendChild(box);
  }
};

// ---------- chats: avatars, summaries with Advanced, your comments (E-0068) ----------
function mini(k){   // the agent's own figure, drawn small: its profile primitive in the chat
  const w = who(k), col = esc(w.color);
  if(k === "steward") return `<svg class="mini" viewBox="-16 -46 32 50" aria-hidden="true"><circle cx="0" cy="-30" r="9" fill="#0A84FF"/><path d="M-12,2 Q-13,-18 0,-19 Q13,-18 12,2 Z" fill="#0A84FF"/></svg>`;
  return `<svg class="mini" viewBox="-16 -60 32 64" aria-hidden="true"><ellipse cx="0" cy="2" rx="11" ry="3.5" fill="#000" opacity=".15"/>
    <path d="M-12,0 Q-13,-26 0,-28 Q13,-26 12,0 Z" fill="${col}"/><circle cx="0" cy="-37" r="10" fill="${col}"/>
    <circle cx="-3.5" cy="-38" r="1.6" fill="#141A3A"/><circle cx="3.5" cy="-38" r="1.6" fill="#141A3A"/>
    <text x="0" y="-51" text-anchor="middle" font-size="11">${esc(w.icon)}</text></svg>`;
}
drawChat = function(){
  const box = $("#phone");
  if(!CHAT){ box.innerHTML = `<div class="ph-head"><button class="ph-back" onclick="closeChat()">‹ Floor</button><div class="ph-title" style="margin-top:28px">Loading…</div></div><div class="ph-body"></div>`; return; }
  const body = box.querySelector(".ph-body"), atBottom = !body || body.scrollHeight - body.scrollTop - body.clientHeight < 60;
  const draft = box.querySelector("textarea")?.value || "", dirChecked = !!box.querySelector("#ph-dir")?.checked;
  const items = CHAT.posts.map(p => ({kind:"msg", ...p})).concat((CHAT.doing||[]).map(d => ({kind:"doing", ...d}))).sort((a,b) => a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0);
  let html = "", lastTs = null;
  items.forEach((it, i) => {
    if(!lastTs || new Date(it.ts) - new Date(lastTs) > 15*60*1000) html += `<div class="ph-time">${stamp(it.ts)}</div>`;
    lastTs = it.ts;
    if(it.kind === "doing"){ html += `<div class="ph-doing"><b>${esc(who(it.who).name)}</b> ${esc(it.what)}</div>`; return; }
    const prev = items[i-1], next = items[i+1], me = it.who === "steward", w = who(it.who);
    const first = !prev || prev.kind !== "msg" || prev.who !== it.who, last = !next || next.kind !== "msg" || next.who !== it.who;
    if(first && !me) html += `<div class="ph-name">${esc(w.name)}</div>`;
    const sum = it.summary || it.text, long = (it.text || "").trim() !== (sum || "").trim();
    html += `<div class="ph-row${me ? " me" : ""}${last ? " last" : ""}">${me ? "" : `<span class="av ${last ? "" : "hide"}" style="background:none;border:0">${mini(it.who)}</span>`}
      <div class="bub"><span class="sum">${esc(sum)}</span>${long ? `<details><summary>Advanced</summary><pre>${esc(it.text)}</pre></details>` : ""}</div></div>`;
  });
  const typing = (L?.offices || []).filter(o => o.status === "working" && CHAT.participants.includes(o.key));
  for(const o of typing){ const w = who(o.key);
    html += `<div class="ph-name">${esc(w.name)}</div><div class="ph-row last"><span class="av" style="background:none;border:0">${mini(o.key)}</span><div class="bub typing" aria-label="${esc(w.name)} is working"><i></i><i></i><i></i></div></div>`; }
  const people = CHAT.participants.map(who);
  box.innerHTML = `<div class="ph-head"><button class="ph-back" onclick="closeChat()" aria-label="Back to the floor">‹ Floor</button>
      <div class="ph-avatars">${CHAT.participants.slice(0,4).map(k => `<span style="background:#fff;border-color:#F9F9F9">${mini(k)}</span>`).join("")}</div>
      <div class="ph-title" id="ph-title">${esc(people.map(w => w.name).join(", "))}</div>
      <div class="ph-sub">${CHAT.tag ? `#${esc(CHAT.tag)} · ` : ""}${esc(CHAT.title)} · <span class="ph-live"><i></i>live</span></div></div>
    <div class="ph-body" aria-live="polite">${html || `<div class="ph-doing">No messages yet.</div>`}</div>
    <div class="ph-foot">${L?.mode === "public" || DEMO ? `<div class="ph-input">${DEMO ? "Simulation: comments are off in demo mode." : "Read-only in public view."}</div>` :
      `<form class="ph-compose" id="ph-form"><textarea id="ph-text" placeholder="Add a comment to this chat…" aria-label="Your comment" maxlength="4000"></textarea>
        <div class="row"><label><input type="checkbox" id="ph-dir"> This is a direction (record it as an edict)</label><button type="submit">Send</button></div></form>`}</div>`;
  const ta = $("#ph-text"); if(ta){ ta.value = draft; $("#ph-dir").checked = dirChecked; }
  const f = $("#ph-form");
  if(f) f.addEventListener("submit", async e => { e.preventDefault(); const text = $("#ph-text").value.trim(); if(!text) return;
    const r = await post(`/api/conversations/${encodeURIComponent(CHAT.id)}/comment`, {text, direction: $("#ph-dir").checked});
    toast(r.message || r.error || (r.ok ? "Sent." : "Couldn't send."), !r.ok); if(r.ok){ $("#ph-text").value = ""; $("#ph-dir").checked = false; loadChat(); } });
  const nb = box.querySelector(".ph-body"); if(atBottom) nb.scrollTop = nb.scrollHeight;
};

// ---------- floating speech bubbles while no chat is open (E-0071) ----------
const lastSeen = {};
const _pollConvos = pollConvos;
pollConvos = async function(){
  await _pollConvos();
  for(const c of CONVOS){
    const before = lastSeen[c.id]; lastSeen[c.id] = c.count;
    if(before === undefined || c.count <= before || chatOpen) continue;
    if(AG[c.last_who]) floater(c.last_who, c.last_summary || c.last_text || "", c.title);
  }
};
function floater(k, text, where){
  const s = AG[k].pos; if(!s) return;
  const lines = wrap(text, 34).slice(0, 2), w = Math.max(...lines.map(l => l.length), where.length + 3) * 6.9 + 26, h = lines.length * 16 + 30;
  const g = el("g", {class:"floater"}, $("#bubbles"));
  const bx = s.x - w/2, by = s.y - 150 - h;
  el("rect", {x:bx, y:by, width:w, height:h, rx:12, fill:"#FFFFFF", stroke:CAST[k]?.color || "#8E97C4", "stroke-width":2}, g);
  el("path", {d:`M${s.x-7},${by+h} L${s.x},${by+h+10} L${s.x+7},${by+h} Z`, fill:"#FFFFFF"}, g);
  lines.forEach((l, i) => { const t = el("text", {x:bx+13, y:by+19+i*16, fill:"#1B2046", "font-family":"Barlow", "font-size":13.5}, g); t.textContent = l; });
  const wt = el("text", {x:bx+13, y:by+h-8, fill:"#6A7099", "font-family":"Barlow Semi Condensed", "font-size":11.5, "font-weight":700}, g); wt.textContent = `in ${where}`;
  setTimeout(() => g.remove(), 7200);
}

// ---------- demo mode: labeled simulation, in the browser only (E-0074) ----------
if(DEMO){
  const badge = document.createElement("div"); badge.className = "demo-badge"; badge.textContent = "SIMULATED ACTIVITY · demo mode · nothing here is real or recorded";
  document.body.appendChild(badge); document.title = "[SIMULATED] " + document.title;
  const keys = ["pm","scribe","lawyer","auditor","researcher","ideas","prototyper","media","social"];
  const LINES = {
    researcher:["Briefing library paper 07 on weak judges and strong debaters.","Three new preprints on judge calibration this week; one looks solid.","Checking whether the Ising aggregation holds on noisy labels."],
    ideas:["Proposal: a tiny demo of panel dependence with simulated judges.","Folding the calibration idea into P-002 instead of a new project.","Draft spec ready for the Lawyer's opinion."],
    prototyper:["Bench v001: the split is locked; hashing the claim IDs now.","Dev run on 50 claims finished; metrics with confidence intervals attached.","Fixing a flaky test in the aggregator."],
    media:["Storyboard for the Bench demo: three scenes, 45 seconds.","Captions checked against the transcript; one fix.","Contrast review of the new floor colors: all pairs pass."],
    social:["Draft reply to someone who asked about our sources: waiting for approval.","Intro thread revised with the Lawyer's wording.","No new mentions to answer."],
    pm:["Sprint plan: four items approved, two waiting on budget.","Routing the latest edict to the Scribe.","Digest drafted for the morning."],
    scribe:["Filed the decision as an officer case.","User Guide updated for the new floor.","Blog facts compiled for the week."],
    lawyer:["Opinion: proceed with changes; credit the dataset authors.","Conduct review of the pending draft: passes.","No overrule requests today."],
    auditor:["All eight verifiers pass.","Reproduced the dev metrics from the committed config: identical.","Spend today: within every office's cap."]};
  const pick = a => a[Math.floor(Math.random() * a.length)];
  const now = () => new Date().toISOString();
  const status = Object.fromEntries(keys.map(k => [k, "idle"])), last = {}, flagsOf = {};
  const convos = [
    {id:"demo-bench-baseline", title:"Bench baseline", tag:"proposal", participants:["prototyper","researcher","auditor"], posts:[]},
    {id:"demo-weekly-plan", title:"Weekly plan", tag:"decision", participants:["pm","ideas","lawyer","scribe"], posts:[]},
    {id:"demo-launch-thread", title:"Launch thread", tag:"proposal", participants:["social","media","lawyer"], posts:[]}];
  const T = [];
  const titles = ["Lock the test split","Dev run on 50 claims","Aggregator: geometric median","Demo storyboard","Captions pass","Intro thread revision","Weekly digest","File case for the plan","Calibration plot","Dataset license note","Contrast review","Reply to a mention"];
  const owners = ["prototyper","prototyper","prototyper","media","media","social","pm","scribe","researcher","lawyer","media","social"];
  titles.forEach((t, i) => T.push({n:i + 1, title:t, office:owners[i], state:pick(["open","ready","started","review","done","blocked"]), notes:"Simulated task (demo mode)."}));
  let seq = 1000;
  function tick(){
    const k = pick(keys); status[k] = Math.random() < .45 ? "working" : "idle";
    if(Math.random() < .5){ const c = pick(convos.filter(c => c.participants.includes(k)).concat(convos)); const text = pick(LINES[k] || ["Working."]);
      if(c.participants.includes(k)){ c.posts.push({who:k, ts:now(), text:text + "\n\n(Simulated message in demo mode.)", summary:text}); last[k] = text; } }
    const t = pick(T); t.state = pick(["open","ready","started","review","done","blocked"]);
    for(const x of keys) flagsOf[x] = status[x] === "working" ? [{kind:"busy", note:"Busy (simulated)"}]
      : T.some(t => t.office === x && t.state === "blocked") ? [{kind:"blocked", note:"Blocked (simulated)"}]
      : x === "social" ? [{kind:"approval", note:"Awaiting approval (simulated)"}] : [{kind:"scheduled", note:"Awaiting its next run (simulated)"}];
    seq += 1;
  }
  for(let i = 0; i < 12; i++) tick(); setInterval(tick, 2500);
  const realApi = api;
  api = async function(p){
    if(p.startsWith("/api/live")){ const real = await realApi(p).catch(() => null);
      return {...(real || {}), mode:"demo", huddle:null, waiting:[{what:"SIMULATED: 1 draft to approve", how:"demo mode", detail:[]}],
        offices: keys.map(k => ({key:k, status:status[k], since:now(), runs_today:3, last:last[k] || null, last_ts:last[k] ? now() : null, flags:flagsOf[k] || []})),
        pipeline:[{stage:"Papers", n:12},{stage:"Proposals", n:4},{stage:"Projects", n:3},{stage:"Demos", n:2},{stage:"Posts", n:1}], last_event:seq}; }
    if(p.startsWith("/api/conversations/")){ const c = convos.find(c => c.id === decodeURIComponent(p.split("/").pop()));
      return c ? {id:c.id, title:c.title + " (simulated)", tag:c.tag, participants:c.participants, posts:c.posts.slice(-40), doing:[]} : {error:"not found"}; }
    if(p.startsWith("/api/conversations")) return convos.filter(c => c.posts.length).map(c => { const l = c.posts[c.posts.length - 1];
      return {id:c.id, title:c.title, tag:c.tag, participants:c.participants, count:c.posts.length, last_ts:l.ts, last_who:l.who, last_text:l.text, last_summary:l.summary}; });
    if(p.startsWith("/api/tasks")) return T;
    if(p.startsWith("/api/events")) return [];
    return realApi(p);
  };
}

// ---------- start ----------
drawWhiteboards(); drawCoffee(); huddleButton();
if(typeof L !== "undefined" && L) render();
})();
