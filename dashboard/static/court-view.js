// The Court (P-006; specs/steward-2026-09-25-the-court.md): the Decisions tab. An isometric courtroom drawn with the floor's
// own rendering code (tile, box, hat, el, iso) and the floor's own characters (cloned from the floor, so every agent looks
// exactly as it does there), plus the Judge. Everything on screen is animated from the case's events in the Record
// (/api/cases/<id>/replay), so a live case and a replay run through the same code, step for step.
"use strict";
(function(){
if (typeof svg === "undefined" || typeof tile !== "function") return;                 // the floor only
const POS_COLOR = {A: "#4FD1C5", B: "#F2B84B", C: "#A78BFA", D: "#F472B6", insufficient: "#8E97C4"};
const BAND_COLOR = {Insufficient: "#8E97C4", Low: "#F2B84B", Moderate: "#4FD1C5", High: "#6CC3A0"};
const css = document.createElement("style");
css.textContent = `
svg.court{position:absolute;inset:0;width:100%;height:100%;display:none}
body.court-mode svg.world{display:none}body.court-mode svg.court{display:block}
body.court-mode .tray,body.court-mode .cam,body.court-mode #cam{display:none}
.cv-btn{font:700 14px var(--display);padding:8px 14px;border-radius:999px;border:1px solid var(--line);background:#1A1530;color:#CDB8FF;cursor:pointer;pointer-events:auto}
.cv-btn.on{background:#CDB8FF;color:#141A3A}
.cv-banner{position:fixed;top:118px;left:50%;transform:translateX(-50%);z-index:6;font:700 13px var(--display);letter-spacing:.08em;padding:6px 14px;border-radius:999px;
  background:#2B1F14;color:#FFD9A8;border:1px solid #F2B84B;display:none}
body.court-mode .cv-banner.show{display:block}
.cv-panel h2{display:flex;justify-content:space-between;align-items:center}
.cv-tabs{display:flex;gap:4px;margin:0 0 10px}.cv-tabs button{background:none;border:1px solid var(--line);color:var(--muted);border-radius:8px;padding:5px 10px;font:600 13px var(--display);cursor:pointer}
.cv-tabs button[aria-selected="true"]{color:var(--text);border-color:#CDB8FF}
.cv-case{background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin:6px 0;cursor:pointer}
.cv-case .q{font:600 14px var(--display)}.cv-case .m{color:var(--muted);font-size:12.5px;margin-top:3px}
.cv-chip{display:inline-block;border-radius:999px;padding:1px 8px;font:700 12px var(--display);color:#141A3A;cursor:help}
.cv-sec{margin:12px 0 4px;font:600 13.5px var(--display);color:var(--muted)}
.cv-ex{font-size:12.5px;margin:3px 0}.cv-ex a{color:#9CC7FF}
.cv-tx{white-space:pre-wrap;font:12px/1.45 ui-monospace,Menlo,monospace;background:#0F1430;border:1px solid var(--line);border-radius:8px;padding:8px;max-height:260px;overflow:auto}
.cv-tx .struck{text-decoration:line-through;color:#F07167}
.cv-form label{display:block;font:600 13px var(--display);margin:8px 0 3px}.cv-form input,.cv-form textarea,.cv-form select{width:100%;box-sizing:border-box;background:#0F1430;color:var(--text);
  border:1px solid var(--line);border-radius:8px;padding:6px 8px;font:14px var(--ui)}
.cv-scrub{display:flex;gap:6px;align-items:center;margin:6px 0}.cv-scrub input{flex:1}
.cv-scrub button{background:#1A1530;color:#CDB8FF;border:1px solid var(--line);border-radius:8px;padding:4px 10px;font:700 13px var(--display);cursor:pointer}
.cv-bd{font-size:12.5px;color:var(--muted)}.cv-bd b{color:var(--text)}
@media (prefers-reduced-motion:reduce){svg.court *{transition:none!important;animation:none!important}}
`;
document.head.appendChild(css);

// ---------- the courtroom scene ----------
const C = document.createElementNS(NS, "svg"); C.setAttribute("class", "court"); C.setAttribute("role", "img"); C.setAttribute("aria-label", "The Court");
document.querySelector(".stage").appendChild(C);
const banner = document.createElement("div"); banner.className = "cv-banner"; banner.textContent = "PROVISIONAL COURT · until the Court's amendment is ratified";
document.body.appendChild(banner);
const R = 14;                                              // the courtroom is R×R tiles
const BENCH = {x: 5.2, y: 0.8}, TABLE = {x: 7, y: 8}, JURY = {x: 12, y: 5};
let S = {};                                                // the scene's live objects

function withFlat(fn){ const r = ROT; ROT = 0; try { return fn(); } finally { ROT = r; } }   // the courtroom is never turned
function P(x, y, z){ return withFlat(() => iso(x, y, z || 0)); }

function drawRoom(){
  C.innerHTML = "";
  withFlat(() => {
    const g = el("g", {"aria-hidden": "true"}, C);
    for(let x = 0; x < R; x++) for(let y = 0; y < R; y++) tile(x, y, (x + y) % 2 ? "#221B36" : "#261E3D", "#2E2650", g);
    // the aisle to the bench, and a rug under the circle
    for(let y = 3; y < R; y++) tile(6.5, y, "#2B2247", "#3A2F5E", g);
    for(let x = 4; x < 10; x++) for(let y = 5; y < 11; y++) tile(x, y, "#2A2148", "#43386F", g);
    // the raised bench at the back, the Judge's seat
    box(BENCH.x - 0.2, BENCH.y - 0.4, 4, 1.6, 40, "#4A3A2A", "#2F241A", "#3B2E21", g);
    box(BENCH.x - 0.2, BENCH.y - 0.4, 4, 0.25, 58, "#5A4632", "#3A2C20", "#46362A", g);
    // the evidence table in the middle of the circle
    box(TABLE.x - 1, TABLE.y - 1, 2, 2, 16, "#5A4F9C", "#3E3673", "#4A4187", g);
    // the jury box along one side
    box(JURY.x, JURY.y, 1.6, 6, 14, "#3D2F4F", "#2A2036", "#33283F", g);
    const lb = P(JURY.x + 1.9, JURY.y + 6.4); const t = el("text", {x: lb.x, y: lb.y + 14, "text-anchor": "middle", fill: "#B7BEE3", "font-family": "Barlow Semi Condensed", "font-size": 14, "font-weight": 700, opacity: .75}, g); t.textContent = "JURY";
    const rl = P(0.4, R - 0.4); const rt = el("text", {x: rl.x, y: rl.y + 18, "text-anchor": "middle", fill: "#CFC6FF", "font-family": "Barlow Semi Condensed", "font-size": 13, "font-weight": 700, "letter-spacing": ".08em", opacity: .8}, g);
    rt.textContent = "→ THE RECORD";
    S.recordAt = P(0.4, R - 0.4, 40);
  });
  S.layers = {rings: el("g", {}, C), links: el("g", {}, C), exhibits: el("g", {}, C), people: el("g", {}, C), fx: el("g", {}, C), bubbles: el("g", {}, C)};
  drawScales();
  const tl = P(0, R), tr = P(R, 0), bt = P(R, R);
  C.setAttribute("viewBox", `${tl.x - 40} -300 ${tr.x - tl.x + 80} ${bt.y + 330}`);
}

// scales of justice over the bench: they tilt toward the leading side; at a ruling the tilt is the certainty
function drawScales(){
  const top = P(BENCH.x + 1.8, BENCH.y + 0.4, 250);
  const g = el("g", {class: "scales", transform: `translate(${top.x},${top.y})`}, C);
  el("line", {x1: 0, y1: 0, x2: 0, y2: 46, stroke: "#E8C547", "stroke-width": 3}, g);
  el("path", {d: "M-12,50 L12,50 L6,44 L-6,44 Z", fill: "#E8C547"}, g);
  const beam = el("g", {class: "beam"}, g); beam.style.transition = "transform .9s cubic-bezier(.3,1.4,.5,1)";
  el("line", {x1: -54, y1: 0, x2: 54, y2: 0, stroke: "#E8C547", "stroke-width": 3.5, "stroke-linecap": "round"}, beam);
  el("circle", {cx: 0, cy: 0, r: 4, fill: "#FFE27A"}, beam);
  for(const [side, x] of [["L", -50], ["R", 50]]){
    const pan = el("g", {class: "pan" + side, transform: `translate(${x},0)`}, beam);
    el("line", {x1: 0, y1: 0, x2: -12, y2: 26, stroke: "#E8C547", "stroke-width": 1.2}, pan); el("line", {x1: 0, y1: 0, x2: 12, y2: 26, stroke: "#E8C547", "stroke-width": 1.2}, pan);
    el("path", {d: "M-16,26 Q0,38 16,26 Z", fill: "#E8C547"}, pan);
    const lab = el("text", {x: 0, y: 52, "text-anchor": "middle", "font-family": "Barlow Semi Condensed", "font-size": 12, "font-weight": 700, fill: "#E9ECF8"}, pan); lab.textContent = side === "L" ? "A" : "B";
  }
  const gauge = el("g", {class: "gauge", transform: "translate(0,78)"}, g);
  el("rect", {x: -44, y: -14, width: 88, height: 28, rx: 14, fill: "#0F1430", stroke: "#8E97C4", class: "gbox"}, gauge);
  const gt = el("text", {x: 0, y: 5, "text-anchor": "middle", "font-family": "Barlow Semi Condensed", "font-size": 15, "font-weight": 700, fill: "#E9ECF8", class: "gtext"}, gauge); gt.textContent = "—";
  const tip = el("title", {}, gauge); tip.textContent = "Certainty appears with the ruling.";
  S.scales = {g, beam, gauge, gt, tip, gbox: gauge.querySelector(".gbox")};
}
function tilt(deg){ S.scales.beam.setAttribute("transform", `rotate(${Math.max(-24, Math.min(24, deg))})`);   // SVG rotate: positive tips the right pan down
  S.scales.beam.querySelectorAll(".panL,.panR").forEach(p => { const x = p.classList.contains("panL") ? -50 : 50; p.setAttribute("transform", `translate(${x},0) rotate(${-Math.max(-24, Math.min(24, deg))})`); }); }
function gauge(cert){
  const col = BAND_COLOR[cert.band] || "#8E97C4";
  S.scales.gt.textContent = `${cert.score} · ${cert.band}`; S.scales.gbox.setAttribute("stroke", col); S.scales.gbox.setAttribute("fill", col + "33");
  const i = cert.inputs || {};
  S.scales.tip.textContent = `Certainty ${cert.score} (${cert.band})\nevidence strength ${i.evidence_strength}\ncross-family agreement ${i.cross_family_agreement}\n` +
    `argument survival ${i.argument_survival}\njury margin ${i.jury_margin}\nJudge's confidence ${i.judge_confidence} (low weight)\ncapped at ${cert.cap}`;
}

// ---------- the people ----------
function figure(key, name, color){
  const g = el("g", {class: "cv-person", "data-k": key}, S.layers.people); g.style.transition = "transform 1.1s ease-in-out";
  const src = (typeof AG !== "undefined" && AG[key]) ? AG[key].g.querySelector(".fig") : null;
  if (src){ const f = src.cloneNode(true); f.querySelectorAll(".flag,.zzz,.dots,.mark,.zz").forEach(x => x.remove()); g.appendChild(f); }   // the floor's own character
  else if (key === "judge") judgeFigure(g);
  else { const c = color || "#8E97C4"; el("path", {d: "M-12,0 Q-13,-26 0,-28 Q13,-26 12,0 Z", fill: c}, g); el("circle", {cx: 0, cy: -37, r: 10, fill: c}, g);
         el("circle", {cx: -3.5, cy: -38, r: 1.6, fill: "#141A3A"}, g); el("circle", {cx: 3.5, cy: -38, r: 1.6, fill: "#141A3A"}, g); }
  const t = el("text", {x: 0, y: 20, "text-anchor": "middle", fill: "#DDE2F7", "font-family": "Barlow Semi Condensed", "font-size": 13, "font-weight": 600}, g); t.textContent = name;
  return g;
}
function judgeFigure(g){                                    // a dark robe, white collar, and a gavel, in the floor's shapes
  el("path", {d: "M-14,0 Q-15,-28 0,-30 Q15,-28 14,0 Z", fill: "#15131F"}, g);
  el("path", {d: "M-14,0 Q-15,-28 0,-30 L0,0 Z", fill: "#000", opacity: .25}, g);
  el("path", {d: "M-5,-29 L0,-20 L5,-29 Z", fill: "#F4F1E8"}, g);
  el("circle", {cx: 0, cy: -39, r: 10, fill: "#D9B38C"}, g);
  el("circle", {cx: -3.5, cy: -40, r: 1.6, fill: "#141A3A", class: "eye"}, g); el("circle", {cx: 3.5, cy: -40, r: 1.6, fill: "#141A3A", class: "eye"}, g);
  el("path", {d: "M-11,-44 Q-11,-54 0,-54 Q11,-54 11,-44 Q6,-48 0,-48 Q-6,-48 -11,-44 Z", fill: "#15131F"}, g);           // the cap
  const gavel = el("g", {class: "gavel", transform: "translate(15,-18) rotate(-30)"}, g); gavel.style.transition = "transform .18s";
  el("rect", {x: -1.5, y: -2, width: 3, height: 16, rx: 1, fill: "#7A5230"}, gavel); el("rect", {x: -6, y: -8, width: 12, height: 7, rx: 2, fill: "#5A3A20"}, gavel);
  S.gavel = gavel;
}
function stand(g, p, scale){ g.setAttribute("transform", `translate(${p.x},${p.y}) scale(${scale || 1.2})`); g.dataset.x = p.x; g.dataset.y = p.y; }
function ring(p, color){ el("ellipse", {cx: p.x, cy: p.y, rx: 22, ry: 10, fill: "none", stroke: color, "stroke-width": 3, opacity: .9}, S.layers.rings); }
// -45°: the first two advocates stand left and right on screen
function circleSpot(i, n){ const a = Math.PI * 2 * i / n - Math.PI / 4, r = 2.9; return P(TABLE.x + Math.cos(a) * r, TABLE.y + Math.sin(a) * r); }

// ---------- effects ----------
const wait = ms => new Promise(r => setTimeout(r, ms / (S.speed || 1)));
function bubble(p, text, color, full, cls){
  const lines = (typeof wrap === "function" ? wrap(text, 34) : [text]).slice(0, 4);
  const w = Math.max(...lines.map(l => l.length)) * 6.9 + 22, h = lines.length * 16 + 12;
  const g = el("g", {class: "cv-bubble " + (cls || "")}, S.layers.bubbles); g.style.transition = "opacity .6s, transform .6s";
  const bx = p.x - w / 2, by = p.y - 132 - h;
  el("rect", {x: bx, y: by, width: w, height: h, rx: 10, fill: "#F4F6FF", stroke: color || "#8E97C4", "stroke-width": 2}, g);
  el("path", {d: `M${p.x - 6},${by + h} L${p.x},${by + h + 9} L${p.x + 6},${by + h} Z`, fill: "#F4F6FF"}, g);
  lines.forEach((l, i) => { const t = el("text", {x: bx + 11, y: by + 19 + i * 16, fill: "#1B2046", "font-family": "Barlow", "font-size": 13}, g); t.textContent = l; });
  const ti = el("title", {}, g); ti.textContent = full || text;
  return g;
}
function crack(g){ if (!g) return; const r = g.querySelector("rect"); const b = r.getBBox();
  el("path", {d: `M${b.x + b.width * .3},${b.y} l8,${b.height * .4} l-6,4 l10,${b.height * .6}`, stroke: "#F07167", "stroke-width": 2.5, fill: "none"}, g);
  g.style.opacity = ".25"; g.style.transform = "translateY(10px)"; }
function flash(p, text, color){
  const g = el("g", {}, S.layers.fx);
  const t = el("text", {x: p.x, y: p.y - 150, "text-anchor": "middle", fill: color, "font-family": "Barlow Semi Condensed", "font-size": 22, "font-weight": 800, stroke: "#141A3A", "stroke-width": 4, "paint-order": "stroke"}, g);
  t.textContent = text; g.animate([{opacity: 0, transform: "scale(.6)"}, {opacity: 1, transform: "scale(1.1)"}, {opacity: 1, transform: "scale(1)"}, {opacity: 0}], {duration: 1400 / (S.speed || 1), easing: "ease-out"});
  setTimeout(() => g.remove(), 1500 / (S.speed || 1));
}
async function gavelStrike(){ if (!S.gavel) return; S.gavel.setAttribute("transform", "translate(15,-18) rotate(35)"); await wait(180); S.gavel.setAttribute("transform", "translate(15,-18) rotate(-30)");
  const j = S.people.judge; if (j) { const p = {x: +j.dataset.x, y: +j.dataset.y}; const r = el("circle", {cx: p.x + 20, cy: p.y - 20, r: 4, fill: "none", stroke: "#FFE27A", "stroke-width": 2}, S.layers.fx);
    r.animate([{r: 4, opacity: 1}, {r: 26, opacity: 0}], {duration: 500}); setTimeout(() => r.remove(), 520); } }
function exhibitDoc(x, i, n){
  const a = (i / Math.max(n, 1)) * Math.PI * 2, p = P(TABLE.x + Math.cos(a) * .55, TABLE.y + Math.sin(a) * .55, 18);
  const g = el("g", {class: "cv-ex", transform: `translate(${p.x},${p.y})`}, S.layers.exhibits); g.style.transition = "transform .5s, opacity .5s";
  el("rect", {x: -7, y: -9, width: 14, height: 18, rx: 2, fill: "#F4F1E8", stroke: "#CDB8FF", "stroke-width": 1}, g);
  [-4, 0, 4].forEach(y => el("line", {x1: -4, y1: y, x2: 4, y2: y, stroke: "#8E97C4", "stroke-width": 1}, g));
  const glow = el("circle", {r: 13, fill: "#FFE27A", opacity: 0, class: "glow", filter: "url(#blur)"}, g); g.insertBefore(glow, g.firstChild);
  const t = el("title", {}, g); t.textContent = `${x.exhibit}: ${x.title || ""}${x.reliability != null ? ` · reliability ${x.reliability}` : ""}`;
  g.dataset.x = p.x; g.dataset.y = p.y; return g;
}
async function cite(ids, speaker){
  for (const id of ids){
    const d = S.exhibits[id]; if (!d || !speaker) continue;
    const p = {x: +d.dataset.x, y: +d.dataset.y}, s = {x: +speaker.dataset.x, y: +speaker.dataset.y};
    d.setAttribute("transform", `translate(${p.x},${p.y - 16})`); d.querySelector(".glow").setAttribute("opacity", .8);
    const l = el("line", {x1: p.x, y1: p.y - 16, x2: s.x, y2: s.y - 40, stroke: "#FFE27A", "stroke-width": 1.4, opacity: .8, "stroke-dasharray": "3 3"}, S.layers.links);
    await wait(380);
    setTimeout(() => { d.setAttribute("transform", `translate(${p.x},${p.y})`); d.querySelector(".glow").setAttribute("opacity", 0); l.remove(); }, 1400 / (S.speed || 1));
  }
}
async function scroll(ruling, cert){
  const mid = P(TABLE.x, TABLE.y, 190);
  const g = el("g", {class: "cv-scroll", transform: `translate(${mid.x},${mid.y})`}, S.layers.fx); g.style.transition = "transform 1.4s ease-in, opacity 1.4s";
  const w = 300, body = el("rect", {x: -w / 2, y: -8, width: w, height: 0, rx: 6, fill: "#F4F1E8", stroke: "#C9B98F", "stroke-width": 2}, g);
  el("rect", {x: -w / 2 - 8, y: -14, width: w + 16, height: 10, rx: 5, fill: "#C9B98F"}, g);
  const col = BAND_COLOR[cert.band] || "#8E97C4";
  const txt = el("g", {opacity: 0}, g);
  const h1 = el("text", {x: 0, y: 16, "text-anchor": "middle", "font-family": "Barlow Semi Condensed", "font-size": 15, "font-weight": 800, fill: "#1B2046"}, txt);
  h1.textContent = ruling.holding === "insufficient" ? "INSUFFICIENT EVIDENCE" : `HELD: ${ruling.holding}`;
  (typeof wrap === "function" ? wrap(ruling.text || "", 44) : [ruling.text || ""]).slice(0, 3).forEach((l, i) => { const t = el("text", {x: 0, y: 36 + i * 15, "text-anchor": "middle", "font-family": "Barlow", "font-size": 12, fill: "#1B2046"}, txt); t.textContent = l; });
  el("rect", {x: -60, y: 84, width: 120, height: 22, rx: 11, fill: col}, txt);
  const ct = el("text", {x: 0, y: 99, "text-anchor": "middle", "font-family": "Barlow Semi Condensed", "font-size": 13, "font-weight": 800, fill: "#141A3A"}, txt); ct.textContent = `Certainty ${cert.score} · ${cert.band}`;
  body.animate([{height: 0}, {height: 116}], {duration: 900 / (S.speed || 1), fill: "forwards", easing: "ease-out"}); body.setAttribute("height", 116);
  await wait(900); txt.setAttribute("opacity", 1); S.scrollEl = g;
  await wait(2600);
  if (S.final) return;                                   // a finished replay keeps the scroll on screen
  g.setAttribute("transform", `translate(${S.recordAt.x},${S.recordAt.y}) scale(.08)`); g.style.opacity = "0.2";
}

// ---------- the play-by-play: one event at a time ----------
function reset(){ drawRoom(); S.people = {}; S.exhibits = {}; S.claimBubble = {}; S.lead = {A: 0, B: 0, C: 0, D: 0}; S.final = false; tilt(0); }
function speakerOf(k){ return S.people[k]; }
function leadTilt(){ const a = S.lead.A || 0, b = S.lead.B || 0; tilt((b - a) * 3); }
async function step(e, fast){
  const d = e.data || {}, sp = S.speed;
  if (fast) S.speed = 40;
  try {
    if (e.type === "case.filed"){ S.question = d.question; }
    else if (e.type === "positions.framed"){ S.positions = d.positions; }
    else if (e.type === "exhibit.admitted" || e.type === "exhibit.excluded"){
      const n = Object.keys(S.exhibits).length; const g = exhibitDoc(d, n, 6); S.exhibits[d.exhibit] = g;
      if (e.type === "exhibit.excluded"){ g.style.opacity = ".25"; g.querySelector("rect").setAttribute("stroke", "#F07167"); }
      await wait(250);
    } else if (e.type === "advocates.assigned"){
      if (!S.people.judge){ const j = figure("judge", "The Judge"); stand(j, P(BENCH.x + 1.8, BENCH.y + 0.4, 40), 1.25); S.people.judge = j; }
      d.advocates.forEach((a, i) => { const p = circleSpot(i, d.advocates.length); ring(p, POS_COLOR[a.position_id]);
        const g = figure(a.agent, `${(typeof CAST !== "undefined" && CAST[a.agent]?.name) || a.agent} · ${a.position_id}`); stand(g, p); S.people[a.agent] = g; g.dataset.home = JSON.stringify(p); });
      d.jury.forEach((j, i) => { const g = figure(j.agent, (typeof CAST !== "undefined" && CAST[j.agent]?.name) || j.agent); stand(g, P(JURY.x + 0.8, JURY.y + 0.8 + i * 1.8, 14), 0.95); S.people[j.agent] = g; });
      await wait(600);
    } else if (e.type === "argument"){
      const g = speakerOf(e.actor); if (!g) return;
      const home = JSON.parse(g.dataset.home || "{}"), t = P(TABLE.x, TABLE.y), fwd = {x: home.x + (t.x - home.x) * .28, y: home.y + (t.y - home.y) * .28};
      stand(g, fwd); await wait(700);
      const claims = d.claims || [];
      const b = bubble(fwd, `${d.kind}: ${d.summary || claims.map(c => c.text).join(" ")}`, POS_COLOR[d.position],
                       `${e.actor} for ${d.position} (${d.kind}, round ${d.round}):\n` + claims.map(c => `[${c.id}] ${c.text} (cites ${c.cites.join(", ") || "nothing"})`).join("\n"));
      claims.forEach(c => { S.claimBubble[c.id] = b; S.lead[d.position] = (S.lead[d.position] || 0) + (c.cites_admitted?.length ? 1 : 0); });
      await cite([...new Set(claims.flatMap(c => c.cites_admitted || []))], g);
      leadTilt(); await wait(1600);
      stand(g, home); setTimeout(() => { if (!b.classList.contains("keep")) b.remove(); }, 1200 / (S.speed || 1));
    } else if (e.type === "objection"){
      const g = speakerOf(e.actor); const p = g ? {x: +g.dataset.x, y: +g.dataset.y} : P(TABLE.x, TABLE.y);
      flash(p, "OBJECTION!", "#F07167"); await wait(700);
      await gavelStrike();
      const j = S.people.judge; const jp = j ? {x: +j.dataset.x, y: +j.dataset.y} : p;
      flash(jp, d.ruling === "sustained" ? "Sustained" : "Overruled", d.ruling === "sustained" ? "#F07167" : "#6CC3A0");
      if (d.ruling === "sustained"){
        const owner = (d.claim.match(/-R\d+-([A-D])/) || [])[1];
        if (owner) S.lead[owner] = Math.max(0, (S.lead[owner] || 0) - 1);
        let cb = S.claimBubble[d.claim];
        if (!cb || !cb.isConnected){ const who = Object.values(S.people).find(x => (x.querySelector("text:last-child")?.textContent || "").endsWith(`· ${owner}`));
          cb = who ? bubble({x: +who.dataset.x, y: +who.dataset.y}, `[struck] ${d.claim}`, POS_COLOR[owner]) : null; }
        if (cb){ cb.classList.add("keep"); crack(cb); setTimeout(() => cb.remove(), 2200 / (S.speed || 1)); }
        leadTilt();
      }
      await wait(1100);
    } else if (e.type === "question"){
      const j = S.people.judge, g = speakerOf(d.to);
      if (j){ const q = bubble({x: +j.dataset.x, y: +j.dataset.y}, `To ${d.to}: ${d.question}`, "#CDB8FF", d.question); await wait(1500); q.remove(); }
      if (g){ const a = bubble({x: +g.dataset.x, y: +g.dataset.y}, d.answer, "#8E97C4", d.answer); await wait(1500); a.remove(); }
    } else if (e.type === "ballot.sealed"){
      const g = speakerOf(e.actor); if (!g) return;
      const p = {x: +g.dataset.x, y: +g.dataset.y}, box = P(JURY.x + 0.8, JURY.y + 6.2, 18);
      const env = el("g", {transform: `translate(${p.x},${p.y - 30})`}, S.layers.fx); env.style.transition = "transform .8s ease-in";
      el("rect", {x: -8, y: -5, width: 16, height: 10, rx: 1.5, fill: "#F4F1E8", stroke: "#C9B98F"}, env); el("path", {d: "M-8,-5 L0,1 L8,-5", fill: "none", stroke: "#C9B98F"}, env);
      await wait(80); env.setAttribute("transform", `translate(${box.x},${box.y})`); S.envelopes = (S.envelopes || []).concat([env]); await wait(700);
    } else if (e.type === "ballot.counted"){
      for (const [i, b] of (d.ballots || []).entries()){
        const env = (S.envelopes || [])[i]; const g = speakerOf(b.juror);
        if (env) env.querySelector("rect").setAttribute("fill", POS_COLOR[b.vote] || "#8E97C4");
        if (g) flash({x: +g.dataset.x, y: +g.dataset.y}, b.vote === "insufficient" ? "Insufficient" : b.vote, POS_COLOR[b.vote] || "#8E97C4");
        await wait(900);
      }
    } else if (e.type === "judge.ruling"){ await gavelStrike(); await wait(300); }
    else if (e.type === "case.ruled"){
      await gavelStrike(); await wait(250); await gavelStrike();
      const cert = d.breakdown || {score: d.certainty, band: d.band, inputs: {}};
      const toward = d.holding === "B" ? 1 : d.holding === "A" ? -1 : 0;
      tilt(toward * (cert.score / 100) * 24); gauge(cert);
      await scroll({holding: d.holding, text: S.rulingText || ""}, cert);
    }
  } finally { if (fast) S.speed = sp; }
}

// ---------- live and replay ----------
let CASE = null, EVENTS = [], shown = 0, playing = false, polling = null;
async function openCase(id, opts){
  CASE = await api(`/api/cases/${id}`); const r = await api(`/api/cases/${id}/replay`); EVENTS = r.events || [];
  S.rulingText = (CASE.ruling || {}).holding_text || "";
  reset(); shown = 0; S.speed = 1;
  const upto = opts && opts.from != null ? opts.from : (CASE.status === "ruled" ? 0 : EVENTS.length);
  for (; shown < upto; shown++) await step(EVENTS[shown], true);                      // catch up without animation
  cvSide(); play();
  clearInterval(polling); polling = setInterval(poll, 3000);
}
async function play(){
  if (playing) return; playing = true;
  while (playing && shown < EVENTS.length){ await step(EVENTS[shown]); shown++; scrubUpdate(); }
  if (shown >= EVENTS.length && CASE && CASE.status === "ruled"){ S.final = true; }
  playing = false; scrubUpdate();
}
async function poll(){
  if (!CASE || !document.body.classList.contains("court-mode")) return;
  const r = await api(`/api/cases/${CASE.id}/replay`); const n = (r.events || []).length;
  if (n > EVENTS.length){ EVENTS = r.events; const c = await api(`/api/cases/${CASE.id}`); CASE = c; S.rulingText = (c.ruling || {}).holding_text || ""; if (!playing) play(); cvSide(); }
}
async function seek(i){ playing = false; await wait(50); reset(); for (shown = 0; shown < i; shown++) await step(EVENTS[shown], true); scrubUpdate(); }
function scrubUpdate(){ const s = document.querySelector("#cv-scrub"); if (s){ s.max = EVENTS.length; s.value = shown; }
  const l = document.querySelector("#cv-at"); if (l) l.textContent = `${shown} / ${EVENTS.length}${EVENTS[shown - 1] ? " · " + EVENTS[shown - 1].type : ""}`; }

// ---------- the side panel ----------
let tab = "docket", DOCKET = null, filter = "all";
function chip(c){ if (c.certainty == null) return `<span class="cv-chip" style="background:#3A3F66;color:#DDE2F7">${esc(c.status || "")}</span>`;
  return `<span class="cv-chip" style="background:${BAND_COLOR[c.band] || "#8E97C4"}" title="Certainty ${esc(c.certainty)} (${esc(c.band)})">${esc(c.certainty)} · ${esc(c.band)}</span>`; }
function breakdown(cert){ const i = cert.inputs || {};
  return `<div class="cv-bd" title="capped at the lower of evidence strength and cross-family agreement">Evidence strength <b>${esc(i.evidence_strength)}</b> · cross-family agreement <b>${esc(i.cross_family_agreement)}</b> · argument survival <b>${esc(i.argument_survival)}</b> · jury margin <b>${esc(i.jury_margin)}</b> · Judge's confidence <b>${esc(i.judge_confidence)}</b> (weight 0.10) · weighted ${esc(cert.weighted_mean)}, capped at ${esc(cert.cap)}</div>`; }
async function cvSide(){
  if (!document.body.classList.contains("court-mode")) return;
  const box = document.querySelector("#side"); if (!box) return;
  if (tab === "docket" || !DOCKET) DOCKET = await api("/api/cases");
  const tabs = `<div class="cv-tabs" role="tablist">${["docket", "case", "file"].map(t => `<button role="tab" data-t="${t}" aria-selected="${tab === t}">${t === "file" ? "⚖️ File a case" : t[0].toUpperCase() + t.slice(1)}</button>`).join("")}</div>`;
  let body = "";
  if (tab === "docket"){
    const cs = (DOCKET.cases || []).filter(c => filter === "all" || c.status === filter);
    body = `<h2>The docket <b>${cs.length}</b></h2><div class="cv-scrub">Status <select id="cv-filter">${["all", "filed", "in discovery", "in session", "ruled", "reopened", "error"].map(s => `<option${s === filter ? " selected" : ""}>${s}</option>`).join("")}</select></div>` +
      (cs.map(c => `<div class="cv-case" data-id="${esc(c.id)}"><div class="q">${esc(c.id)}${c.test ? " (test)" : ""} · ${esc(c.question)}</div><div class="m">${chip(c)} · ${esc(c.status)} · ${esc((c.filed || "").slice(0, 10))}${c.holding ? ` · held ${esc(c.holding)}` : ""}${c.case_law ? ` · ${esc(c.case_law)}` : ""}</div></div>`).join("") || `<p class="none">No cases yet.</p>`);
  } else if (tab === "case" && CASE){
    const c = CASE, cert = c.certainty, r = c.ruling || {};
    const pos = (c.positions || []).map(p => `<div class="cv-ex"><span class="cv-chip" style="background:${POS_COLOR[p.id]}">${esc(p.id)}</span> ${esc(p.text)}</div>`).join("");
    const ex = (c.exhibits || []).map(x => `<div class="cv-ex">${x.admitted ? "✓" : "✗"} <b>${esc(x.id)}</b> ${esc(x.title || "")} · reliability ${esc(x.reliability)} · ${esc(x.date || "")}${/^https?:/.test(x.source || "") ? ` · <a href="${esc(x.source)}" target="_blank" rel="noopener noreferrer">source ↗</a>` : ` · ${esc(x.source || "")}`}</div>`).join("") || `<p class="none">None yet.</p>`;
    const tx = esc((c.transcript || "").replace(/^[\s\S]*?```\n?|```\s*$/g, "")).replace(/^(.*STRUCK.*)$/gm, `<span class="struck">$1</span>`);
    body = `<h2>${esc(c.id)} ${cert ? chip({certainty: cert.score, band: cert.band}) : ""}</h2><p style="margin:0 0 6px">${esc(c.question)}</p>
      <div class="cv-scrub"><button id="cv-play">▶</button><input type="range" id="cv-scrub" min="0" max="${EVENTS.length}" value="${shown}"><span id="cv-at" class="cv-bd"></span></div>
      <div class="cv-scrub"><button id="cv-restart">Replay from the start</button> <a href="${esc(c.weave || "")}" target="_blank" rel="noopener noreferrer" style="color:#FFCC33">View in Weave ↗</a></div>
      <div class="cv-sec">Positions</div>${pos}<div class="cv-sec">Exhibits</div>${ex}
      ${r.final_holding ? `<div class="cv-sec">Ruling</div><p style="margin:0">${r.final_holding === "insufficient" ? "<b>Insufficient evidence.</b>" : `<b>${esc(r.final_holding)}</b>.`} ${esc(r.holding_text || "")}</p>
        ${breakdown(cert)}<div class="cv-sec">Dissent</div><p style="margin:0">${esc(r.dissent || "None.")}</p>
        <div class="cv-sec">Jury</div>${(c.ballots || []).map(b => `<div class="cv-ex">${esc(b.juror)} (${esc(b.family)}): <b>${esc(b.vote)}</b>. ${esc(b.reason)}</div>`).join("")}
        <div class="cv-sec">Reopen if</div>${(r.reopen_conditions || []).map(x => `<div class="cv-ex">· ${esc(x)}</div>`).join("")}
        ${c.case_law ? `<div class="cv-sec">Case law</div><div class="cv-ex">Filed as ${esc(c.case_law)} (officer case${c.provisional ? ", provisional court" : ""})</div>` : ""}` : `<div class="cv-sec">Status</div><p style="margin:0">${esc(c.status)} · ${esc(c.spent_tokens || 0)} of ${esc(c.budget_tokens)} tokens</p>`}
      <div class="cv-sec">Transcript</div><div class="cv-tx">${tx || "The argument hasn't started."}</div>`;
  } else if (tab === "case"){ body = `<p class="none">Pick a case on the docket.</p>`; }
  else {
    body = `<h2>⚖️ File a case</h2><div class="cv-form"><label>Question</label><textarea id="cv-q" rows="3" maxlength="500" placeholder="A question the evidence can settle."></textarea>
      <label>Positions (optional; the Lawyer frames them if you leave these empty)</label>${[1, 2, 3, 4].map(i => `<input class="cv-p" maxlength="300" placeholder="Position ${String.fromCharCode(64 + i)}">`).join("")}
      <label>Evidence links (optional, one per line)</label><textarea id="cv-l" rows="3" placeholder="https://arxiv.org/abs/..."></textarea>
      <label>Priority</label><select id="cv-pr"><option>normal</option><option>high</option><option>low</option></select>
      <label>Budget (tokens)</label><input id="cv-b" type="number" value="150000" min="20000" max="500000" step="10000">
      <div style="margin-top:10px"><button class="btn" id="cv-go">File the case</button></div></div>`;
  }
  box.innerHTML = `<button class="back" id="cv-back">Back to the floor</button>` + tabs + body;
  box.querySelector("#cv-back").onclick = () => toggle(false);
  box.querySelectorAll(".cv-tabs button").forEach(b => b.onclick = () => { tab = b.dataset.t; cvSide(); });
  box.querySelectorAll(".cv-case").forEach(d => d.onclick = () => { tab = "case"; openCase(d.dataset.id); });
  const f = box.querySelector("#cv-filter"); if (f) f.onchange = () => { filter = f.value; cvSide(); };
  const s = box.querySelector("#cv-scrub"); if (s) s.oninput = () => seek(+s.value);
  const pl = box.querySelector("#cv-play"); if (pl) pl.onclick = () => playing ? (playing = false) : play();
  const rs = box.querySelector("#cv-restart"); if (rs) rs.onclick = async () => { await seek(0); play(); };
  const go = box.querySelector("#cv-go"); if (go) go.onclick = async () => {
    const body = {question: box.querySelector("#cv-q").value, positions: [...box.querySelectorAll(".cv-p")].map(i => i.value).filter(Boolean),
                  links: box.querySelector("#cv-l").value.split(/\n+/).map(x => x.trim()).filter(Boolean), priority: box.querySelector("#cv-pr").value, budget: +box.querySelector("#cv-b").value};
    const r = await fetch("/api/cases", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)}).then(r => r.json()).catch(() => ({error: "no answer"}));
    if (typeof toast === "function") toast(r.message || r.error || "Done.", !r.ok);
    if (r.ok){ tab = "case"; openCase(r.id); }
  };
  scrubUpdate();
}

// ---------- the Decisions tab ----------
function toggle(on){
  document.body.classList.toggle("court-mode", on);
  document.querySelector("#cv-btn")?.classList.toggle("on", on);
  if (on){ if (!S.layers) reset(); cvSide(); if (!CASE) api("/api/cases").then(d => { DOCKET = d; banner.classList.toggle("show", !!d.provisional); const first = (d.cases || []).find(c => !c.test) || (d.cases || [])[0]; if (first){ tab = "case"; openCase(first.id); } }); }
  else { playing = false; clearInterval(polling); if (typeof render === "function") render(); }
}
window.courtView = {seekEnd: async () => { await seek(Math.max(0, EVENTS.length - 1)); S.final = true; await step(EVENTS[EVENTS.length - 1]); shown = EVENTS.length; scrubUpdate(); },
  open: (id) => { toggle(true); if (id){ tab = "case"; openCase(id); } }, close: () => toggle(false)};
const hud = document.querySelector(".hud");
if (hud && !document.querySelector("#cv-btn")){
  const b = document.createElement("button"); b.id = "cv-btn"; b.className = "cv-btn"; b.textContent = "⚖️ Decisions"; b.title = "The Court: cases argued from evidence, with a certainty score";
  b.onclick = () => toggle(!document.body.classList.contains("court-mode"));
  const at = hud.querySelector(".wv-btn") || hud.querySelector('a[href="/scope"]'); at ? at.before(b) : hud.appendChild(b);
}
// the floor repaints its side panel on every live update; while the Court is open, the Court's panel stays (it redraws itself when its case changes)
const floorSide = side;
side = function(){ if (document.body.classList.contains("court-mode")) return; return floorSide(); };
})();
