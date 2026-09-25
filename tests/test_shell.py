"""The web terminal (Charter Article 18.7(c)(iii); dashboard/shell_bridge.py). Standard library only, no browser.
Run: python3 tests/test_shell.py   (scratch copy; starts the dashboard on free ports)"""
import atexit, base64, hashlib, json, os, pathlib, shutil, signal, socket, struct, subprocess, sys, tempfile, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
atexit.register(shutil.rmtree, t.parent, True)
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs", "__pycache__", ".env", "secrets", "*.key"))
subprocess.run([sys.executable, "agents/bin/eventlog.py", "init", "--actor", "steward"], cwd=t, capture_output=True)
home = t.parent / "home"; home.mkdir()
env = {**os.environ, "SHELL": "/bin/bash", "HOME": str(home), "COLLECTIVE_SHELL_TOKEN_SECS": "2", "BASH_SILENCE_DEPRECATION_WARNING": "1"}
def port():
    with socket.socket() as s: s.bind(("127.0.0.1", 0)); return s.getsockname()[1]
P, PP = port(), port()
srv = subprocess.Popen([sys.executable, "dashboard/server.py", "--port", str(P)], cwd=t, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pub = subprocess.Popen([sys.executable, "dashboard/server.py", "--port", str(PP), "--public"], cwd=t, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
atexit.register(lambda: [p.terminate() for p in (srv, pub)])
ORIGIN = f"http://127.0.0.1:{P}"
def token(p=P):
    with urllib.request.urlopen(f"http://127.0.0.1:{p}/api/shell/token", timeout=10) as r: return json.loads(r.read())["token"]
for _ in range(60):
    try: token(); break
    except Exception: time.sleep(0.2)

class WS:
    def __init__(self, tok, cmd="shell", origin=ORIGIN, host=None, p=P, cols=80, rows=24):
        self.s = socket.create_connection(("127.0.0.1", p), timeout=10); key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /ws/shell?cmd={cmd}&token={tok}&cols={cols}&rows={rows} HTTP/1.1\r\nHost: {host or f'127.0.0.1:{p}'}\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
               + (f"Origin: {origin}\r\n" if origin else "") + "\r\n")
        self.s.sendall(req.encode()); head = b""
        while b"\r\n\r\n" not in head:
            c = self.s.recv(1)
            if not c: break
            head += c
        self.status = int(head.split(b" ")[1]) if head else 0; self.buf = b""; self.out = b""
        if self.status == 101:
            want = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
            assert f"Sec-WebSocket-Accept: {want}".encode() in head, head
    def send(self, data, op=2):
        data = data.encode() if isinstance(data, str) else data; m = os.urandom(4)
        n = len(data); hdr = bytes([0x80 | op]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack("!H", n))
        self.s.sendall(hdr + m + bytes(b ^ m[i % 4] for i, b in enumerate(data)))
    def until(self, needle, secs=10):
        end = time.time() + secs; self.s.settimeout(0.5)
        while needle.encode() not in self.out and time.time() < end:
            try: c = self.s.recv(65536)
            except socket.timeout: continue
            if not c: break
            self.buf += c
            while len(self.buf) >= 2:
                n, i = self.buf[1] & 0x7F, 2
                if n == 126: n, i = struct.unpack("!H", self.buf[2:4])[0], 4
                elif n == 127: n, i = struct.unpack("!Q", self.buf[2:10])[0], 10
                if len(self.buf) < i + n: break
                if self.buf[0] & 0x0F == 2: self.out += self.buf[i:i + n]
                self.buf = self.buf[i + n:]
        return needle.encode() in self.out
    def close(self):
        try: self.send(struct.pack("!H", 1000), op=8)
        except OSError: pass
        self.s.close()

def events():
    return [json.loads(l) for l in (t / "private/ledger/events.ndjson").read_text().splitlines() if l.strip()]

try:
    # handshake, echo round trip, resize, Ctrl-C
    w = WS(token()); assert w.status == 101, w.status
    w.send("echo hello-collective-$((6*7))\r"); assert w.until("hello-collective-42"), w.out[-300:]
    w.send(json.dumps({"type": "resize", "cols": 101, "rows": 41}), op=1); time.sleep(0.3)
    w.send("stty size\r"); assert w.until("41 101"), w.out[-300:]
    w.send("sleep 30\r"); time.sleep(0.8); w.send("\x03"); w.send("echo after-ctrl-c\r")
    assert w.until("after-ctrl-c", 6), "Ctrl-C must interrupt sleep 30"
    # a password prompt is never recorded; a key is redacted
    w.send("read -s pw; echo got-it\r"); time.sleep(0.5); w.send("hunter2-not-recorded\r"); assert w.until("got-it"), w.out[-200:]
    key = "xai-" + "Q" * 40
    w.send(f"echo {key} && echo done-key\r"); assert w.until("done-key")
    pid = next(e for e in reversed(events()) if e["type"] == "shell.start")["data"]["pid"]
    w.close(); time.sleep(3)
    left = subprocess.run(["ps", "-A", "-o", "pid=,pgid=,stat=,comm="], capture_output=True, text=True).stdout
    group = [l for l in left.splitlines() if l.split()[1:2] == [str(pid)]]
    assert not group, f"the process group must be gone after disconnect: {group}"
    ev = events()
    lines = [e["data"]["line"] for e in ev if e["type"] == "shell.input"]
    assert any("echo hello-collective" in l for l in lines), lines
    assert not any("hunter2" in l for l in lines), "a line typed with echo off must never be recorded"
    assert not any(key in l for l in lines) and any("[redacted: secret]" in l for l in lines), lines
    end = next(e for e in reversed(ev) if e["type"] == "shell.end")
    assert end["data"]["hidden_lines"] >= 1 and end["data"].get("blob"), end
    import gzip
    raw = (t / "private/ledger/blobs" / end["data"]["blob"][:2] / end["data"]["blob"][2:]).read_bytes()
    blob = (gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw).decode("utf-8", "replace")
    assert "hello-collective-42" in blob and key not in blob and "hunter2" not in blob, "output blob: recorded and redacted"
    # refusals
    assert WS(token(), origin=None).status == 403, "no Origin"
    assert WS(token(), origin="http://evil.example").status == 403, "foreign Origin"
    assert WS(token(), host="evil.example").status == 403, "bad Host"
    tok = token(); a = WS(tok); assert a.status == 101; a.close(); assert WS(tok).status == 403, "a token works once"
    old = token(); time.sleep(2.5); assert WS(old).status == 403, "an expired token"
    assert WS(token(), cmd="python3").status == 400, "only shell and herdr"
    try: urllib.request.urlopen(f"http://127.0.0.1:{PP}/api/shell/token", timeout=10); raise AssertionError("public view gives no token")
    except urllib.error.HTTPError as e: assert e.code == 403
    assert WS("x", p=PP, origin=f"http://127.0.0.1:{PP}").status == 403, "public view"
    # talking to an agent in the drawer (E-0092): refused until the Charter names it, then only for active agents
    assert WS(token(), cmd="agent&agent=scribe").status == 403, "agent talk waits for A-0030"
    ch = t / "CHARTER.md"; ch.write_text(ch.read_text() + "\n<!-- test: the web terminal drawer -->\n")
    rr = t / "agents/bin/run-role.sh"; rr.write_text('#!/bin/bash\necho "talking-to-$1 $2"\nsleep 5\n'); rr.chmod(0o755)   # a stand-in: no model is called
    assert WS(token(), cmd="agent&agent=nobody").status == 400, "unknown agent"
    assert WS(token(), cmd="agent&agent=../x").status == 400, "not a key"
    a = WS(token(), cmd="agent&agent=scribe"); assert a.status == 101; assert a.until("talking-to-scribe --interactive"), "runs run-role.sh KEY --interactive"; a.close()
    time.sleep(1.5); assert any(e["type"] == "shell.start" and e["data"].get("agent") == "scribe" for e in events()), "recorded with the agent"
    four = [WS(token()) for _ in range(4)]; assert all(x.status == 101 for x in four)
    assert WS(token()).status == 429, "at most four shells"
    for x in four: x.close()
    print("shell tests passed")
finally:
    for p in (srv, pub): p.terminate()
