#!/usr/bin/env python3
"""Collective event log (Charter Article 12: Replayability).

Every change to the Collective's state is an event in an append-only, hash-chained log.
File contents live in a content-addressed blob store. State at any point =
replay of events up to that point (see replay.py).

Layout:
  private/ledger/events.ndjson     one JSON event per line (append-only)
  private/ledger/blobs/ab/cdef...  gzip'd content, named by SHA-256 of the raw bytes
  private/ledger/HEAD.json         {"seq", "hash", "manifest": {path: blob}}  (a cache;
                           always rebuildable from events)

Commands:
  eventlog.py init                               genesis: snapshot the whole tree
  eventlog.py sync  --actor A [--reason R] [--run ID]
                                                 record file changes since HEAD
  eventlog.py record --actor A --type T [--run ID] [--data JSON] [--blob-file F]
  eventlog.py run-start --actor A [--data JSON]  prints a run id
  eventlog.py run-end   --actor A --run ID [--data JSON]
  eventlog.py verify                             check the hash chain and HEAD
"""
import argparse, datetime, fnmatch, gzip, hashlib, json, os, pathlib, re, sys, uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "private" / "ledger"
EVENTS = LEDGER / "events.ndjson"
BLOBS = LEDGER / "blobs"
HEAD = LEDGER / "HEAD.json"
IGNORE_FILE = LEDGER / "ignore"
DEFAULT_IGNORE = [".git/*", "*/.git/*", "private/secrets/*.key", "private/ledger/*", "agents/.env", "*/logs/*", "*.pyc", "__pycache__/*",
                  "node_modules/*", ".venv/*", ".DS_Store", "*/.DS_Store", "org/STOP", "org/PAUSE-*"]
SECRET_RE = re.compile(
    r"(?<![A-Za-z0-9])sk-(ant-)?[A-Za-z0-9_-]{20,}|(?<![A-Za-z0-9])xai-[A-Za-z0-9]{20,}|gh[pous]_[A-Za-z0-9]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}"
    r"|\b\d{8,10}:[A-Za-z0-9_-]{35}\b|(?:API|SECRET|TOKEN|PASSWORD)[A-Z_]*=[^\s'\"]{6,}")

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def ignore_patterns():
    pats = list(DEFAULT_IGNORE)
    if IGNORE_FILE.exists():
        pats += [l.strip() for l in IGNORE_FILE.read_text().splitlines() if l.strip() and not l.startswith("#")]
    return pats

def ignored(rel: str, pats) -> bool:
    return any(fnmatch.fnmatch(rel, p) or rel.startswith(p.rstrip("*")) and p.endswith("/*") for p in pats)

def put_blob(data: bytes) -> tuple[str, bool]:
    """Store bytes; return (blob id, redacted?). Secrets are never stored."""
    redacted = False
    try:
        text = data.decode()
        if SECRET_RE.search(text):
            data = SECRET_RE.sub("[redacted: secret]", text).encode(); redacted = True
    except UnicodeDecodeError:
        pass
    h = sha(data)
    p = BLOBS / h[:2] / h[2:]
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(gzip.compress(data, mtime=0))
    return h, redacted

def get_blob(h: str) -> bytes:
    return gzip.decompress((BLOBS / h[:2] / h[2:]).read_bytes())

def scan_tree():
    pats = ignore_patterns(); out = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not p.is_symlink():
            rel = p.relative_to(ROOT).as_posix()
            if not ignored(rel, pats):
                out[rel] = p
    return out

def tree_hash(manifest: dict) -> str:
    return sha(canon(sorted(manifest.items())))

def load_head():
    if HEAD.exists():
        return json.loads(HEAD.read_text())
    return {"seq": 0, "hash": "GENESIS", "manifest": {}}

def append(head, actor, etype, run=None, data=None):
    ev = {"seq": head["seq"] + 1, "ts": now(), "actor": actor, "type": etype,
          "run": run, "data": data or {}, "prev": head["hash"]}
    ev["hash"] = sha(canon(ev))
    with EVENTS.open("a") as f:
        f.write(json.dumps(ev, sort_keys=True, ensure_ascii=False) + "\n")
    head["seq"], head["hash"] = ev["seq"], ev["hash"]
    return ev

def save_head(head):
    HEAD.write_text(json.dumps(head, indent=1, sort_keys=True))

def sync(head, actor, run=None, reason=None):
    """Record every file change since HEAD as file.put / file.delete events."""
    cur = scan_tree(); man = head["manifest"]; n = 0
    for rel, p in cur.items():
        data = p.read_bytes()
        h = sha(data)
        if man.get(rel) == h:
            continue
        bid, red = put_blob(data)
        if man.get(rel) == bid:
            continue
        mode = "755" if os.access(p, os.X_OK) else "644"
        append(head, actor, "file.put", run, {"path": rel, "blob": bid, "mode": mode,
                                              "redacted": red, **({"reason": reason} if reason else {})})
        if red:
            append(head, "system", "incident", run, {"kind": "secret_redacted", "path": rel})
        man[rel] = bid; n += 1
    for rel in [r for r in man if r not in cur]:
        append(head, actor, "file.delete", run, {"path": rel, **({"reason": reason} if reason else {})})
        del man[rel]; n += 1
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "sync", "record", "run-start", "run-end", "verify"])
    ap.add_argument("--actor", default="system"); ap.add_argument("--type")
    ap.add_argument("--run"); ap.add_argument("--data", default="{}")
    ap.add_argument("--blob-file"); ap.add_argument("--reason")
    a = ap.parse_args()
    LEDGER.mkdir(exist_ok=True); BLOBS.mkdir(exist_ok=True)
    data = json.loads(a.data)

    if a.cmd == "verify":
        prev, seq, man = "GENESIS", 0, {}
        for line in EVENTS.read_text().splitlines():
            ev = json.loads(line); h = ev.pop("hash")
            if ev["prev"] != prev or sha(canon(ev)) != h or ev["seq"] != seq + 1:
                print(f"FAIL at seq {ev['seq']}"); sys.exit(1)
            prev, seq = h, ev["seq"]
            if ev["type"] == "file.put": man[ev["data"]["path"]] = ev["data"]["blob"]
            elif ev["type"] == "file.delete": man.pop(ev["data"]["path"], None)
        head = load_head()
        ok = head["hash"] == prev and head["manifest"] == man
        print(f"{'ok' if ok else 'FAIL'}: {seq} events, chain intact, HEAD {'matches' if ok else 'DIFFERS FROM'} replay")
        sys.exit(0 if ok else 1)

    head = load_head()
    if a.cmd == "init":
        if EVENTS.exists() and EVENTS.stat().st_size:
            print("already initialized"); return
        append(head, a.actor or "steward", "org.genesis", None,
               {"charter_sha256": sha((ROOT / "CHARTER.md").read_bytes()) if (ROOT / "CHARTER.md").exists() else None})
        n = sync(head, a.actor or "steward", None, "genesis snapshot")
        append(head, "system", "state.checkpoint", None, {"tree": tree_hash(head["manifest"]), "files": len(head["manifest"])})
        save_head(head); print(f"genesis: {n} files, seq {head['seq']}")
    elif a.cmd == "sync":
        n = sync(head, a.actor, a.run, a.reason); save_head(head); print(n)
    elif a.cmd == "record":
        if a.blob_file:
            bid, red = put_blob(pathlib.Path(a.blob_file).read_bytes()); data = {**data, "blob": bid, "redacted": red}
        append(head, a.actor, a.type, a.run, data); save_head(head)
    elif a.cmd == "run-start":
        rid = f"{a.actor}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}"
        ext = sync(head, "external", rid, "changes found outside any recorded run")
        if ext:
            append(head, "system", "incident", rid, {"kind": "out_of_band_change", "files": ext})
        append(head, a.actor, "run.start", rid, data); save_head(head); print(rid)
    elif a.cmd == "run-end":
        n = sync(head, a.actor, a.run)
        append(head, a.actor, "run.end", a.run, {**data, "files_changed": n, "tree": tree_hash(head["manifest"])})
        save_head(head)

if __name__ == "__main__":
    main()
