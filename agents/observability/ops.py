"""@op: the Collective's own machinery as Weave ops (P-005, layer 3B; Charter Article 12.10).

    from ops import run_cli      # at a script's entry point: run_cli(main, "edict") -> ops edict.new, edict.note, ...
    from ops import op           # or on a function:   @op("sprint.count_votes", keep=("sprint",))

The decorated function always runs exactly as before. An op costs one local file append and no network:
its name, times, privacy-shaped inputs and output (or exception) go to the spool
agents/observability/.ops_spool.ndjson (git-ignored), and the bridge (otel_bridge.py follow, its own
process) sends them to Weave as ops with their real times. If the spool can't be written, the op is skipped
after one warning. OBS_OPS=0 or OBS_PRIVATE_MODE=off turns ops off.

What an op records (E-0108, OBS_PRIVATE_MODE): in "metadata" mode only the arguments named in keep=, plus
each other argument's type and length, and the result's type and length (or itself if it's a number or a
bool); in "full" mode the redacted values. Everything passes through redact.py.
"""
import datetime, fcntl, functools, json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPOOL = HERE / ".ops_spool.ndjson"
sys.path.insert(0, str(HERE))
_state = {"warned": False}

def _warn(msg):
    if not _state["warned"]:
        _state["warned"] = True
        print(f"note: Weave ops off ({msg}); continuing without tracing", file=sys.stderr)

def _mode():
    if not os.environ.get("OBS_PRIVATE_MODE"):
        try:
            for line in (ROOT / "agents/.env").read_text().splitlines():
                if line.startswith("OBS_PRIVATE_MODE="): os.environ["OBS_PRIVATE_MODE"] = line.split("=", 1)[1].strip().strip("'\"")
        except OSError: pass
    return os.environ.get("OBS_PRIVATE_MODE", "metadata")

def _now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _spool(rec):
    try:
        with open(SPOOL, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX); f.write(json.dumps(rec, default=str) + "\n")
    except Exception as e: _warn(f"spool: {str(e)[:80]}")

def _shape(v):
    if isinstance(v, (bool, int, float)) or v is None: return v
    try: return {"type": type(v).__name__, "len": len(v)}
    except TypeError: return {"type": type(v).__name__}

def _inputs(fn, args, kwargs, keep):
    from redact import redact
    import inspect
    try: bound = inspect.signature(fn).bind_partial(*args, **kwargs).arguments
    except (TypeError, ValueError): bound = {f"arg{i}": a for i, a in enumerate(args)} | kwargs
    if _mode() == "full": return redact({k: repr(v)[:2000] if not isinstance(v, (str, int, float, bool)) else v for k, v in bound.items()})
    out = {}
    for k, v in bound.items():
        if k in keep and isinstance(v, (str, int, float, bool)) or v is None: out[k] = v
        elif k in keep and hasattr(v, "__dict__"):                        # an argparse namespace: its kept fields
            out[k] = {kk: vv for kk, vv in vars(v).items() if kk in keep and isinstance(vv, (str, int, float, bool))}
        else: out[k] = _shape(v)
    return redact(out)

def op(name, keep=()):
    """Record fn as the Weave op `name` (best effort). keep: argument names safe to send in metadata mode."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if os.environ.get("OBS_OPS", "1") == "0" or _mode() == "off": return fn(*args, **kwargs)
            try: rec = {"op": name, "started_at": _now(), "inputs": _inputs(fn, args, kwargs, keep), "pid": os.getpid()}
            except Exception as e: _warn(str(e)[:80]); return fn(*args, **kwargs)
            try:
                result = fn(*args, **kwargs)
            except BaseException as ex:
                code = getattr(ex, "code", None)
                rec.update(ended_at=_now(), exception=f"{type(ex).__name__}" + (f" (exit {code})" if code not in (None, 0) else ""),
                           ok=isinstance(ex, SystemExit) and code in (None, 0))
                _spool(rec); raise
            try:
                from redact import redact
                rec.update(ended_at=_now(), ok=True, output=redact(repr(result)[:2000]) if _mode() == "full" else _shape(result))
            except Exception: rec.update(ended_at=_now(), ok=True)
            _spool(rec)
            return result
        return wrapper
    return deco

import re as _re
_ID = _re.compile(r"^(?:[A-Z]{1,2}-\d{3,4}|[a-z][a-z0-9]{1,15}|\d{1,6}|v?\d+\.\d+\.\d+|[a-z]+[-_][a-z0-9_-]{1,30})$")

def run_cli(main, name, only=None, rename=None, keep_flags=()):
    """Run a script's main() as the op `<name>.<subcommand>` (or rename[subcommand]). Only subcommands in `only`
    are traced (None: all). In metadata mode the op records the subcommand, id-like positional arguments
    (E-0107, A-0045, pm, 12), and the values of keep_flags; never free text."""
    argv = sys.argv[1:]
    sub = argv[0] if argv and not argv[0].startswith("-") else ""
    if only is not None and sub not in only: return main()
    opname = (rename or {}).get(sub) or (f"{name}.{sub}" if sub else name)
    ids = [x for i, x in enumerate(argv[1:], 1) if not x.startswith("-") and _ID.match(x)
           and not (argv[i - 1].startswith("-") and argv[i - 1] not in keep_flags and i - 1 > 0)]   # a flag's value is text, not an id
    flags = {}
    for i, x in enumerate(argv):
        if x in keep_flags and i + 1 < len(argv): flags[x.lstrip("-")] = argv[i + 1]
    @op(opname, keep=("command", "ids", "flags"))
    def traced(command, ids, flags): return main()
    return traced(sub, " ".join(ids), " ".join(f"{k}={v}" for k, v in flags.items()))
