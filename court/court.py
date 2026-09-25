#!/usr/bin/env python3
"""The Court (P-006; specs/steward-2026-09-25-the-court.md). A question becomes a case; advocates on different model
families argue assigned positions from admitted exhibits through fusion-harness; the Judge rules; jurors cast sealed
ballots; deterministic code scores the certainty. Every phase is an event in the Record (data.court = "court"), which is
also what the courtroom view replays and what the Weave bridge traces as one conversation per case.

  court.py file --question Q [--position "A: ..." --position "B: ..."] [--link URL|PATH ...] [--priority normal]
                [--budget 150000] [--filer steward] [--private] [--no-discovery]     prints the case id
  court.py run C-NNNN          run a filed case to its ruling (the dashboard starts this in the background)
  court.py show C-NNNN         the case as JSON
  court.py families            the model families available here

Provisional: until the Court's amendment is ratified, the UI says "Provisional court" and rulings are filed as officer
cases (Article 13.1), the lowest rank, with the provisional Court as their source.
"""
import argparse, datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
CERT = ROOT / "court/certainty.py"
sys.path.insert(0, str(ROOT / "court"))
import certainty as C

# ---------- model families ----------
MODELS = {   # model -> family; every one reachable here (Anthropic and xAI keys; W&B Inference with the W&B key)
    "anthropic/claude-sonnet-5": "anthropic", "xai/grok-4.7": "xai", "wandb/deepseek-ai/DeepSeek-V4-Pro": "deepseek",
    "wandb/Qwen/Qwen3-235B-A22B-Instruct-2507": "qwen", "wandb/moonshotai/Kimi-K2.6": "moonshot", "wandb/zai-org/GLM-5.2": "zai",
    "wandb/openai/gpt-oss-120b": "openai", "wandb/meta-llama/Llama-3.3-70B-Instruct": "meta"}
ADVOCATE_MODELS = ["anthropic/claude-sonnet-5", "xai/grok-4.7", "wandb/Qwen/Qwen3-235B-A22B-Instruct-2507", "wandb/meta-llama/Llama-3.3-70B-Instruct"]
JUDGE_MODEL = "wandb/deepseek-ai/DeepSeek-V4-Pro"
JURY_MODELS = ["wandb/moonshotai/Kimi-K2.6", "wandb/zai-org/GLM-5.2", "wandb/openai/gpt-oss-120b"]
ADVOCATE_OFFICES = ["researcher", "prototyper", "getscholar", "dave"]   # assigned in this order; they don't choose (never a neutral officer)
JURY_OFFICES = ["pm", "social", "ideas"]                               # voting offices not arguing this case

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def sha(t): return hashlib.sha256(t.encode() if isinstance(t, str) else t).hexdigest()
def env_from_file():
    for k in ("ANTHROPIC_API_KEY", "XAI_API_KEY", "WANDB_API_KEY"):
        if not os.environ.get(k):
            m = re.search(rf"^{k}=(.+)$", (ROOT / "agents/.env").read_text(), re.M)
            if m: os.environ[k] = m.group(1).strip().strip("'\"")

def provisional():
    """The Court is provisional until the amendment titled below is ratified in the Charter's log."""
    s = (ROOT / "CHARTER.md").read_text(); log = s[[m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", s)][-1]:]
    return not re.search(r"^### A-\d{4} · v[\d.]+ · \S+ · Class \w · The Court\b.*?\nratified_by: \S", log, re.S | re.M)

# ---------- the record ----------
def record(cid, etype, actor, data):
    """One court event in the Record (hash-chained, Article 12). Turns are the Court's: the actor is "court" and the seat says
    which chair spoke (a model seated for an office, never the office itself); the Steward and the system act as themselves."""
    payload = {"case": cid, "court": "court", **data}
    if actor not in ("steward", "system"): payload["seat"], actor = actor, "court"
    r = subprocess.run([PY, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", actor, "--type", etype, "--data", json.dumps(payload)],
                       capture_output=True, text=True, env={**os.environ, "OBS_OPS": "0"})
    if r.returncode: raise RuntimeError(f"the Record refused {etype}: {r.stderr[-200:]}")
    return payload

def case_dir(cid, private=None):
    for base in (ROOT / "cases", ROOT / "private/cases"):
        if (base / cid).exists(): return base / cid
    return (ROOT / ("private/cases" if private else "cases")) / cid

def load(cid): return json.loads((case_dir(cid) / "case.json").read_text())
def save(cid, c):
    d = case_dir(cid, c.get("private")); d.mkdir(parents=True, exist_ok=True)
    (d / "case.json").write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n")

def next_case_id(test=False):
    if test:
        n = [int(p.name[3:]) for p in (ROOT / "cases").glob("CT-*") if re.fullmatch(r"CT-\d{4}", p.name)] if (ROOT / "cases").exists() else []
        return f"CT-{max(n + [0]) + 1:04d}"
    nums = [int(p.name[2:6]) for p in (ROOT / "org/cases").glob("C-*.md")] + [int(p.name[2:]) for base in (ROOT / "cases", ROOT / "private/cases")
            if base.exists() for p in base.glob("C-*") if re.fullmatch(r"C-\d{4}", p.name)]
    return f"C-{max(nums) + 1:04d}"

# ---------- turns through fusion-harness ----------
def turns(jobs, c):
    """Run turns in parallel through court/fh_court.ts (fusion-harness's runChild). Counts tokens against the case budget."""
    env_from_file()
    agent_dir = tempfile.mkdtemp(prefix="court-pi-"); shutil.copy(ROOT / "court/pi/models.json", agent_dir)
    try:
        r = subprocess.run(["node", str(ROOT / "court/fh_court.ts")], input=json.dumps(jobs), capture_output=True, text=True,
                           env={**os.environ, "PI_CODING_AGENT_DIR": agent_dir}, timeout=900)
    finally: shutil.rmtree(agent_dir, True)
    try: out = {x["id"]: x for x in json.loads(r.stdout)}
    except ValueError: raise RuntimeError(f"fusion-harness driver failed: {(r.stdout + r.stderr)[-400:]}")
    for x in out.values():
        c["spent_tokens"] = c.get("spent_tokens", 0) + (x.get("tokensIn") or 0) + (x.get("tokensOut") or 0)
        c["spent_usd"] = round(c.get("spent_usd", 0) + (x.get("costUsd") or 0), 6)
    return out

def as_json(text):
    text = re.sub(r"^```(json)?|```$", "", (text or "").strip(), flags=re.M)
    m = re.search(r"\{.*\}", text, re.S)
    try: return json.loads(m.group(0)) if m else {}
    except ValueError: return {}

def over_budget(c): return c.get("spent_tokens", 0) >= c.get("budget_tokens", 150000)

# ---------- evidence ----------
def tracked(src):
    """A local exhibit must be a file git tracks in the public tree: resolved inside the repo, never under private/,
    never an env file (the Lawyer's 2026-09-25 incident: prefix checks on the raw string were bypassable)."""
    try: p = (ROOT / src).resolve()
    except (OSError, RuntimeError): return None
    if not p.is_relative_to(ROOT) or p.is_relative_to(ROOT / "private") or p.name.startswith(".env") or not p.is_file(): return None
    rel = str(p.relative_to(ROOT))
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=ROOT, capture_output=True, text=True)
    return p if r.returncode == 0 else None

def public_url(url):
    """http(s) to a public address only: no loopback, private, link-local, or reserved hosts (checked on every redirect)."""
    import ipaddress, socket, urllib.parse
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname: return False
    try: addrs = {a[4][0] for a in socket.getaddrinfo(u.hostname, u.port or (443 if u.scheme == "https" else 80))}
    except OSError: return False
    for a in addrs:
        ip = ipaddress.ip_address(a.split("%")[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified: return False
    return True

class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not public_url(newurl): raise urllib.error.URLError(f"redirect to a non-public address refused: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)
_opener = urllib.request.build_opener(_SafeRedirect)

def _get(url, limit):
    if not public_url(url): return None
    with _opener.open(urllib.request.Request(url, headers={"User-Agent": "collective-court/1.0"}), timeout=40) as r: return r.read(limit).decode("utf-8", "replace")

def fetch(src, limit=60000):
    """An exhibit's text: a tracked repo file, or a public web page (arXiv's full HTML when there is one). Anything else: ""."""
    src = str(src or "").strip()
    if not re.match(r"^https?://", src):
        p = tracked(src)
        return p.read_text(errors="replace")[:limit] if p else ""
    url = src
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", src)
    if m: url = f"https://arxiv.org/html/{m.group(1)}"
    body = None
    try: body = _get(url, 2_000_000)
    except Exception:
        if m:
            try: body = _get(f"https://export.arxiv.org/api/query?id_list={m.group(1)}", 2_000_000)
            except Exception: body = None
    if not body: return ""
    text = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", " ", body))
    return re.sub(r"\s+", " ", text)[:limit]

CATALOG = ["research/briefs/nine-judges-two-effective-votes.md", "research/briefs/ising-dependence-aware-aggregation.md",
           "research/briefs/more-debate-same-evidence.md", "research/library/LIBRARY.md", "research/papers.md", "evals/results/E1.json",
           "evals/REGISTRY.md", "projects/002-verafy-bench/spec.md", "ideas/panel-illusion.md"]

def discovery(cid, c):
    """The Researcher proposes exhibits; each is fetched, hashed, and stored; the Judge admits or excludes each."""
    d = case_dir(cid, c.get("private")); (d / "exhibits").mkdir(parents=True, exist_ok=True)
    catalog = [p for p in CATALOG if (ROOT / p).exists()] + c.get("links", [])
    ask = (f"QUESTION: {c['question']}\nPOSITIONS: {json.dumps(c['positions'])}\n\nAvailable sources (repo paths or links):\n" + "\n".join(f"- {p}" for p in catalog) +
           "\n\nYou're gathering evidence for the Court. Pick up to 6 sources that bear on the question, for EITHER side (don't take a side). For each, "
           "rate reliability 0 to 1 (peer review, replication, sample size, conflicts), and give an independence group: sources that rest on the same "
           "underlying study or data share a group (different papers are different groups unless one reuses the other's data). Give the date only "
           "if the source states it; otherwise \"unknown\". Reply with only JSON: "
           '{"exhibits": [{"source": "...", "title": "...", "date": "YYYY or YYYY-MM-DD", "reliability": 0.0, "independence_group": "...", "why": "one sentence"}]}')
    role = (ROOT / "agents/researcher/ROLE.md").read_text()
    if c.get("no_discovery"): out = {"text": "{}"}
    else: out = turns([{"id": "discovery", "model": ADVOCATE_MODELS[0], "system": role + "\n\nYou are serving the Court as its evidence gatherer.", "prompt": ask}], c)["discovery"]
    allowed = set(catalog)                       # only the catalog and the filer's own links: never a path the model made up
    picks = [x for x in (as_json(out["text"]).get("exhibits") or []) if str(x.get("source", "")).strip() in allowed][:6] if not c.get("no_discovery") else []
    exhibits = []
    for i, x in enumerate(picks, 1):
        xid = f"{cid}-X{i:02d}"; text = fetch(str(x.get("source", "")))
        h = sha(text) if text else None
        if text:        # a web page's text may be someone else's copyright: it stays in the private repo; its hash and source are public
            home = (ROOT / "private/cases" / cid / "exhibits") if str(x.get("source", "")).startswith("http") else (d / "exhibits")
            home.mkdir(parents=True, exist_ok=True); (home / f"X{i:02d}.txt").write_text(text)
        exhibits.append({"id": xid, "source": x.get("source"), "title": x.get("title"), "date": x.get("date"), "reliability": max(0.0, min(1.0, float(x.get("reliability") or 0))),
                         "independence_group": x.get("independence_group") or xid, "why": x.get("why"), "sha256": h, "chars": len(text), "fetched": bool(text)})
    # the Judge rules on admission
    listing = "\n".join(f"{x['id']}: {x['title']} ({x['source']}), {x['date']}, reliability {x['reliability']}, fetched: {x['fetched']}, "
                        f"excerpt: {(fetch_text(d, x)[:600]).strip()}" for x in exhibits)
    rulings = {}
    if exhibits:
        jr = turns([{"id": "admit", "model": JUDGE_MODEL, "system": JUDGE_SYSTEM, "prompt": f"QUESTION: {c['question']}\n\nProposed exhibits:\n{listing}\n\n"
                     "Rule on each: admit it if it's relevant, fetched, and from an identifiable source; exclude it otherwise. Reply with only JSON: "
                     '{"rulings": [{"exhibit": "C-NNNN-X01", "admitted": true, "reason": "one sentence"}]}'}], c)["admit"]
        rulings = {r.get("exhibit"): r for r in as_json(jr["text"]).get("rulings", [])}
    for x in exhibits:
        r = rulings.get(x["id"], {"admitted": x["fetched"], "reason": "no ruling returned; admitted only if fetched"})
        x["admitted"] = bool(r.get("admitted")) and x["fetched"]; x["ruling_reason"] = r.get("reason")
        record(cid, "exhibit.admitted" if x["admitted"] else "exhibit.excluded", "judge",
               {"exhibit": x["id"], "title": x["title"], "source": x["source"], "reliability": x["reliability"], "independence_group": x["independence_group"],
                "sha256": x["sha256"], "reason": x["ruling_reason"]})
    (d / "exhibits" / "exhibits.json").write_text(json.dumps(exhibits, indent=1, ensure_ascii=False) + "\n")
    c["exhibits"] = exhibits

def fetch_text(d, x):
    for p in (d / "exhibits" / f"{x['id'][-3:]}.txt", ROOT / "private/cases" / d.name / "exhibits" / f"{x['id'][-3:]}.txt"):
        if p.exists(): return p.read_text()
    return ""

# ---------- the argument ----------
JUDGE_SYSTEM = ("You are the Judge of the Collective's Court. You are neutral: you weigh only the admitted exhibits and the arguments. You rule on "
                "admission of evidence, objections, and the case. Every factual claim must cite an exhibit ID; an uncited or misrepresented claim should "
                "be struck when an advocate objects. 'Insufficient evidence' is a proper ruling when the exhibits don't settle the question.")
def advocate_system(office, position):
    role = (ROOT / f"agents/{office}/ROLE.md").read_text() if (ROOT / f"agents/{office}/ROLE.md").exists() else ""
    return (f"{role}\n\nYou are serving the Court as an advocate. You have been ASSIGNED this position (you didn't choose it; argue it as well as the "
            f"evidence honestly allows): {position}\nRules: every factual claim cites at least one admitted exhibit ID (like C-0012-X01) from the "
            "exhibit list; never invent evidence; if an exhibit cuts against you, say so. Reply only with the JSON the prompt asks for.")

def exhibit_packet(c):
    d = case_dir(c["id"], c.get("private"))
    return "\n\n".join(f"[{x['id']}] {x['title']} ({x['source']}, {x['date']}, reliability {x['reliability']})\n{fetch_text(d, x)[:2200]}"
                       for x in c["exhibits"] if x.get("admitted"))

CLAIMS_JSON = '{"summary": "one or two sentences", "claims": [{"text": "one factual claim", "cites": ["C-NNNN-X01"]}]}'

def argument_round(cid, c, rnd, kind, prior):
    jobs = []
    for a in c["advocates"]:
        others = "\n\n".join(f"{p['position_id']} ({p['agent']}): " + " | ".join(f"[{cl['id']}] {cl['text']} (cites {', '.join(cl['cites']) or 'nothing'})" for cl in p["claims"])
                             for p in prior if p["position_id"] != a["position_id"])
        task = {"opening": "Give your OPENING: your strongest 2 to 4 claims.",
                "rebuttal": "Give your REBUTTAL: answer the other side's claims above, and add at most 2 new claims.",
                "closing": "Give your CLOSING: your 2 to 3 claims that best survive the debate."}[kind]
        jobs.append({"id": a["agent"], "model": a["model"], "system": advocate_system(a["agent"], a["position"]),
                     "prompt": f"QUESTION: {c['question']}\n\nADMITTED EXHIBITS:\n{exhibit_packet(c)}\n\n" + (f"THE OTHER SIDE SO FAR:\n{others}\n\n" if others else "") +
                               f"{task} Reply with only JSON: {CLAIMS_JSON}"})
    out = turns(jobs, c); stmts = []
    for a in c["advocates"]:
        j = as_json(out[a["agent"]]["text"]); n = 0; claims = []
        admitted = {x["id"] for x in c["exhibits"] if x.get("admitted")}
        for cl in (j.get("claims") or [])[:5]:
            n += 1; cites = [x for x in (cl.get("cites") or []) if isinstance(x, str)]
            claims.append({"id": f"{cid}-R{rnd}-{a['position_id']}{n}", "text": str(cl.get("text", ""))[:600], "cites": cites,
                           "cites_admitted": [x for x in cites if x in admitted]})
        o = out[a["agent"]]
        ev = record(cid, "argument", a["agent"], {"round": rnd, "kind": kind, "position": a["position_id"], "summary": str(j.get("summary", ""))[:400],
                                                  "claims": claims, "model": a["model"], "family": a["family"], "tokens_in": o.get("tokensIn"), "tokens_out": o.get("tokensOut"),
                                                  "error": o.get("error") if not claims else None})
        stmts.append({"position_id": a["position_id"], "agent": a["agent"], "claims": claims, "summary": ev["summary"], "kind": kind, "round": rnd})
    return stmts

def objections(cid, c, stmts):
    """Each advocate may object to the other side's claims (uncited, or misrepresenting an exhibit); the Judge rules on each."""
    jobs = []
    for a in c["advocates"]:
        theirs = [cl for s in stmts if s["position_id"] != a["position_id"] for cl in s["claims"]]
        if not theirs: continue
        jobs.append({"id": a["agent"], "model": a["model"], "system": advocate_system(a["agent"], a["position"]),
                     "prompt": f"ADMITTED EXHIBITS:\n{exhibit_packet(c)}\n\nTHE OTHER SIDE'S LATEST CLAIMS:\n" +
                               "\n".join(f"[{cl['id']}] {cl['text']} (cites {', '.join(cl['cites']) or 'nothing'})" for cl in theirs) +
                               "\n\nObject ONLY to claims that cite no admitted exhibit, or that misrepresent what the cited exhibit says. At most 2 objections. "
                               'Reply with only JSON: {"objections": [{"claim": "C-NNNN-R1-A1", "ground": "uncited" or "misrepresents", "why": "one sentence"}]}'})
    if not jobs: return []
    out = turns(jobs, c); objs = []
    ids = {cl["id"]: cl for s in stmts for cl in s["claims"]}
    for a in c["advocates"]:
        for o in (as_json(out.get(a["agent"], {}).get("text", "")).get("objections") or [])[:2]:
            if o.get("claim") in ids and not ids[o["claim"]]["id"].split("-R")[1][2:].startswith(a["position_id"]):
                objs.append({"by": a["agent"], "claim": o["claim"], "ground": o.get("ground", ""), "why": str(o.get("why", ""))[:300]})
    if not objs: return []
    listing = "\n".join(f"{i}. {o['by']} objects to [{o['claim']}] \"{ids[o['claim']]['text']}\" (cites {', '.join(ids[o['claim']]['cites']) or 'nothing'}) on ground "
                        f"'{o['ground']}': {o['why']}" for i, o in enumerate(objs))
    jr = turns([{"id": "objections", "model": JUDGE_MODEL, "system": JUDGE_SYSTEM, "prompt": f"ADMITTED EXHIBITS:\n{exhibit_packet(c)}\n\nOBJECTIONS:\n{listing}\n\n"
                 "Rule on each: sustained (the claim is uncited or misrepresents its exhibit; it is struck) or overruled. Reply with only JSON: "
                 '{"rulings": [{"n": 0, "ruling": "sustained" or "overruled", "reason": "one sentence"}]}'}], c)["objections"]
    rl = {r.get("n"): r for r in as_json(jr["text"]).get("rulings", [])}
    for i, o in enumerate(objs):
        r = rl.get(i, {"ruling": "sustained" if not ids[o["claim"]]["cites_admitted"] else "overruled", "reason": "no ruling returned; decided by whether it cites an admitted exhibit"})
        o["ruling"] = "sustained" if str(r.get("ruling", "")).lower().startswith("sustain") else "overruled"; o["reason"] = r.get("reason")
        record(cid, "objection", o["by"], {"claim": o["claim"], "ground": o["ground"], "why": o["why"], "ruling": o["ruling"], "reason": o["reason"], "judge_model": JUDGE_MODEL})
    return objs

def bench_questions(cid, c, transcript):
    jr = turns([{"id": "q", "model": JUDGE_MODEL, "system": JUDGE_SYSTEM, "prompt": f"QUESTION: {c['question']}\n\nTRANSCRIPT SO FAR:\n{transcript}\n\n"
                 "Ask each advocate ONE pointed question that would help you rule. Reply with only JSON: "
                 '{"questions": [{"to": "' + '" or "'.join(a["agent"] for a in c["advocates"]) + '", "question": "..."}]}'}], c)["q"]
    qs = [q for q in (as_json(jr["text"]).get("questions") or []) if q.get("to") in {a["agent"] for a in c["advocates"]}][:len(c["advocates"])]
    if not qs: return []
    by = {a["agent"]: a for a in c["advocates"]}
    out = turns([{"id": q["to"], "model": by[q["to"]]["model"], "system": advocate_system(q["to"], by[q["to"]]["position"]),
                  "prompt": f"ADMITTED EXHIBITS:\n{exhibit_packet(c)}\n\nThe Judge asks you: {q['question']}\nAnswer in at most 3 sentences, citing exhibit IDs. "
                            'Reply with only JSON: {"answer": "..."}'} for q in qs], c)
    res = []
    for q in qs:
        ans = str(as_json(out[q["to"]]["text"]).get("answer", out[q["to"]]["text"]))[:900]
        record(cid, "question", "judge", {"to": q["to"], "question": str(q["question"])[:500], "answer": ans, "judge_model": JUDGE_MODEL})
        res.append({"to": q["to"], "question": q["question"], "answer": ans})
    return res

# ---------- jury, ruling, and filing ----------
def jury(cid, c, transcript):
    pos = "\n".join(f"{p['id']}: {p['text']}" for p in c["positions"])
    jobs = [{"id": j["agent"], "model": j["model"], "system": ((ROOT / f"agents/{j['agent']}/ROLE.md").read_text() if (ROOT / f"agents/{j['agent']}/ROLE.md").exists() else "") +
             "\n\nYou are a juror of the Collective's Court. Vote on the evidence and the arguments alone.",
             "prompt": f"QUESTION: {c['question']}\nPOSITIONS:\n{pos}\n\nTRANSCRIPT (struck claims marked STRUCK):\n{transcript}\n\n"
                       'Cast your sealed ballot. Reply with only JSON: {"vote": "' + '" or "'.join(p["id"] for p in c["positions"]) + '" or "insufficient", "reason": "at most two sentences"}'}
            for j in c["jury"]]
    out = turns(jobs, c); ballots = []
    for j in c["jury"]:
        b = as_json(out[j["agent"]]["text"]); vote = str(b.get("vote", "insufficient")).strip()
        vote = vote if vote in {p["id"] for p in c["positions"]} else "insufficient"
        ballot = {"juror": j["agent"], "family": j["family"], "model": j["model"], "vote": vote, "reason": str(b.get("reason", ""))[:400]}
        seal = sha(json.dumps(ballot, sort_keys=True))
        record(cid, "ballot.sealed", j["agent"], {"seal": seal, "family": j["family"], "model": j["model"]})
        ballots.append({**ballot, "seal": seal})
    # the deterministic count (the Collective's vote counter, gov-tally.py) on the leading position vs. everything else
    tallies = {p["id"]: sum(1 for b in ballots if b["vote"] == p["id"]) for p in c["positions"]}
    tallies["insufficient"] = sum(1 for b in ballots if b["vote"] == "insufficient")
    lead = max(c["positions"], key=lambda p: (tallies[p["id"]], p["id"] == c["positions"][0]["id"]))["id"]
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t) / cid; (d / "ballots").mkdir(parents=True)
        (d / "amendment.json").write_text(json.dumps({"id": cid, "class": "C", "frozen_sha256": sha(c["question"]), "members": [b["juror"] for b in ballots],
                                                      "affects_privileges": False}))
        for b in ballots:
            (d / "ballots" / f"{b['juror']}.md").write_text(f"vote: {'yes' if b['vote'] == lead else ('abstain' if b['vote'] == 'insufficient' else 'no')}\n"
                                                             f"self_interest: no\nreason: {b['reason'][:300]}\nfrozen_sha256: {sha(c['question'])}\n")
        r = subprocess.run([PY, str(ROOT / "agents/bin/gov-tally.py"), str(d)], capture_output=True, text=True, env={**os.environ, "OBS_OPS": "0"})
        count = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
    record(cid, "ballot.counted", "system", {"ballots": ballots, "tallies": tallies, "leading": lead, "counter": "agents/bin/gov-tally.py", "count": count})
    return ballots, tallies

def rule(cid, c, transcript, tallies):
    pos = "\n".join(f"{p['id']}: {p['text']}" for p in c["positions"])
    jr = turns([{"id": "ruling", "model": JUDGE_MODEL, "system": JUDGE_SYSTEM, "thinking": "medium",
                 "prompt": f"QUESTION: {c['question']}\nPOSITIONS:\n{pos}\n\nADMITTED EXHIBITS:\n{exhibit_packet(c)}\n\nTRANSCRIPT (struck claims marked STRUCK):\n{transcript}\n\n"
                           f"THE JURY'S COUNT: {json.dumps(tallies)}\n\nIssue your ruling. Reply with only JSON: "
                           '{"holding": "' + '" or "'.join(p["id"] for p in c["positions"]) + '" or "insufficient", "holding_text": "one sentence", '
                           '"reasoning": [{"point": "...", "cites": ["C-NNNN-X01"]}], "dissent": "any dissent, including disagreement with the jury, or empty", '
                           '"confidence": 0 to 100, "rebutted_claims": ["claim ids of the PREVAILING side that the other side successfully rebutted"], '
                           '"reopen_conditions": ["what new evidence would change this ruling"]}'}], c)["ruling"]
    j = as_json(jr["text"]); hold = str(j.get("holding", "insufficient"))
    hold = hold if hold in {p["id"] for p in c["positions"]} | {"insufficient"} else "insufficient"
    ruling = {"holding": hold, "holding_text": str(j.get("holding_text", ""))[:500], "reasoning": (j.get("reasoning") or [])[:8], "dissent": str(j.get("dissent", ""))[:800],
              "confidence": max(0, min(100, int(float(j.get("confidence") or 0)))), "rebutted_claims": [x for x in (j.get("rebutted_claims") or []) if isinstance(x, str)],
              "reopen_conditions": [str(x)[:300] for x in (j.get("reopen_conditions") or [])[:5]], "judge_model": JUDGE_MODEL}
    record(cid, "judge.ruling", "judge", ruling)
    return ruling

def transcript_text(c, events_so_far):
    struck = {e["data"]["claim"] for e in events_so_far if e["type"] == "objection" and e["data"].get("ruling") == "sustained"}
    lines = []
    for e in events_so_far:
        d = e["data"]
        if e["type"] == "argument":
            lines.append(f"{d['kind'].upper()} (round {d['round']}), {e['actor']} for {d['position']}: {d.get('summary', '')}")
            lines += [f"  [{cl['id']}]{' STRUCK' if cl['id'] in struck else ''} {cl['text']} (cites {', '.join(cl['cites']) or 'nothing'})" for cl in d.get("claims", [])]
        elif e["type"] == "objection": lines.append(f"  OBJECTION by {e['actor']} to [{d['claim']}] ({d['ground']}): {d['ruling'].upper()}. {d.get('reason') or ''}")
        elif e["type"] == "question": lines.append(f"  THE BENCH asks {d['to']}: {d['question']}\n  ANSWER: {d['answer']}")
    return "\n".join(lines)

def run(cid):
    c = load(cid); c["status"] = "in discovery"; save(cid, c)
    if not c.get("positions_framed"):
        record(cid, "positions.framed", c.get("framed_by", "lawyer"), {"positions": c["positions"]}); c["positions_framed"] = True
    discovery(cid, c); save(cid, c)
    # advocates: assigned, one per position, each on its own family; the Judge on a family no advocate uses
    c["advocates"] = [{"position_id": p["id"], "position": f"{p['id']}: {p['text']}", "agent": ADVOCATE_OFFICES[i], "model": ADVOCATE_MODELS[i], "family": MODELS[ADVOCATE_MODELS[i]]}
                      for i, p in enumerate(c["positions"])]
    c["judge"] = {"agent": "judge", "model": JUDGE_MODEL, "family": MODELS[JUDGE_MODEL]}
    c["jury"] = [{"agent": a, "model": m, "family": MODELS[m]} for a, m in zip([j for j in JURY_OFFICES if j not in {x["agent"] for x in c["advocates"]}], JURY_MODELS)]
    fams = [a["family"] for a in c["advocates"]]
    assert len(set(fams)) == len(fams) and c["judge"]["family"] not in fams, "model families must be separated (spec 6.7)"
    record(cid, "advocates.assigned", "system", {"advocates": c["advocates"], "judge": c["judge"], "jury": c["jury"], "provisional": provisional()})
    c["status"] = "in session"; save(cid, c)
    evs = lambda: C.case_events(cid)
    prior = argument_round(cid, c, 1, "opening", [])
    objections(cid, c, prior)
    for rnd in (2, 3):
        if over_budget(c): break
        prior = argument_round(cid, c, rnd, "rebuttal", prior); save(cid, c)
        objections(cid, c, prior)
    if not over_budget(c): bench_questions(cid, c, transcript_text(c, evs()))
    prior = argument_round(cid, c, 4, "closing", prior); objections(cid, c, prior); save(cid, c)
    tx = transcript_text(c, evs())
    ballots, tallies = jury(cid, c, tx); c["ballots"], c["tallies"] = ballots, tallies
    ruling = rule(cid, c, tx, tallies)
    cert = C.compute(evs())
    final = ruling["holding"]
    if final != "insufficient" and cert["score"] < C.CFG["insufficient_below"]: final = "insufficient"      # the rule: below 40 is insufficient evidence
    c.update(status="ruled", ruling={**ruling, "final_holding": final}, certainty=cert, ruled_at=now()); save(cid, c)
    record(cid, "case.ruled", "judge", {"holding": final, "judge_holding": ruling["holding"], "certainty": cert["score"], "band": cert["band"], "breakdown": cert,
                                        "reopen_conditions": ruling["reopen_conditions"], "spent_tokens": c.get("spent_tokens"), "provisional": provisional()})
    write_records(cid, c, tx)
    return c

def write_records(cid, c, tx):
    d = case_dir(cid, c.get("private")); r = c["ruling"]; cert = c["certainty"]
    pos = {p["id"]: p["text"] for p in c["positions"]}
    held = "Insufficient evidence" if r["final_holding"] == "insufficient" else f"{r['final_holding']}: {pos[r['final_holding']].rstrip('.')}"
    (d / "transcript.md").write_text(f"# {cid} · transcript\n\n**Question:** {c['question']}\n\n```\n{tx}\n```\n")
    reasoning = "\n".join(f"- {p.get('point', '')} ({', '.join(p.get('cites') or []) or 'no citation'})" for p in r["reasoning"])
    (d / "ruling.md").write_text(f"""# {cid} · ruling{' (provisional court)' if provisional() else ''}

**Question:** {c['question']}

**Holding:** {held}. {r['holding_text']}

**Certainty:** {cert['score']} ({cert['band']}). Evidence strength {cert['inputs']['evidence_strength']}, cross-family agreement {cert['inputs']['cross_family_agreement']}, argument survival {cert['inputs']['argument_survival']}, jury margin {cert['inputs']['jury_margin']}, the Judge's confidence {cert['inputs']['judge_confidence']} (weight 0.10); capped at {cert['cap']}. Recompute: `python3 court/certainty.py {cid}`.
{"" if r["final_holding"] == r["holding"] else f"""
The Judge held {r['holding']}, but certainty fell below {C.CFG['insufficient_below']}, so the Court's rule makes the holding "insufficient evidence".
"""}
## Reasoning

{reasoning}

## Dissent

{r['dissent'] or 'None.'}

## Jury

{chr(10).join(f"- {b['juror']} ({b['family']}): {b['vote']}. {b['reason']}" for b in c.get('ballots', [])) or json.dumps(c.get('tallies', {}))}

## Reopen conditions

{chr(10).join('- ' + x for x in r['reopen_conditions']) or '- None stated.'}

## Parties

Seats, not offices: each seat is a model given that office's instructions for this case; its turns are the Court's, not the office's.

- Advocates: {', '.join(f"{a['agent']} for {a['position_id']} ({a['model']})" for a in c['advocates'])}
- Judge: {c['judge']['model']} ({c['judge']['family']})
- Jury: {', '.join(f"{j['agent']} ({j['model']})" for j in c['jury'])}
- Tokens: {c.get('spent_tokens')} of {c.get('budget_tokens')}
""")
    file_case_law(cid, c, held)

def headnote(text, n=230):
    text = " ".join(text.split()).rstrip(".")
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"

def file_case_law(cid, c, held):
    """The ruling as an officer case (Article 13.1) while the Court is provisional; its number must be this case's."""
    if c.get("case_law") or c.get("case_law_draft") or c.get("test"): return              # test cases (CT-) are never precedent
    r = c["ruling"]; cert = c["certainty"]
    draft = f"""---
id: (assigned)
title: {c['question'][:110]}
date: {datetime.date.today().isoformat()}
court: officer
labels: [research, governance]
headnote: {headnote(("Insufficient evidence: " if r['final_holding'] == 'insufficient' else '') + (r['holding_text'] or held))} Certainty {cert['score']} ({cert['band']}).
source: cases/{cid}/ruling.md (the Court, P-006{', provisional: filed as an officer case under Article 13.1' if provisional() else ''})
cites: []
review_by: {(datetime.date.today() + datetime.timedelta(days=90)).isoformat()}
---

## Question

{c['question']}

## Facts

The Court heard the case with {sum(1 for x in c['exhibits'] if x.get('admitted'))} admitted exhibits (cases/{cid}/exhibits/exhibits.json), advocates on {', '.join(a['family'] for a in c['advocates'])}, a Judge on {c['judge']['family']}, and a jury of {len(c['jury'])} on {', '.join(j['family'] for j in c['jury'])}. The full transcript is cases/{cid}/transcript.md; every phase is in the Record.

## Holding

{held}. {r['holding_text']}

## Reasoning

{chr(10).join(f"- {p.get('point', '')} ({', '.join(p.get('cites') or []) or 'no citation'})" for p in r['reasoning'])}

Certainty {cert['score']} ({cert['band']}), computed by court/certainty.py from the Record.

## Dissent

{r['dissent'] or 'None.'}

## Scope

This question as asked, on the evidence admitted. Reopen conditions: {'; '.join(r['reopen_conditions']) or 'none stated'}.

## History

- {datetime.date.today().isoformat()}: filed from the Court's ruling in {cid}.
"""
    # the Scribe is the Reporter (Article 13.1, C-0005): the Court writes the draft, and asks the Scribe to file it within 24 hours
    d = case_dir(cid, c.get("private")); (d / "case-law-draft.md").write_text(draft)
    c["case_law_draft"] = str((d / "case-law-draft.md").relative_to(ROOT)); save(cid, c)
    ts = now().replace("+00:00", "Z")
    (ROOT / "org/board" / f"{datetime.date.today().isoformat()}-ruling-{cid.lower()}.md").write_text(
        f"#ruling\n### system · {ts}\n{cid} is ruled; @scribe please file its case-law entry from {c['case_law_draft']} within 24 hours (Article 13.1).\n\n"
        f"Holding: {held}. Certainty {cert['score']} ({cert['band']}).\n")
    record(cid, "case_law.drafted", "system", {"draft": c["case_law_draft"]})

# ---------- filing ----------
def file_case(question, positions=None, links=None, priority="normal", budget=150000, filer="steward", private=False, no_discovery=False, test=False):
    question = " ".join(question.split())
    if not (10 <= len(question) <= 500): raise SystemExit("REFUSED: a question is 10 to 500 characters")
    cid = next_case_id(test)
    ps = [{"id": chr(65 + i), "text": re.sub(r"^[A-D][:.)]\s*", "", p.strip())[:300]} for i, p in enumerate(positions or []) if p.strip()][:4]
    framed_by = filer
    if len(ps) < 2:
        c0 = {"spent_tokens": 0}
        out = turns([{"id": "frame", "model": ADVOCATE_MODELS[0], "system": (ROOT / "agents/lawyer/ROLE.md").read_text() + "\n\nYou are framing positions for the Court.",
                      "prompt": f"QUESTION: {question}\n\nFrame 2 to 4 mutually exclusive positions a court could hold (Yes/No is fine when the question is binary). "
                                'Reply with only JSON: {"positions": ["...", "..."]}'}], c0)["frame"]
        ps = [{"id": chr(65 + i), "text": str(p)[:300]} for i, p in enumerate((as_json(out["text"]).get("positions") or ["Yes", "No"])[:4])]
        framed_by = "lawyer"
    c = {"id": cid, "question": question, "positions": ps, "links": [l for l in (links or []) if l][:10], "priority": priority, "budget_tokens": int(budget),
         "filer": filer, "private": private, "no_discovery": no_discovery, "test": test, "status": "filed", "filed_at": now(), "framed_by": framed_by, "spent_tokens": 0}
    save(cid, c)
    record(cid, "case.filed", filer, {"question": question, "positions": ps, "links": c["links"], "priority": priority, "budget_tokens": c["budget_tokens"],
                                      "private": private, "provisional": provisional()})
    return cid

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["file", "run", "show", "families"]); ap.add_argument("case", nargs="?")
    ap.add_argument("--question"); ap.add_argument("--position", action="append"); ap.add_argument("--link", action="append")
    ap.add_argument("--priority", default="normal"); ap.add_argument("--budget", type=int, default=150000); ap.add_argument("--filer", default="steward")
    ap.add_argument("--private", action="store_true"); ap.add_argument("--no-discovery", action="store_true"); ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.cmd == "families": print(json.dumps(MODELS, indent=1)); return
    if a.cmd == "file": print(file_case(a.question or "", a.position, a.link, a.priority, a.budget, a.filer, a.private, a.no_discovery, a.test)); return
    if a.cmd == "show": print(json.dumps(load(a.case), indent=1)); return
    try: c = run(a.case)
    except Exception as e:
        c = load(a.case); c["status"] = "error"; c["error"] = f"{type(e).__name__}: {str(e)[:300]}"; save(a.case, c)
        record(a.case, "case.error", "system", {"error": c["error"]}); raise
    print(f"{a.case}: {c['ruling']['final_holding']} · certainty {c['certainty']['score']} ({c['certainty']['band']})")

if __name__ == "__main__":
    main()
