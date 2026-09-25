// The camera (P-001; edict E-0087): zoom, pan, and turn the isometric floor. It changes only the view:
// nothing is written, and the floor's own coordinates (rooms, homes, drops) stay in tiles.
// Wheel or pinch zooms toward the pointer; dragging empty floor pans; the buttons turn it a quarter at a time.
"use strict";
(function(){
const css = document.createElement("style");
css.textContent = `
.cam{position:fixed;left:18px;bottom:110px;display:flex;flex-direction:column;gap:6px;z-index:6}
.cam button{width:40px;height:40px;border-radius:12px;border:1px solid var(--line);background:rgba(18,24,52,.94);color:var(--text);
  font:700 18px var(--display);cursor:pointer;display:flex;align-items:center;justify-content:center}
.cam button:hover{border-color:#8E97C4}.cam .z{font:600 12px var(--display);color:var(--muted);text-align:center}
svg.world.panning{cursor:grabbing}svg.world{cursor:grab;touch-action:none}
svg.world .agent,svg.world [role=button]{cursor:pointer}
`;
document.head.appendChild(css);

const base = svg.getAttribute("viewBox").split(/\s+/).map(Number);     // the whole floor, as build() framed it
const MIN = .6, MAX = 4;
let cam = {z:1, x:0, y:0};                                               // zoom, and the pan in world units
try { const c = JSON.parse(localStorage.getItem("collective.camera") || "null"); if(c && isFinite(c.z)){ cam = {z:c.z, x:c.x, y:c.y}; ROT = (c.r|0) % 4; } } catch(e) {}
function save(){ try { localStorage.setItem("collective.camera", JSON.stringify({...cam, r:ROT})); } catch(e) {} }
function apply(){
  cam.z = Math.max(MIN, Math.min(MAX, cam.z));
  const w = base[2] / cam.z, h = base[3] / cam.z;
  const cx = base[0] + base[2]/2 + cam.x, cy = base[1] + base[3]/2 + cam.y;
  svg.setAttribute("viewBox", `${cx - w/2} ${cy - h/2} ${w} ${h}`);
  const zl = document.querySelector(".cam .z"); if(zl) zl.textContent = Math.round(cam.z * 100) + "%";
  save();
}
function toWorld(clientX, clientY){ const p = svg.createSVGPoint(); p.x = clientX; p.y = clientY; return p.matrixTransform(svg.getScreenCTM().inverse()); }
function zoomAt(f, clientX, clientY){       // keep the point under the pointer where it is
  const before = clientX == null ? null : toWorld(clientX, clientY);
  cam.z *= f; apply();
  if(before){ const after = toWorld(clientX, clientY); cam.x += before.x - after.x; cam.y += before.y - after.y; apply(); }
}
function rebuild(){
  const agents = [...$("#agents").children];
  [...svg.children].forEach(c => { if(c.tagName !== "title" && c.tagName !== "desc") c.remove(); });
  build(); agents.forEach(a => $("#agents").appendChild(a));
  window.floorExtras?.redraw();
  if(typeof L !== "undefined" && L) render();
  if(typeof drawChats === "function") drawChats();
  apply();
}
function turnBy(d){ ROT = (ROT + d + 4) % 4; rebuild(); }

svg.addEventListener("wheel", e => { e.preventDefault(); zoomAt(Math.exp(-e.deltaY * (e.ctrlKey ? .01 : .0015)), e.clientX, e.clientY); }, {passive:false});
// pan by dragging empty floor; anything clickable (agents, phones, chats, whiteboards) keeps its own pointer
let pan = null;
svg.addEventListener("pointerdown", e => {
  if(e.button !== 0 || e.target.closest(".agent,[role=button],.phone,.convo,.wb,a,button")) return;
  pan = {id:e.pointerId, x:e.clientX, y:e.clientY, moved:false};
});
svg.addEventListener("pointermove", e => {
  if(!pan || pan.id !== e.pointerId) return;
  if(!pan.moved && Math.hypot(e.clientX - pan.x, e.clientY - pan.y) < 4) return;
  if(!pan.moved){ pan.moved = true; svg.setPointerCapture(e.pointerId); svg.classList.add("panning"); }
  const a = toWorld(pan.x, pan.y), b = toWorld(e.clientX, e.clientY);
  cam.x -= b.x - a.x; cam.y -= b.y - a.y; pan.x = e.clientX; pan.y = e.clientY; apply();
});
const endPan = () => { pan = null; svg.classList.remove("panning"); };
svg.addEventListener("pointerup", endPan); svg.addEventListener("pointercancel", endPan);

const box = document.createElement("div"); box.className = "cam"; box.setAttribute("role", "toolbar"); box.setAttribute("aria-label", "Camera");
box.innerHTML = `<button data-a="in" title="Zoom in (+)" aria-label="Zoom in">＋</button><div class="z">100%</div>
  <button data-a="out" title="Zoom out (−)" aria-label="Zoom out">−</button>
  <button data-a="left" title="Turn the floor left ([)" aria-label="Turn the floor left">⟲</button>
  <button data-a="right" title="Turn the floor right (])" aria-label="Turn the floor right">⟳</button>
  <button data-a="home" title="Reset the view (0)" aria-label="Reset the view">⌂</button>`;
document.body.appendChild(box);
const act = a => { if(a === "in") zoomAt(1.25); else if(a === "out") zoomAt(1/1.25); else if(a === "left") turnBy(3); else if(a === "right") turnBy(1);
  else if(a === "home"){ cam = {z:1, x:0, y:0}; if(ROT){ ROT = 0; rebuild(); } else apply(); } };
box.addEventListener("click", e => { const b = e.target.closest("button"); if(b) act(b.dataset.a); });
document.addEventListener("keydown", e => {
  if(e.target.closest("input,textarea,select,[contenteditable],.tdrawer") || e.metaKey || e.ctrlKey || e.altKey) return;
  const a = {"+":"in", "=":"in", "-":"out", "[":"left", "]":"right", "0":"home"}[e.key]; if(a){ e.preventDefault(); act(a); }
});
if(ROT) rebuild(); else apply();
})();
