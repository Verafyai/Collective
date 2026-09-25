"""One redaction function for everything the Collective exports (P-005; Charter Articles 12.3, 12.10).

    from redact import redact
    redact("text")            -> text with secrets, emails, and phone numbers replaced
    redact({"a": [..]})       -> the same, applied to every string inside

It applies, in order: the event log's own secret patterns (Article 12.3), the web terminal's extra ones
(xai-, wandb_v1_, key=value), every rule in the gitleaks 8.30.1 config
(gitleaks-rules.toml, MIT; fetched by bootstrap and pinned by SHA-256, not committed), email addresses, and phone numbers. Standard library only. Anything it can't
parse is replaced whole, so a failure never lets text through.
"""
import pathlib, re, sys, tomllib, warnings

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bin"))
from eventlog import SECRET_RE                                   # Article 12.3's patterns

MARK = "[redacted]"
EXTRA_RE = re.compile(r"(?<![A-Za-z0-9])(?:xai-[A-Za-z0-9]{20,}|wandb_v1_[A-Za-z0-9_]{20,})"
                      r"|(?i:(?:api[_-]?key|secret|token|password|passwd|authorization)\s*[:=]\s*\S{6,})")
EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w-])")
PHONE_RE = re.compile(r"(?<![\w+])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}(?!\w)")

def _go_to_py(rx):
    """gitleaks writes Go regexps; Python needs a mid-pattern (?i) as a scoped group."""
    flags = 0
    if rx.startswith("(?i)"): rx, flags = rx[4:], re.I
    k = rx.find("(?i)")
    while k != -1:
        rx = rx[:k] + "(?i:" + rx[k + 4:] + ")"; k = rx.find("(?i)")
    return re.compile(rx, flags)

def _gitleaks():
    rules = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for r in tomllib.loads((HERE / "gitleaks-rules.toml").read_text()).get("rules", []):
            if not r.get("regex"): continue
            try: rules.append((r["id"], _go_to_py(r["regex"]), r.get("secretGroup", 0)))
            except re.error: pass
    return rules
GITLEAKS = _gitleaks()

def _gitleaks_sub(text):
    for _, rx, group in GITLEAKS:
        def repl(m, g=group):
            try:
                if g and m.group(g): return m.group(0).replace(m.group(g), MARK)
            except IndexError: pass
            return MARK
        text = rx.sub(repl, text)
    return text

def redact(v):
    """Redact every string in v (str, dict, list, tuple); other values pass through unchanged."""
    if isinstance(v, str):
        try:
            t = EXTRA_RE.sub(MARK, SECRET_RE.sub(MARK, v))
            t = _gitleaks_sub(t)
            return PHONE_RE.sub(MARK, EMAIL_RE.sub(MARK, t))
        except Exception:
            return MARK                                          # never let unscanned text through
    if isinstance(v, dict): return {k: redact(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [redact(x) for x in v]
    return v
