#!/usr/bin/env python3
"""Replay the Collective's event log (Charter Article 12).

  replay.py build  --out DIR [--to SEQ | --until ISO_TS | --run RUN_ID]
      Rebuild the Collective's files from scratch as they stood at that point, verifying
      every recorded tree hash on the way. Never touches the live repo.
  replay.py rewind --to SEQ | --until ISO_TS | --run RUN_ID   (Steward only)
      Bring the live repo back to that point. History is kept: the rewind is
      itself recorded as new events, so it can be undone by rewinding again.
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eventlog as E

def events():
    for line in E.EVENTS.read_text().splitlines():
        yield json.loads(line)

def stop_at(args):
    evs = list(events())
    if args.to: return args.to
    if args.until: return max([e["seq"] for e in evs if e["ts"] <= args.until] or [0])
    if args.run:
        ends = [e["seq"] for e in evs if e["run"] == args.run and e["type"] == "run.end"]
        if not ends: sys.exit(f"no run.end for {args.run}")
        return ends[-1]
    return evs[-1]["seq"]

def build(out: pathlib.Path, upto: int):
    man, modes, checked = {}, {}, 0
    for ev in events():
        if ev["seq"] > upto: break
        d = ev["data"]
        if ev["type"] == "file.put": man[d["path"]] = d["blob"]; modes[d["path"]] = d.get("mode", "644")
        elif ev["type"] == "file.delete": man.pop(d["path"], None)
        elif ev["type"] in ("run.end", "state.checkpoint") and "tree" in d:
            if E.tree_hash(man) != d["tree"]:
                sys.exit(f"FAIL: tree hash mismatch at seq {ev['seq']}")
            checked += 1
    out.mkdir(parents=True, exist_ok=True)
    for rel, bid in man.items():
        p = out / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(E.get_blob(bid)); os.chmod(p, 0o755 if modes.get(rel) == "755" else 0o644)
    return man, checked

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "rewind"])
    ap.add_argument("--out"); ap.add_argument("--to", type=int); ap.add_argument("--until"); ap.add_argument("--run")
    ap.add_argument("--i-am-steward", action="store_true")
    a = ap.parse_args(); upto = stop_at(a)
    if a.cmd == "build":
        out = pathlib.Path(a.out or f"replay-{upto}")
        man, checked = build(out, upto)
        print(f"rebuilt {len(man)} files at seq {upto} into {out} · {checked} checkpoints verified · tree {E.tree_hash(man)[:12]}")
    else:
        if not a.i_am_steward: sys.exit("REFUSED: rewind is a Steward action (pass --i-am-steward)")
        if not (E.ROOT / "org" / "STOP").exists(): sys.exit("REFUSED: stop the Collective first (touch org/STOP)")
        head = E.load_head()
        E.append(head, "steward", "org.rewind.start", None, {"to_seq": upto, "from_seq": head["seq"]}); E.save_head(head)
        with tempfile.TemporaryDirectory() as t:
            man, _ = build(pathlib.Path(t), upto)
            live = E.scan_tree()
            for rel in live:
                if rel not in man: (E.ROOT / rel).unlink()
            for rel in man:
                dst = E.ROOT / rel; dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pathlib.Path(t) / rel, dst)
        head = E.load_head()
        n = E.sync(head, "steward", None, f"rewind to seq {upto}")
        E.append(head, "steward", "org.rewound", None, {"to_seq": upto, "files_changed": n, "tree": E.tree_hash(head["manifest"])})
        E.save_head(head); print(f"rewound to seq {upto}: {n} files changed; org/STOP still in place")

if __name__ == "__main__":
    main()
