#!/usr/bin/env python3
"""Play back the Collective's history as a readable timeline (Charter Article 12).

  playback.py [--from SEQ] [--to SEQ] [--actor ROLE] [--run RUN_ID] [--html OUT.html]
  playback.py --follow         live: print new events as they happen (Ctrl-C to stop)
Prints a timeline grouped by run. With --html, writes a self-contained page
with collapsible runs and full transcripts (from blobs) inline.
"""
import argparse, html, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eventlog as E

ICON = {"run.start": "▶", "run.end": "■", "file.put": "✎", "file.delete": "✗", "agent.transcript": "💬",
        "approval.granted": "✅", "approval.rejected": "⛔", "effect.posted": "📣", "incident": "⚠",
        "org.genesis": "✦", "org.rewound": "⏪", "state.checkpoint": "◆", "governance": "⚖",
        "project.created": "◇", "project.version": "◈", "project.released": "🚀", "project.comment": "✉",
        "amendment.proposed": "§", "amendment.status": "§", "edict.issued": "✎", "case.filed": "⚖"}

def line(e):
    d = e["data"]; t = e["type"]
    what = d.get("path") or d.get("summary") or d.get("kind") or d.get("file") or ""
    if t == "run.end": what = f"{d.get('files_changed', 0)} files changed · tree {d.get('tree', '')[:10]}"
    return f"{e['seq']:>6}  {e['ts'][:19]}  {ICON.get(t, '·')} {e['actor']:<11} {t:<18} {what}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", type=int, default=0); ap.add_argument("--to", type=int)
    ap.add_argument("--actor"); ap.add_argument("--run"); ap.add_argument("--html")
    ap.add_argument("--follow", action="store_true")
    a = ap.parse_args()
    if a.follow:
        import time
        print("Following the Collective's event log (Ctrl-C to stop)…", flush=True)
        seen = 0
        while True:
            if E.EVENTS.exists():
                lines = E.EVENTS.read_text().splitlines()
                for l in lines[seen:]:
                    e = json.loads(l)
                    if not a.actor or e["actor"] == a.actor: print(line(e), flush=True)
                seen = len(lines)
            time.sleep(1)
    evs = [json.loads(l) for l in E.EVENTS.read_text().splitlines()]
    evs = [e for e in evs if e["seq"] >= a.frm and (a.to is None or e["seq"] <= a.to)
           and (not a.actor or e["actor"] == a.actor) and (not a.run or e["run"] == a.run)]
    if not a.html:
        for e in evs: print(line(e))
        return
    rows = []
    for e in evs:
        body = ""
        if e["type"] == "agent.transcript" and "blob" in e["data"]:
            body = "<details><summary>transcript</summary><pre>" + html.escape(E.get_blob(e["data"]["blob"]).decode("utf-8", "replace")[:200000]) + "</pre></details>"
        rows.append(f"<div class='ev {html.escape(e['type'].split('.')[0])}'><code>{html.escape(line(e))}</code>{body}</div>")
    page = ("<!doctype html><meta charset=utf-8><title>Collective playback</title>"
            "<style>body{font:13px ui-monospace,monospace;background:#0f1216;color:#dfe6ee;padding:16px}"
            ".ev{padding:2px 0;border-bottom:1px solid #1d232b}.incident{color:#f0a36b}.approval{color:#7fd6a4}"
            ".org{color:#9fb4ff}pre{white-space:pre-wrap;background:#161b22;padding:8px}</style>"
            f"<h1>the Collective · events {evs[0]['seq'] if evs else 0}–{evs[-1]['seq'] if evs else 0}</h1>" + "".join(rows))
    pathlib.Path(a.html).write_text(page); print(f"wrote {a.html} ({len(evs)} events)")

if __name__ == "__main__":
    main()
