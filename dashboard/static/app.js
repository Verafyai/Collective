// The Collective Dashboard (P-001). Everything from the records is rendered with
// textContent / DOM nodes, never as HTML (spec §6).
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const params = new URLSearchParams(location.search);
let AT = params.get("at") || "live";
let STATE = null;

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k instanceof Node ? k : String(k));
  return el;
}

// ---------- a small, safe markdown renderer (DOM only) ----------
function safeHref(u) {
  u = u.trim();
  if (/^https:\/\//i.test(u)) return u;
  if (/^(#|[\w./-]+$)/.test(u) && !/^javascript:/i.test(u)) return null; // repo-relative: shown as text
  return null;
}
function inline(text) {
  const out = []; const re = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)|(\[[^\]]+\]\([^)]+\))/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const t = m[0];
    if (m[1]) out.push(h("code", {}, t.slice(1, -1)));
    else if (m[2]) out.push(h("strong", {}, ...inline(t.slice(2, -2))));
    else if (m[3]) out.push(h("em", {}, ...inline(t.slice(1, -1))));
    else {
      const [, label, url] = t.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      const href = safeHref(url);
      out.push(href ? h("a", { href, rel: "noopener noreferrer", target: "_blank" }, label) : h("span", { title: url }, label));
    }
    last = m.index + t.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
function markdown(src, { idPrefix = "" } = {}) {
  const root = h("div", { class: "md" });
  const lines = src.replace(/\r/g, "").split("\n");
  let i = 0, para = [];
  const flush = () => { if (para.length) { root.append(h("p", {}, ...inline(para.join(" ")))); para = []; } };
  while (i < lines.length) {
    const l = lines[i];
    if (/^(```|````)/.test(l)) {
      flush(); const fence = l.match(/^`+/)[0]; const buf = []; i++;
      while (i < lines.length && !lines[i].startsWith(fence)) buf.push(lines[i++]);
      root.append(h("pre", {}, h("code", {}, buf.join("\n")))); i++; continue;
    }
    const hd = l.match(/^(#{1,6})\s+(.*)$/);
    if (hd) {
      flush(); const lvl = Math.min(hd[1].length + 1, 6);
      const id = idPrefix + hd[2].toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      root.append(h("h" + lvl, { id }, ...inline(hd[2]))); i++; continue;
    }
    if (/^\s*\|/.test(l)) {
      flush(); const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(lines[i++]);
      const cells = r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
      const t = h("table"); const body = rows.filter(r => !/^\s*\|[\s:|-]+\|\s*$/.test(r));
      body.forEach((r, n) => t.append(h("tr", {}, ...cells(r).map(c => h(n === 0 ? "th" : "td", {}, ...inline(c))))));
      root.append(t); continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
      flush(); const ordered = /^\s*\d+\./.test(l); const list = h(ordered ? "ol" : "ul");
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        let item = lines[i++].replace(/^\s*([-*]|\d+\.)\s+/, "");
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) item += " " + lines[i++].trim();
        list.append(h("li", {}, ...inline(item)));
      }
      root.append(list); continue;
    }
    if (/^>\s?/.test(l)) {
      flush(); const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) buf.push(lines[i++].replace(/^>\s?/, ""));
      root.append(h("blockquote", {}, ...inline(buf.join(" ")))); continue;
    }
    if (/^(---|\*\*\*)\s*$/.test(l)) { flush(); root.append(h("hr")); i++; continue; }
    if (/^<!--.*-->$/.test(l.trim())) { i++; continue; }
    if (!l.trim()) { flush(); i++; continue; }
    para.push(l.trim()); i++;
  }
  flush(); return root;
}

// ---------- chrome ----------
function badge(text, kind) { return h("span", { class: "badge " + kind }, text); }
function fmtTime(ts) { if (!ts) return "—"; const d = new Date(ts); return isNaN(d) ? ts : d.toLocaleString(); }
function asOfLine(a) {
  const bits = [];
  if (a.commit) bits.push("commit " + a.commit.slice(0, 7));
  if (a.event != null) bits.push("event #" + a.event);
  return "as of " + (bits.join(", ") || "—");
}
function panel(title, source, ...kids) {
  const a = STATE.header.as_of;
  return h("section", { class: "panel", "aria-labelledby": "h-" + title.replace(/\W+/g, "") },
    h("h2", { id: "h-" + title.replace(/\W+/g, "") }, title),
    h("p", { class: "src" }, `${asOfLine(a)} · source: ${source}`), ...kids);
}

function renderHeader() {
  const hd = STATE.header, f = $("#facts"); f.replaceChildren();
  const fact = (dt, dd) => f.append(h("div", {}, h("dt", {}, dt), h("dd", {}, dd)));
  fact("Charter", "v" + hd.charter_version);
  fact("Sprint", hd.sprint.id ? `${hd.sprint.id} · ${hd.sprint.phase}` : hd.sprint.phase);
  fact("Stop switch", hd.stop ? badge("ON: org/STOP", "bad") : badge("off", "ok"));
  if (hd.paused.length) fact("Paused", badge(hd.paused.join(", "), "warn"));
  fact("As of", asOfLine(hd.as_of).replace(/^as of /, ""));
  fact("Mode", badge(hd.mode, hd.mode === "public" ? "muted" : "warn"));
  const asof = $("#asof");
  asof.className = "asof" + (hd.as_of.kind === "live" ? "" : " past");
  asof.textContent = hd.as_of.kind === "live"
    ? `Live. Updates automatically. ${asOfLine(hd.as_of)}${hd.as_of.event_ts ? " (" + fmtTime(hd.as_of.event_ts) + ")" : ""}.`
    : `Viewing the past: ${hd.as_of.label}, ${asOfLine(hd.as_of)}${hd.as_of.event_ts ? " (" + fmtTime(hd.as_of.event_ts) + ")" : ""}. Choose "live" to return.`;
  $("#gen").textContent = "rendered " + fmtTime(STATE.generated_at);
  document.title = (hd.as_of.kind === "live" ? "" : "[past] ") + "Collective Dashboard";
}

function renderRail(current) {
  const ul = $("#rail"); ul.replaceChildren();
  for (const p of STATE.panels) {
    const soon = p.version > 1 ? h("span", { class: "soon", title: `planned for version ${String(p.version).padStart(3, "0")}` }, "v" + String(p.version).padStart(3, "0")) : null;
    ul.append(h("li", {}, h("a", { href: "#/" + p.id, "aria-current": p.id === current ? "page" : null }, h("span", {}, p.title), soon)));
  }
}

function renderTravel() {
  const sel = $("#t-commit"); const keep = sel.value; sel.replaceChildren();
  for (const c of STATE.versioning.travel.commits)
    sel.append(h("option", { value: c.sha }, `${c.short} · ${c.date.slice(0, 16).replace("T", " ")} · ${c.subject.slice(0, 60)}`));
  if (keep) sel.value = keep;
  const ev = STATE.versioning.travel.events;
  $("#t-event-wrap").hidden = !ev;
  if (ev && ev.last) { $("#t-event").max = ev.last.seq; $("#t-event").placeholder = "1–" + ev.last.seq; }
  const [kind, arg] = AT.includes(":") ? [AT.split(":")[0], AT.slice(AT.indexOf(":") + 1)] : ["live", ""];
  const radio = document.querySelector(`input[name=kind][value=${kind}]`); if (radio) radio.checked = true;
  if (kind === "commit") sel.value = STATE.header.as_of.commit || arg;
  if (kind === "event") $("#t-event").value = arg;
  if (kind === "date") { const d = new Date(arg); if (!isNaN(d)) $("#t-date").value = new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16); }
}

// ---------- panels ----------
function vMission() {
  const m = STATE.mission;
  return panel("Mission", m.source,
    m.last_change ? h("p", { class: "src" }, `Last changed ${fmtTime(m.last_change.date)} in ${m.last_change.commit}: ${m.last_change.subject}`) : null,
    h("p", { class: "src" }, "Sources: " + m.sources_note),
    markdown(m.markdown));
}

function vCharter() {
  const c = STATE.charter;
  const toc = h("ol", { class: "toc" }, ...c.articles.map(a => {
    const id = "art-" + a.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    return h("li", {}, h("a", { href: "#" + id, onclick: e => { e.preventDefault(); document.getElementById(id)?.scrollIntoView({ block: "start" }); } }, a));
  }));
  const log = h("div", { class: "scroll" }, h("table", {},
    h("tr", {}, ...["Amendment", "Version", "Date", "Class", "Title", "Vote", "Ratified by"].map(x => h("th", {}, x))),
    ...c.amendments.slice().reverse().map(e => h("tr", {}, h("td", { class: "mono" }, e.id), h("td", { class: "mono" }, "v" + e.version),
      h("td", { class: "mono" }, e.date), h("td", {}, e.class), h("td", {}, e.title), h("td", {}, e.vote), h("td", {}, e.ratified_by)))));
  const tl = h("div", { class: "scroll" }, h("table", {},
    h("tr", {}, ...["Version", "Date", "Amendment", "Class", "Change", "Articles", "Members", "Plugins", "Files"].map(x => h("th", {}, x))),
    ...c.timeline.slice().reverse().map(r => h("tr", {}, ...["version", "date", "amendment", "class", "change", "articles", "members", "plugins", "files"].map(k => h("td", { class: /version|date|amendment/.test(k) ? "mono" : null }, r[k]))))));
  const opts = () => c.versions.map(v => h("option", { value: v }, "v" + v));
  const from = h("select", { "aria-label": "From version" }, ...opts()); const to = h("select", { "aria-label": "To version" }, ...opts());
  if (c.versions.length > 1) { from.value = c.versions[c.versions.length - 2]; to.value = c.versions[c.versions.length - 1]; }
  const out = h("div", { "aria-live": "polite" });
  const diffBtn = h("button", { type: "button", onclick: async () => {
    out.replaceChildren(h("p", {}, "Comparing…"));
    try {
      const r = await fetch(`/api/charter-diff?at=${encodeURIComponent(AT)}&from=${from.value}&to=${to.value}`);
      const j = await r.json(); if (!r.ok) throw new Error(j.error);
      const pre = h("div", { class: "diff" });
      for (const line of (j.diff || "No structural changes (Parts I–IV) between these versions.").split("\n"))
        pre.append(h("span", { class: line.startsWith("+") ? "add" : line.startsWith("-") ? "del" : line.startsWith("@@") ? "hunk" : null }, line + "\n"));
      out.replaceChildren(pre);
    } catch (e) { out.replaceChildren(h("p", { class: "error" }, "Diff failed: " + e.message)); }
  } }, "Compare");
  const text = markdown(c.parts_markdown.replace(/^## (Article [\d.]+ — .+)$/gm, "## $1"), { idPrefix: "" });
  text.querySelectorAll("h3").forEach(el => { if (/^article-/.test(el.id)) el.id = "art-" + el.id; });
  return panel("Charter", "CHARTER.md, charter/history/, charter/TIMELINE.md, charter-verify.py",
    h("p", {}, "Version ", h("strong", { class: "mono" }, "v" + c.version), " · log verification ",
      c.verify.ok ? badge("verified", "ok") : badge("FAILED", "bad"), " ", h("span", { class: "mono src" }, c.verify.summary)),
    h("h3", {}, "Articles (Parts I–IV)"), toc,
    h("h3", {}, "Amendment log"), log,
    h("h3", {}, "Structure timeline"), tl,
    h("h3", {}, "Compare two versions (Parts I–IV)"), h("p", {}, "From ", from, " to ", to, " ", diffBtn), out,
    h("h3", {}, "Parts I–IV, rendered"), h("div", { class: "charter-text" }, text));
}

function vVersioning() {
  const v = STATE.versioning;
  const repos = h("table", {}, h("tr", {}, ...["Repository", "HEAD", "Committed", "Subject", "Ahead of GitHub"].map(x => h("th", {}, x))),
    ...v.repos.map(r => r.hidden ? h("tr", {}, h("td", {}, r.name), h("td", { colspan: 4, class: "src" }, "hidden in public mode"))
      : h("tr", {}, h("td", {}, r.name), h("td", { class: "mono" }, r.head), h("td", { class: "mono" }, fmtTime(r.date)), h("td", {}, r.subject),
          h("td", {}, r.ahead == null ? "—" : r.ahead === 0 ? badge("in sync", "ok") : badge(r.ahead + " to push", "warn")))));
  const checks = h("table", {}, h("tr", {}, h("th", {}, "Check"), h("th", {}, "Status"), h("th", {}, "Detail")),
    ...v.checks.map(c => h("tr", {}, h("td", {}, c.name),
      h("td", {}, badge(c.status === "ok" ? "ok" : c.status === "fail" ? "FAIL" : c.status, c.status === "ok" ? "ok" : c.status === "fail" ? "bad" : "muted")),
      h("td", { class: "mono" }, c.detail))));
  const ev = v.travel.events;
  return panel("Versioning", "git (both repos), eventlog.py, charter-verify.py, edict.py, case.py, amendment.py",
    h("h3", {}, "Repositories"), repos, h("p", { class: "src" }, v.push_reminder),
    h("h3", {}, "Verification"), checks,
    h("h3", {}, "Backups and history"),
    h("ul", {},
      h("li", {}, "Last event-log backup: ", v.last_backup ? `event #${v.last_backup.seq}, ${fmtTime(v.last_backup.ts)}` : "none recorded yet (the private repo push is the backup; ledger-backup.sh records one)"),
      ev ? h("li", {}, `Event log: ${ev.count} events, #${ev.first?.seq} (${fmtTime(ev.first?.ts)}) to #${ev.last?.seq} (${fmtTime(ev.last?.ts)}). Earlier history is in git.`) : h("li", {}, "Event log: private (hidden in public mode)."),
      h("li", {}, `Public commits available for time travel: ${v.travel.commits.length}.`)),
    h("p", {}, "Use the time-travel bar above to render the whole dashboard at any commit, event, or date."));
}

function vSoon(p) {
  return h("section", { class: "panel soon-card" }, h("h2", {}, p.title),
    h("p", {}, `Planned for version ${String(p.version).padStart(3, "0")} of this project (see projects/001-dashboard/PROJECT.md, roadmap).`),
    h("p", {}, "Version 001 has the header, Mission, Charter, Versioning, and time travel."));
}

function render() {
  const id = (location.hash.match(/^#\/([\w-]+)/) || [])[1] || "mission";
  renderHeader(); renderRail(id); renderTravel();
  const p = STATE.panels.find(x => x.id === id) || STATE.panels[0];
  const main = $("#main");
  main.replaceChildren(p.id === "mission" ? vMission() : p.id === "charter" ? vCharter() : p.id === "versioning" ? vVersioning() : vSoon(p));
}

async function load() {
  $("#asof").textContent = AT === "live" ? "Loading…" : `Rebuilding the Collective as of ${AT}…`;
  try {
    const r = await fetch("/api/state?at=" + encodeURIComponent(AT));
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || r.status);
    STATE = j; render();
  } catch (e) {
    $("#asof").textContent = ""; $("#main").replaceChildren(h("section", { class: "panel" }, h("p", { class: "error" }, "Couldn't load: " + e.message)));
  }
}

function setAt(at) {
  AT = at; const u = new URL(location.href);
  if (at === "live") u.searchParams.delete("at"); else u.searchParams.set("at", at);
  history.pushState(null, "", u); load();
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = (() => { try { return localStorage.getItem("theme"); } catch { return null; } })();
  if (saved) document.documentElement.dataset.theme = saved;
  $("#theme").addEventListener("click", () => {
    const dark = matchMedia("(prefers-color-scheme: dark)").matches;
    const cur = document.documentElement.dataset.theme || (dark ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next; try { localStorage.setItem("theme", next); } catch {}
  });
  $("#travel-form").addEventListener("submit", e => {
    e.preventDefault();
    const kind = new FormData(e.target).get("kind");
    if (kind === "live") return setAt("live");
    if (kind === "commit") return setAt("commit:" + $("#t-commit").value);
    if (kind === "event") return $("#t-event").value && setAt("event:" + $("#t-event").value);
    if (kind === "date") return $("#t-date").value && setAt("date:" + new Date($("#t-date").value).toISOString().slice(0, 19) + "Z");
  });
  window.addEventListener("hashchange", () => STATE && render());
  window.addEventListener("popstate", () => { AT = new URLSearchParams(location.search).get("at") || "live"; load(); });
  try {
    const es = new EventSource("/api/stream");
    es.addEventListener("changed", () => { if (AT === "live" && STATE) load(); });
  } catch {}
  load();
});
