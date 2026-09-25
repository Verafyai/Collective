"""The Court (P-006): certainty, replay, family separation, and the case routes. No model calls.
Run: python3 tests/test_court.py   (reads the Record read-only; the server runs on a scratch copy)"""
import atexit, json, os, pathlib, shutil, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "court"))
import certainty as C

# ---- certainty is reproducible: recomputing from the Record gives the stored number, input for input ----
cases = [d for d in sorted((ROOT / "cases").glob("C*-*")) if (d / "case.json").exists()] if (ROOT / "cases").exists() else []
ruled = [json.loads((d / "case.json").read_text()) for d in cases]
ruled = [c for c in ruled if c.get("status") == "ruled"]
for c in ruled:
    again = C.compute(C.case_events(c["id"]))
    assert again["score"] == c["certainty"]["score"] and again["inputs"] == c["certainty"]["inputs"], (c["id"], again, c["certainty"])
    evs = C.case_events(c["id"])
    a = next(e for e in evs if e["type"] == "advocates.assigned")["data"]
    fams = [x["family"] for x in a["advocates"]]
    assert len(set(fams)) == len(fams) and a["judge"]["family"] not in fams, "every advocate on its own family; the Judge on none of theirs"
    assert [e["seq"] for e in evs] == sorted(e["seq"] for e in evs), "the replay is the Record's order"
    assert evs[0]["type"] == "case.filed" and evs[-1]["type"] in ("case.ruled", "case.error")
    if not c.get("test"): assert c.get("case_law") or c.get("case_law_draft"), "a real ruling becomes case law (filed, or drafted for the Scribe)"
real = [c for c in ruled if not c.get("test")]
assert real and any(e["type"] == "objection" and e["data"]["ruling"] == "sustained" for c in real for e in C.case_events(c["id"])), "at least one sustained objection"
poor = [c for c in ruled if c.get("test") and c.get("no_discovery")]
assert poor and all(c["ruling"]["final_holding"] == "insufficient" for c in poor), "an evidence-poor case is ruled insufficient"

# ---- the evidence fetcher takes tracked public files and public URLs only (the Lawyer's 2026-09-25 incident) ----
import court as CO
for bad in ["./agents/.env", "agents//.env", "./private/ledger/events.ndjson", "research/../private/ledger/HEAD.json", "../../../etc/hosts", "/etc/hosts",
            "agents/observability/.bridge_state", "http://127.0.0.1:4848/api/live", "http://localhost/", "http://10.0.0.1/", "file:///etc/hosts"]:
    assert CO.fetch(bad) == "", bad
assert CO.fetch("research/briefs/nine-judges-two-effective-votes.md"), "a tracked public file is fine"

# ---- the rules, on synthetic events ----
def ev(t, d, actor="x"): return {"type": t, "actor": actor, "data": {"case": "C-9999", "court": "court", **d}}
base = [ev("exhibit.admitted", {"exhibit": "X1", "reliability": 0.8, "independence_group": "g1"}),
        ev("exhibit.admitted", {"exhibit": "X2", "reliability": 0.6, "independence_group": "g1"}),
        ev("argument", {"position": "A", "claims": [{"id": "A1", "cites": ["X1"]}, {"id": "A2", "cites": ["X2"]}, {"id": "A3", "cites": []}]}),
        ev("argument", {"position": "B", "claims": [{"id": "B1", "cites": []}]})]
jury = ev("ballot.counted", {"ballots": [{"family": "f1", "vote": "A"}, {"family": "f2", "vote": "A"}, {"family": "f3", "vote": "B"}]})
judge = ev("judge.ruling", {"holding": "A", "confidence": 90, "rebutted_claims": []})
r0 = C.compute(base + [jury, judge])
r1 = C.compute(base + [ev("objection", {"claim": "A2", "ruling": "sustained"}), jury, judge])
assert r0["inputs"]["argument_survival"] > r1["inputs"]["argument_survival"], "a struck claim leaves argument survival"
assert r1["inputs"]["evidence_strength"] == 80.0, "a struck claim's exhibit no longer supports the holding (X1 only: 0.8, one group)"
assert r0["inputs"]["evidence_strength"] == round(0.7 * 0.5 * 100, 2), "two exhibits, one independence group: halved"
assert r0["score"] <= min(r0["inputs"]["evidence_strength"], r0["inputs"]["cross_family_agreement"]), "capped at the weaker of evidence and agreement"
assert C.compute(base + [jury, judge], judge_confidence=0)["score"] <= r0["score"], "the Judge's confidence has a low weight"
assert C.compute([jury, judge])["score"] == 0 and C.band(0)["band"] == "Insufficient" and C.band(47)["band"] == "Low" and C.band(80)["band"] == "High"
w = json.loads((ROOT / "court/certainty.json").read_text())["weights"]
assert abs(sum(w.values()) - 1) < 1e-9 and w["judge_confidence"] <= min(v for k, v in w.items() if k != "judge_confidence")

# ---- the routes, on a scratch copy with the Record's court events ----
t = pathlib.Path(tempfile.mkdtemp()) / "c"; atexit.register(shutil.rmtree, t.parent, True)
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".venv", "node_modules", ".git", "blobs", "logs", "pdfs", ".env", "secrets", "*.key", "gitleaks-rules.toml"))
with socket.socket() as s: s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
srv = subprocess.Popen([sys.executable, "dashboard/server.py", "--port", str(port)], cwd=t, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env={**os.environ, "COLLECTIVE_NO_REPLIES": "1", "OBS_OPS": "0"})
atexit.register(srv.terminate)
base_url = f"http://127.0.0.1:{port}"
def get(p):
    with urllib.request.urlopen(base_url + p, timeout=20) as r: return json.loads(r.read())
def post(p, body, origin=True):
    req = urllib.request.Request(base_url + p, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"Origin": base_url} if origin else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b"{}")
for _ in range(60):
    try: get("/api/cases"); break
    except Exception: time.sleep(0.2)
d = get("/api/cases")
assert d["provisional"] is True, "the Court is provisional until its amendment is ratified"
ids = {c["id"] for c in d["cases"]}
for c in ruled:
    assert c["id"] in ids
    detail = get(f"/api/cases/{c['id']}")
    assert detail["certainty"]["score"] == c["certainty"]["score"] and detail["transcript"] and detail["ruling_md"]
    rp = get(f"/api/cases/{c['id']}/replay")["events"]
    assert [e["seq"] for e in rp] == [e["seq"] for e in C.case_events(c["id"])], "the replay route serves exactly the Record's sequence"
assert "court" in get("/api/live") and isinstance(get("/api/live")["court"]["in_session"], list)
code, body = post("/api/cases", {"question": "short"}); assert code == 400, body
code, body = post("/api/cases", {"question": "Is this filing refused without an Origin header?"}, origin=False); assert code == 403, body
time.sleep(10.5)
code, body = post("/api/cases", {"question": "Does a filing from the Decisions tab reach the docket?", "positions": ["Yes", "No"], "budget": 50000})
assert code == 200 and body["ok"] and body["id"].startswith("C-"), body
assert any(c["id"] == body["id"] and c["status"] == "filed" for c in get("/api/cases")["cases"]), "filed, and not run (tests start no case)"
edicts = sorted((t / "private/edicts").glob("E-*.md"))
assert edicts and "File a case" in edicts[-1].read_text(), "a filing from the UI is recorded as the Steward's edict"
try: get("/api/cases/C-0000"); raise AssertionError("expected 404")
except urllib.error.HTTPError as e: assert e.code == 404
print("court tests passed")
