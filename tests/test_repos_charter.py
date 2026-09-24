"""Tests for the two-repo split (Article 17) and Charter rewind (Article 16).
Run: python3 tests/test_repos_charter.py   (works on a scratch copy, offline)"""
import pathlib, shutil, subprocess, sys, tempfile, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs"))
def sh(*cmd, ok=True, cwd=t):
    r = subprocess.run(list(cmd), capture_output=True, text=True, cwd=cwd)
    if ok: assert r.returncode == 0, (cmd, r.stdout, r.stderr)
    return r.stdout + r.stderr
for d in (t, t / "private"):
    if (d / ".git").exists(): shutil.rmtree(d / ".git")
sh("git", "config", "--global", "user.email", "rex@example.com"); sh("git", "config", "--global", "user.name", "Rex St. John")
# 1. two repos, private ignored by public
out = sh("agents/bin/repos.sh", "init", "--offline")
assert "Verafyai/Collective.git" in out and "Verafyai/CollectivePrivate.git" in out, out
sh("agents/bin/repos.sh", "commit", "Initial")
pub = sh("git", "ls-files"); priv = sh("git", "-C", "private", "ls-files")
assert "CHARTER.md" in pub and "private/" not in pub, "public repo must not contain private/"
assert "edicts/E-0001" in priv and "CHARTER.md" not in priv
# 2. a secret in a public file blocks the public commit and records an incident privately
fake_key = "sk-" + "ant-api03-" + "ABCD" * 8          # assembled at runtime so no key-shaped text lives in the repo
(t / "prototypes" / "leak.txt").write_text("ANTHROPIC_API_KEY=" + fake_key + "\n")
r = sh("agents/bin/repos.sh", "commit", "leaky", ok=False)
assert "REFUSED" in r and list((t / "private" / "incidents").glob("*public-commit-blocked.md")), r
assert "leak.txt" not in sh("git", "ls-files")
(t / "prototypes" / "leak.txt").unlink()
# 3. edicts commit into the private repo
sh(sys.executable, "agents/bin/edict.py", "new", "--title", "Test", "--text", "Do the thing.")
assert "Edict E-" in sh("git", "-C", "private", "log", "--oneline", "-1")
# 4. charter rewind: refused without STOP; then back to v3.2.0 structure and forward again
cur = re.search(r"Charter version: ([\d.]+)", (t / "CHARTER.md").read_text()).group(1)
assert "REFUSED" in sh(sys.executable, "agents/bin/charter.py", "rewind", "v3.2.0", "--i-am-steward", ok=False)
(t / "org" / "STOP").touch()
sh(sys.executable, "agents/bin/charter.py", "rewind", "v3.2.0", "--i-am-steward")
now = (t / "CHARTER.md").read_text()
old = (t / "charter/history/CHARTER-v3.2.0.md").read_text()
new_v = re.search(r"Charter version: ([\d.]+)", now).group(1)
assert now.split("\n---\n\n# PART VI")[0].replace(f"Charter version: {new_v}", "Charter version: 3.2.0") == old.split("\n---\n\n# PART VI")[0]
assert "Reversion to v3.2.0" in now and "### A-0000" in now, "log continues, never rewound"
sh(sys.executable, "agents/bin/charter.py", "rewind", f"v{cur}", "--i-am-steward")
back = (t / "CHARTER.md").read_text()
assert "## Article 17" in back and "Reversion to v" + cur in back
v = sh(sys.executable, "agents/bin/charter-verify.py"); assert "FAIL" not in v, v
tl = sh(sys.executable, "agents/bin/charter.py", "timeline"); assert "Reversion to v3.2.0" in tl
assert "@@" in sh(sys.executable, "agents/bin/charter.py", "diff", "v3.2.0", f"v{cur}")
print("repos and charter tests passed")
