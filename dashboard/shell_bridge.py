"""A real terminal in the browser (Charter Article 18.7(c)(iii); P-001): a pseudo-terminal on the
Steward's machine streamed to xterm.js over a WebSocket. Python standard library only.

Three commands, and nothing else: `shell` ($SHELL -l, falling back to /bin/bash), `herdr` (the full
herdr UI), and `agent` (agents/bin/run-role.sh <key> --interactive: a recorded talk with one active agent,
Article 18.8; available once amendment A-0030 is ratified). Refused unless ALL hold: private view; Host is 127.0.0.1:<port> or localhost:<port>; an
Origin header equal to the dashboard's own origin (WebSockets skip same-origin rules); and a one-time
token from GET /api/shell/token, valid for 30 seconds. At most 4 shells at once; each process group is
killed on disconnect or after 30 minutes idle.

Recorded (Article 12), actor steward: shell.start (cmd, pid, cols, rows); every finished typed line as
shell.input (on Enter, Ctrl-C, or 3 s idle), except lines typed while the terminal's echo is off (a
password prompt), which are counted, never recorded; and shell.end (duration, bytes) with the session's
output as a blob, capped at 5 MB. Lines and output are redacted before they are stored.
"""
import base64, fcntl, hashlib, json, os, pathlib, re, secrets, select, signal, socket, struct, subprocess, sys
import tempfile, termios, threading, time, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_SHELLS, IDLE_SECS, LINE_IDLE, OUT_CAP = 4, 30 * 60, 3.0, 5 * 1024 * 1024
TOKEN_SECS = min(30, int(os.environ.get("COLLECTIVE_SHELL_TOKEN_SECS", "30")))   # tests may shorten it; never longer than 30 s
TOKENS, TLOCK = {}, threading.Lock()
LIVE = {}                                    # pid -> session, for the 4-shell limit
sys.path.insert(0, str(ROOT / "agents" / "bin"))
from eventlog import SECRET_RE               # the event log's own redaction (Article 12.3)
EXTRA_RE = re.compile(r"(?<![A-Za-z0-9])xai-[A-Za-z0-9]{20,}|(?i:(?:api[_-]?key|secret|token|password|passwd)\s*[:=]\s*\S{6,})")

def redact(text):
    text = SECRET_RE.sub("[redacted: secret]", text)
    return EXTRA_RE.sub("[redacted: secret]", text)

def record(etype, data, blob=None):
    args = [sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", "steward", "--type", etype, "--data", json.dumps(data)]
    if blob is not None: args += ["--blob-file", blob]
    subprocess.run(args, capture_output=True, cwd=ROOT)

# ---------- tokens ----------
def new_token():
    t = secrets.token_urlsafe(24)
    with TLOCK:
        now = time.time()
        for k in [k for k, v in TOKENS.items() if v < now]: del TOKENS[k]
        TOKENS[t] = now + TOKEN_SECS
    return t

def take_token(t):
    with TLOCK:
        exp = TOKENS.pop(t or "", None)     # one-time: taken whether or not it's still valid
    return exp is not None and exp >= time.time()

# ---------- WebSocket (RFC 6455) ----------
def send_frame(sock, opcode, payload=b""):
    head = bytes([0x80 | opcode]); n = len(payload)
    if n < 126: head += bytes([n])
    elif n < 65536: head += bytes([126]) + struct.pack("!H", n)
    else: head += bytes([127]) + struct.pack("!Q", n)
    sock.sendall(head + payload)

class Frames:
    """Reads client frames: masked, text or binary, fragmented, plus ping/pong/close."""
    def __init__(self, sock): self.sock, self.buf, self.parts, self.kind = sock, b"", [], None
    def _frame(self):
        """Parse one whole frame from the buffer, or None if it hasn't all arrived (nothing is consumed then)."""
        b = self.buf
        if len(b) < 2: return None
        fin, op, masked, n, i = b[0] & 0x80, b[0] & 0x0F, b[1] & 0x80, b[1] & 0x7F, 2
        if not masked: raise ConnectionError("client frames must be masked")
        if n == 126:
            if len(b) < 4: return None
            n, i = struct.unpack("!H", b[2:4])[0], 4
        elif n == 127:
            if len(b) < 10: return None
            n, i = struct.unpack("!Q", b[2:10])[0], 10
        if n > 1 << 20: raise ConnectionError("frame too large")
        if len(b) < i + 4 + n: return None
        mask, data = b[i:i + 4], bytearray(b[i + 4:i + 4 + n])
        for j in range(n): data[j] ^= mask[j % 4]
        self.buf = b[i + 4 + n:]
        return fin, op, bytes(data)
    def next(self):
        """Return (opcode, payload) for a complete message or control frame. A read timeout leaves the buffer intact."""
        while True:
            f = self._frame()
            while f is None:
                chunk = self.sock.recv(65536)
                if not chunk: raise ConnectionError("closed")
                self.buf += chunk; f = self._frame()
            fin, op, data = f
            if op >= 0x8: return op, data                     # control frames are never fragmented
            if op in (0x1, 0x2): self.kind, self.parts = op, [data]
            elif op == 0x0 and self.kind: self.parts.append(data)
            else: raise ConnectionError("bad continuation")
            if fin:
                kind, whole = self.kind, b"".join(self.parts); self.kind, self.parts = None, []
                return kind, whole

def refuse(h, code, why):
    h.send(code, {"error": why})

from rooms import ratified                   # reads the amendment log, not a string the code contains (Auditor, v004 item 2)

def agent_talk_ok():
    """Talking to an agent in the drawer (Article 18.8), once A-0030 is ratified (E-0092)."""
    return ratified("A-0030")

def active_agent(key):
    if not re.fullmatch(r"[a-z][a-z0-9]{1,15}", key or ""): return False
    try: return any(a["key"] == key and a["status"] == "active" for a in json.loads((ROOT / "agents/roster.json").read_text())["agents"])
    except (OSError, ValueError, KeyError): return False

def handle(h, public, port):
    """Serve GET /ws/shell?cmd=shell|herdr&token=...&cols=N&rows=N on handler h."""
    if public: return refuse(h, 403, "the terminal is off in public view")
    host = h.headers.get("Host") or ""
    if host not in (f"127.0.0.1:{port}", f"localhost:{port}"): return refuse(h, 403, "bad Host")
    if h.headers.get("Origin") not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"): return refuse(h, 403, "the Origin must be this dashboard")
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(h.path).query))
    if not take_token(q.get("token")): return refuse(h, 403, "a fresh one-time token is required")
    cmd = q.get("cmd")
    if cmd not in ("shell", "herdr", "agent"): return refuse(h, 400, "cmd must be shell, herdr, or agent")
    agent = q.get("agent") if cmd == "agent" else None
    if cmd == "agent":
        if not agent_talk_ok(): return refuse(h, 403, "talking to agents in the browser waits for the Steward's approval of amendment A-0030")
        if not active_agent(agent): return refuse(h, 400, "no active agent by that key")
    if (h.headers.get("Upgrade") or "").lower() != "websocket" or not h.headers.get("Sec-WebSocket-Key"):
        return refuse(h, 400, "a WebSocket upgrade is required")
    with TLOCK:
        if len(LIVE) >= MAX_SHELLS: return refuse(h, 429, f"at most {MAX_SHELLS} shells at once")
        LIVE["pending-" + secrets.token_hex(4)] = None
        slot = next(k for k in LIVE if k.startswith("pending-") and LIVE[k] is None)
    try:
        accept = base64.b64encode(hashlib.sha1((h.headers["Sec-WebSocket-Key"] + GUID).encode()).digest()).decode()
        h.send_response(101, "Switching Protocols")
        h.send_header("Upgrade", "websocket"); h.send_header("Connection", "Upgrade"); h.send_header("Sec-WebSocket-Accept", accept)
        h.end_headers(); h.wfile.flush()
        h.close_connection = True
        Session(h.connection, cmd, int(q.get("cols") or 80), int(q.get("rows") or 24), slot, agent).run()
    finally:
        with TLOCK: LIVE.pop(slot, None)

class Session:
    def __init__(self, sock, cmd, cols, rows, slot, agent=None):
        self.sock, self.cmd, self.slot, self.t0, self.last = sock, cmd, slot, time.time(), time.time()
        self.agent = agent
        self.label = f"talk with {agent}" if cmd == "agent" else cmd
        self.cols, self.rows = max(10, min(cols, 500)), max(3, min(rows, 300))
        self.out, self.out_bytes, self.line, self.line_t, self.hidden = bytearray(), 0, "", 0.0, 0
        self.tail, self.pending = bytearray(), []
        self.lock = threading.Lock()

    def spawn(self):
        master, slave = os.openpty()
        self.set_size(master)
        argv = ([os.environ.get("SHELL") or "/bin/bash", "-l"] if self.cmd == "shell" else ["herdr"] if self.cmd == "herdr"
                else [str(ROOT / "agents/bin/run-role.sh"), self.agent, "--interactive"])
        if self.cmd == "shell" and not os.path.exists(argv[0]): argv = ["/bin/bash", "-l"]
        env = {**os.environ, "TERM": "xterm-256color", "COLLECTIVE_WEB_TERMINAL": "1"}
        def ctty():   # make the pty this session's controlling terminal, so Ctrl-C reaches the foreground job
            fcntl.ioctl(0, termios.TIOCSCTTY, 0)
        self.proc = subprocess.Popen(argv, stdin=slave, stdout=slave, stderr=slave, cwd=ROOT, env=env,
                                     start_new_session=True, preexec_fn=ctty, close_fds=True)
        self.master, self.slave = master, slave     # the slave stays open here only to read the echo flag
        with TLOCK: LIVE[self.slot] = self

    def set_size(self, fd=None):
        fcntl.ioctl(fd if fd is not None else self.master, termios.TIOCSWINSZ, struct.pack("HHHH", self.rows, self.cols, 0, 0))

    # ---- typed lines (Enter, Ctrl-C, or 3 s idle) ----
    # A line is recorded only if the terminal echoed it back: a password prompt never echoes, so what's typed
    # there is counted as hidden and never stored. The check waits a moment after Enter, for the echo to arrive.
    ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[@-_]")
    def echoed(self, line):
        probe = line.replace("^C", "")[-12:].strip()
        if not probe: return True
        with self.lock: recent = self.ANSI.sub("", bytes(self.tail).decode("utf-8", "replace"))
        return probe in recent

    def typed(self, data):
        for ch in data.decode("utf-8", "replace"):
            if ch in "\r\n": self.flush("enter")
            elif ch == "\x03": self.line += "^C"; self.flush("ctrl-c")
            elif ch in "\x7f\x08": self.line = self.line[:-1]
            elif ch == "\x1b": self.line += ""            # escape sequences (arrows) are not text
            elif ch >= " ": self.line += ch
            self.line_t = time.time()

    def flush(self, why):
        if self.line.strip(): self.pending.append((time.time(), self.line, why))
        self.line = ""

    def settle(self, force=False):
        """Record pending lines once their echo has had time to arrive; unechoed ones are counted as hidden."""
        while self.pending and (force or time.time() - self.pending[0][0] > 0.6):
            _, line, why = self.pending.pop(0)
            if not self.echoed(line): self.hidden += 1; continue
            record("shell.input", {"summary": f"typed in the web {self.label}: {redact(line)[:120]}", "cmd": self.cmd, "agent": self.agent,
                                   "pid": self.proc.pid, "line": redact(line)[:2000], "ended_by": why})

    def run(self):
        self.spawn()
        record("shell.start", {"summary": f"web {self.label} started (pid {self.proc.pid})", "cmd": self.cmd, "agent": self.agent, "pid": self.proc.pid,
                               "cols": self.cols, "rows": self.rows})
        reader = threading.Thread(target=self.pump_out, daemon=True); reader.start()
        frames = Frames(self.sock); why = "closed"
        try:
            self.sock.settimeout(1.0)
            while self.proc.poll() is None:
                if time.time() - self.last > IDLE_SECS: why = "idle 30 minutes"; break
                if self.line and time.time() - self.line_t > LINE_IDLE: self.flush("idle")
                self.settle()
                try: op, data = frames.next()
                except socket.timeout: continue
                self.last = time.time()
                if op == 0x2: self.typed(data); os.write(self.master, data)
                elif op == 0x1:
                    try: msg = json.loads(data.decode())
                    except ValueError: continue
                    if msg.get("type") == "resize":
                        self.cols, self.rows = max(10, min(int(msg.get("cols", 80)), 500)), max(3, min(int(msg.get("rows", 24)), 300))
                        self.set_size()
                elif op == 0x9: send_frame(self.sock, 0xA, data)
                elif op == 0x8: why = "closed by the browser"; break
        except (ConnectionError, OSError):
            why = "disconnected"
        finally:
            self.end(why)

    def pump_out(self):
        while True:
            try:
                r, _, _ = select.select([self.master], [], [], 0.5)
                if not r:
                    if self.proc.poll() is not None: break
                    continue
                data = os.read(self.master, 65536)
            except OSError:
                break
            if not data: break
            with self.lock:
                self.out_bytes += len(data)
                self.tail += data; del self.tail[:-16384]           # recent output, for the echo check
                if len(self.out) < OUT_CAP: self.out += data[:OUT_CAP - len(self.out)]
            try: send_frame(self.sock, 0x2, data)
            except OSError: break

    def end(self, why):
        if self.line: self.flush("close")
        time.sleep(0.3); self.settle(force=True)
        try: os.killpg(self.proc.pid, signal.SIGHUP)
        except (ProcessLookupError, PermissionError): pass
        for fd in (self.master, self.slave):     # close the terminal first: an exiting shell waits for its output to drain
            try: os.close(fd)
            except OSError: pass
        try: self.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try: os.killpg(self.proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError): pass
            try: self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired: pass
        try: send_frame(self.sock, 0x8, struct.pack("!H", 1000))
        except OSError: pass
        with self.lock: text = redact(bytes(self.out).decode("utf-8", "replace"))   # decoded, so redaction always applies
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(text); blob = f.name
        record("shell.end", {"summary": f"web {self.label} ended ({why}) after {int(time.time() - self.t0)} s", "cmd": self.cmd, "agent": self.agent,
                             "pid": self.proc.pid, "duration_s": int(time.time() - self.t0), "bytes": self.out_bytes,
                             "cols": self.cols, "rows": self.rows, "reason": why, "hidden_lines": self.hidden}, blob=blob)
        os.unlink(blob)
