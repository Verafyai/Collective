#!/usr/bin/env python3
"""The Collective's structure over time (Charter Article 16).

  charter.py versions                     every Charter version, with its amendment
  charter.py show VERSION [--part N]      print a past version (or one Part of it)
  charter.py diff FROM TO [--all]         what changed in the structure (Parts I–IV; --all includes Part V)
  charter.py timeline                     rebuild charter/TIMELINE.md: how the structure evolved
  charter.py materialize [--dry-run] [--include-live]
                                          rewrite generated files from Part V of the current Charter
                                          (live records are skipped unless --include-live, for a fresh start)
  charter.py tag                          git-tag the current version (charter-vX.Y.Z) in the public repo
  charter.py rewind VERSION --i-am-steward
        Restore the structure (Parts I–V) of an earlier version as a NEW major version.
        The amendment log is never rewound: the rewind is appended as a new entry, so
        rewinding is itself reversible. Requires org/STOP.
"""
import argparse, difflib, hashlib, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHARTER = ROOT / "CHARTER.md"
HIST = ROOT / "charter" / "history"
PART_RE = re.compile(r"^# PART (\w+) — ", re.M)
FILE_RE = re.compile(r"## V\.\d+ `([^`]+)`\n\n````[a-z]*\n(.*?)\n````\n", re.S)

def vkey(v): return tuple(int(x) for x in v.split("."))
def version_of(text): return re.search(r"Charter version: ([\d.]+)", text).group(1)
def versions():
    out = {}
    for d in (HIST, ROOT / "private" / "charter-history"):   # private: versions that embedded private material
        for p in d.glob("CHARTER-v*.md"):
            out[p.stem.split("-v", 1)[1]] = p
    return dict(sorted(out.items(), key=lambda kv: vkey(kv[0])))

P5_HEAD = re.compile(r"^# PART V — ", re.M)
P6_HEAD = re.compile(r"\n---\n\n# PART VI — ")

def split(text):
    """Structure (Parts 0–V) and the amendment log (Part VI). Headers are matched with
    their em-dash titles, so Part V's embedded source code can't be mistaken for them."""
    i = [m.start() for m in P6_HEAD.finditer(text)][-1]
    return text[:i], text[i:]

def part(text, name):
    body = split(text)[0]
    marks = [(m.group(1), m.start()) for m in PART_RE.finditer(body)]
    for j, (n, s) in enumerate(marks):
        if n == name:
            return body[s: marks[j + 1][1] if j + 1 < len(marks) else len(body)].rstrip()
    sys.exit(f"no Part {name}")

def entry_for(text, ver):
    m = re.search(rf"### (A-\d{{4}}) · v{re.escape(ver)} · ([\d-]+) · Class (\w) · (.+)", text)
    return m.groups() if m else ("?", "?", "?", "?")

def stats(text):
    body = split(text)[0]
    p2 = part(text, "II") if "# PART II" in body else ""
    members = len(re.findall(r"^\| \d+ \| \*\*", p2, re.M))
    plugins = len(re.findall(r"^\| `[\w.-]+/[\w.-]+` \|.*\| (?:core|optional) \|\s*$", p2, re.M))
    return {"articles": len(re.findall(r"^## Article \d+", body, re.M)), "members": members,
            "plugins": plugins, "files": len(re.findall(r"^## V\.\d+ ", body, re.M))}

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

def event(etype, data):
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", "steward",
                    "--type", etype, "--data", json.dumps(data)], capture_output=True)

# Live records: seeded once on a fresh start, never overwritten by materialize.
LIVE = ("org/LEARNINGS.md", "org/board/", "org/cases/", "private/", "research/papers.md", "sprints/", "projects/", "amendments/", "agents/roster.json")

def materialize(text, dry=False, include_live=False):
    body = split(text)[0]
    p5 = body[P5_HEAD.search(body).start():]
    changed = []
    for m in FILE_RE.finditer(p5):
        if not include_live and m.group(1).startswith(LIVE):
            continue
        path, content = ROOT / m.group(1), m.group(2) + "\n"
        if not path.exists() or path.read_text() != content:
            changed.append(m.group(1))
            if not dry:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
                if "/bin/" in m.group(1) or m.group(1).endswith(".sh"):   # every script, including launch.sh
                    path.chmod(0o755)
    return changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["versions", "show", "diff", "timeline", "materialize", "tag", "rewind"])
    ap.add_argument("args", nargs="*"); ap.add_argument("--part"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--i-am-steward", action="store_true")
    ap.add_argument("--include-live", action="store_true", help="also write seed records (fresh start only)")
    a = ap.parse_args(); vs = versions(); cur = CHARTER.read_text()

    if a.cmd == "versions":
        for v, p in vs.items():
            aid, date, cls, title = entry_for(p.read_text(), v)
            mark = "  ← current" if v == version_of(cur) else ""
            print(f"v{v:<8} {aid}  {date}  Class {cls}  {title}{mark}")
    elif a.cmd == "show":
        t = vs[a.args[0].lstrip("v")].read_text()
        print(part(t, a.part) if a.part else t)
    elif a.cmd == "diff":
        f, t = (vs[x.lstrip("v")].read_text() for x in a.args[:2])
        def struct(x):
            b = split(x)[0]
            return (b if a.all else b[:P5_HEAD.search(b).start()]).splitlines()
        sys.stdout.writelines(l + "\n" for l in difflib.unified_diff(struct(f), struct(t), f"v{a.args[0].lstrip('v')}", f"v{a.args[1].lstrip('v')}", lineterm="", n=1))
    elif a.cmd == "timeline":
        rows = ["# How the Collective's structure evolved", "", "Generated by `agents/bin/charter.py timeline` from `charter/history/`. Rewind any version with `charter.py rewind` (Steward).", "",
                "| Version | Date | Amendment | Class | Change | Articles | Members | Plugins | Generated files |", "|---|---|---|---|---|---|---|---|---|"]
        for v, p in vs.items():
            t = p.read_text(); aid, date, cls, title = entry_for(t, v); s = stats(t)
            rows.append(f"| v{v} | {date} | {aid} | {cls} | {title} | {s['articles']} | {s['members']} | {s['plugins']} | {s['files']} |")
        (ROOT / "charter" / "TIMELINE.md").write_text("\n".join(rows) + "\n"); print("\n".join(rows[4:]))
    elif a.cmd == "materialize":
        ch = materialize(cur, a.dry_run, a.include_live)
        print(("would change" if a.dry_run else "rewrote") + f" {len(ch)} files" + (": " + ", ".join(ch[:10]) if ch else ""))
    elif a.cmd == "tag":
        v = version_of(cur)
        r = subprocess.run(["git", "-C", str(ROOT), "tag", "-f", f"charter-v{v}"], capture_output=True, text=True)
        print(f"tagged charter-v{v}" if r.returncode == 0 else f"not tagged: {r.stderr.strip()}")
    elif a.cmd == "rewind":
        if not a.i_am_steward: sys.exit("REFUSED: rewinding the Charter is a Steward action (pass --i-am-steward)")
        if not (ROOT / "org" / "STOP").exists(): sys.exit("REFUSED: stop the Collective first (touch org/STOP)")
        target = a.args[0].lstrip("v")
        if target not in vs: sys.exit(f"no version {target}; see `charter.py versions`")
        now_v = version_of(cur); new_v = f"{vkey(now_v)[0] + 1}.0.0"
        old_struct = split(vs[target].read_text())[0].replace(f"Charter version: {target}", f"Charter version: {new_v}", 1)
        log = split(cur)[1]
        entries = re.findall(r"### (A-\d{4}) ·", log); aid = f"A-{len(entries) + 1:04d}"
        prev = re.findall(r"entry_hash: ([0-9a-f]{64})", log)[-1]
        doc = old_struct + log.rstrip("\n") + "\n"
        csha = sha(doc); eh = sha(prev + csha + aid)
        today = __import__("datetime").date.today().isoformat()
        entry = f"""
### {aid} · v{new_v} · {today} · Class A · Reversion to v{target}
proposed_by: Steward
thread: charter rewind (Article 7.8, Article 16)
change: Structure (Parts I–V) restored from v{target}, replacing v{now_v}. The amendment log is unchanged and continues; rewind forward by rewinding to v{now_v}.
vote: Steward action
ratified_by: Steward
charter_sha256_before_entry: {csha}
prev_entry_hash: {prev}
entry_hash: {eh}
"""
        CHARTER.write_text(doc + entry)
        (HIST / f"CHARTER-v{new_v}.md").write_text(doc + entry)
        ch = materialize(doc + entry)
        event("charter.rewound", {"summary": f"v{now_v} → structure of v{target} as v{new_v}", "amendment": aid})
        print(f"rewound: structure of v{target} is now v{new_v} ({aid}); {len(ch)} generated files rewritten; org/STOP still in place")

if __name__ == "__main__":
    main()
