#!/usr/bin/env python3
"""Read back from Weave for the dashboard (P-005). Prints one JSON object; never prints the key.

  agents/.venv/bin/python agents/observability/weave_query.py recent [--agent KEY] [--limit 25]
  agents/.venv/bin/python agents/observability/weave_query.py agents
  agents/.venv/bin/python agents/observability/weave_query.py evals

The dashboard server runs this (it has no weave of its own), caches the answer for 30 seconds, and falls back
to deep links with "live": false when it fails.
"""
import argparse, json, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENTITY, PROJECT = os.environ.get("WEAVE_ENTITY", "rexstjohn-verafy"), os.environ.get("WEAVE_PROJECT_NAME", "The Collective")
BASE = f"https://wandb.ai/{ENTITY}/{PROJECT.replace(' ', '%20')}/weave"

def key():
    if not os.environ.get("WANDB_API_KEY"):
        try:
            m = re.search(r"^WANDB_API_KEY=(.+)$", (ROOT / "agents/.env").read_text(), re.M)
            if m: os.environ["WANDB_API_KEY"] = m.group(1).strip().strip("'\"")
        except OSError: pass
    return bool(os.environ.get("WANDB_API_KEY"))

def client():
    os.environ.setdefault("WEAVE_PRINT_CALL_LINK", "false"); os.environ.setdefault("WEAVE_IMPLICITLY_PATCH_INTEGRATIONS", "false")
    import contextlib, io, weave
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return weave.init(f"{ENTITY}/{PROJECT}")

def iso(t): return t.isoformat() if t else None

def recent(agent, limit):
    from weave.trace_server.agents import types as T
    c = client(); pid = f"{c.entity}/{c.project}"
    ands = [{"$eq": [{"$getField": "operation_name"}, {"$literal": "invoke_agent"}]}]
    if agent: ands.append({"$eq": [{"$getField": "agent_name"}, {"$literal": agent}]})
    ands.append({"$not": [{"$contains": {"input": {"$getField": "conversation_id"}, "substr": {"$literal": "roster-"}}}]})   # runs, not registrations
    q = {"$expr": {"$and": ands}}
    r = c.server.agent_spans_query(T.AgentSpansQueryReq(project_id=pid, query=q, limit=min(limit * 4, 400),
                                                         sort_by=[T.AgentSortBy(field="started_at", direction="desc")]))
    out = []
    for s in r.spans:
        if str(getattr(s, "conversation_id", "") or "").startswith("roster-"): continue      # registrations, not runs (E-0113)
        if len(out) >= limit: break
        dur = (s.ended_at - s.started_at).total_seconds() if s.started_at and s.ended_at else None
        out.append({"op": s.span_name, "agent": s.agent_name, "started": iso(s.started_at), "duration_s": round(dur, 1) if dur is not None else None,
                    "status": s.status_code, "input_tokens": s.input_tokens, "output_tokens": s.output_tokens, "model": s.request_model,
                    "trace_id": s.trace_id, "url": f"{BASE}/agents"})
    return {"live": True, "runs": out, "total": r.total_count}

def agents():
    from weave.trace_server.agents import types as T
    c = client(); pid = f"{c.entity}/{c.project}"
    r = c.server.agent_agents_query(T.AgentsQueryReq(project_id=pid, limit=200))
    return {"live": True, "agents": [{"agent": a.agent_name, "runs": a.invocation_count, "spans": a.span_count, "input_tokens": a.total_input_tokens,
                                      "output_tokens": a.total_output_tokens, "errors": a.error_count, "last": iso(a.last_seen),
                                      "url": f"{BASE}/agents"} for a in r.agents]}

def evals():
    """The latest result of each registered eval, from the local results the suite writes (evals/results/)."""
    res = {}
    for p in sorted((ROOT / "evals/results").glob("E*.json")):
        try: d = json.loads(p.read_text())
        except ValueError: continue
        res[d["id"]] = d
    return {"live": True, "evals": [res[k] for k in sorted(res, key=lambda x: int(x[1:]))], "url": f"{BASE}/evaluations"}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["recent", "agents", "evals"])
    ap.add_argument("--agent", default=""); ap.add_argument("--limit", type=int, default=25)
    a = ap.parse_args()
    if a.cmd == "evals": print(json.dumps(evals())); return
    if not key(): print(json.dumps({"live": False, "error": "WANDB_API_KEY isn't set"})); return
    try:
        out = recent(re.sub(r"[^a-z0-9]", "", a.agent)[:16], max(1, min(a.limit, 100))) if a.cmd == "recent" else agents()
    except Exception as e:
        out = {"live": False, "error": f"{type(e).__name__}: {str(e)[:160]}"}
    print(json.dumps(out, default=str))

if __name__ == "__main__":
    main()
