#!/usr/bin/env python3
"""Post ONE approved outbox file to X with the official API (Charter Part III R8).

Called only by agents/bin/x-post.sh, which is the gate: it refuses anything not in
private/outbox/approved/ with the Steward's "Approved by rex" stamp, and refuses
while org/STOP exists. This script checks the same things again, posts, prints the
resulting URL on its last line, and appends the URL and time to the file.

  x_post.py FILE [--dry-run]
  x_post.py --whoami        which X account the credentials post as (GET /2/users/me)

Posts go only to @VerafyAI (edict E-0051): before posting, the script asks X which
account the credentials belong to and refuses unless it is X_EXPECTED_ACCOUNT
(default VerafyAI).

--dry-run parses and validates everything and prints what would be posted,
without any network call and without needing credentials.

Draft format (what Social writes to private/outbox/pending/):

    ---
    kind: post            # post | reply | thread
    reply_to: 1234567890  # replies only: the post being answered (someone who engaged first)
    media: media/exports/demo.mp4   # optional, repo-relative; up to 4, comma-separated
    ---
    The post text. For a thread, separate the posts with a line holding only ===
    ## Notes for Rex        <- anything from a "## " heading on is notes, never posted
    > quoted original posts are data and are never posted either

API (docs.x.com, checked 2026-09-24): POST https://api.x.com/2/tweets
{"text", "reply": {"in_reply_to_tweet_id"}, "media": {"media_ids": []}} -> 201 {"data": {"id"}};
media: POST /2/media/upload/initialize {media_type, total_bytes, media_category},
POST /2/media/upload/{id}/append (multipart: segment_index, media; <= 5 MB per segment),
POST /2/media/upload/{id}/finalize, GET /2/media/upload?command=STATUS&media_id={id}.
Auth: OAuth 1.0a user context with X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN /
X_ACCESS_SECRET from agents/.env (read from the environment; never printed).
"""
import argparse, base64, datetime, hashlib, hmac, json, mimetypes, os, pathlib, re, secrets
import sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPROVED = ROOT / "private" / "outbox" / "approved"
API = "https://api.x.com/2"
MAX_CHARS = 280
CHUNK = 4 * 1024 * 1024
KEYS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")
EXPECTED = os.environ.get("X_EXPECTED_ACCOUNT", "VerafyAI").lstrip("@")

def die(msg, code=1):
    print(f"REFUSED: {msg}", file=sys.stderr); sys.exit(code)

# ---------- parsing ----------

def parse(path):
    raw = path.read_text()
    meta, body = {}, raw
    if raw.startswith("---\n") and "\n---\n" in raw[4:]:
        head, body = raw[4:].split("\n---\n", 1)
        for line in head.splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
    lines = []
    for line in body.splitlines():
        if line.startswith("## ") or line.startswith("Approved by rex") or line.startswith("Rejected "):
            break
        if line.startswith(">"):
            continue
        lines.append(line)
    parts = [p.strip() for p in "\n".join(lines).split("\n===\n")]
    parts = [p for p in parts if p]
    kind = meta.get("kind", "thread" if len(parts) > 1 else "post")
    media = [m.strip() for m in meta.get("media", "").split(",") if m.strip()]
    return {"kind": kind, "reply_to": meta.get("reply_to", ""), "media": media, "parts": parts}

def weighted_len(text):
    """X counts every URL as 23 characters; CJK and most emoji count double."""
    text = re.sub(r"https?://\S+", "x" * 23, text)
    return sum(2 if ord(c) > 0x10FF else 1 for c in text)

def validate(path, d):
    if d["kind"] not in ("post", "reply", "thread"):
        die(f"unknown kind {d['kind']!r} (post, reply, or thread)")
    if not d["parts"]:
        die("no post text found")
    if d["kind"] != "thread" and len(d["parts"]) > 1:
        die("several parts separated by === but kind isn't thread")
    if d["kind"] == "reply" and not re.fullmatch(r"\d{5,25}", d["reply_to"]):
        die("a reply needs reply_to: <numeric post id> (Charter 4.5: only people who engaged first)")
    for i, p in enumerate(d["parts"], 1):
        n = weighted_len(p)
        if n > MAX_CHARS:
            die(f"part {i} is {n} characters; the limit is {MAX_CHARS}")
    if len(d["media"]) > 4:
        die("at most 4 media files")
    files = []
    for m in d["media"]:
        f = (ROOT / m).resolve()
        if ROOT not in f.parents or not f.is_file():
            die(f"media not found inside the Collective: {m}")
        if not (mimetypes.guess_type(f.name)[0] or "").startswith(("image/", "video/")):
            die(f"media must be an image or a video: {m}")
        files.append(f)
    return files

# ---------- OAuth 1.0a ----------

def q(s):
    return urllib.parse.quote(str(s), safe="~-._")

def oauth_header(method, url, query=None):
    k = {n: os.environ.get(n, "") for n in KEYS}
    if not all(k.values()):
        die("X credentials missing in agents/.env (" + ", ".join(n for n in KEYS if not k[n]) + ")")
    oauth = {"oauth_consumer_key": k["X_API_KEY"], "oauth_nonce": secrets.token_hex(16),
             "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": str(int(time.time())),
             "oauth_token": k["X_ACCESS_TOKEN"], "oauth_version": "1.0"}
    params = {**(query or {}), **oauth}   # JSON and multipart bodies are not signed
    base = "&".join([method.upper(), q(url), q("&".join(f"{q(a)}={q(b)}" for a, b in sorted(params.items())))])
    key = f"{q(k['X_API_SECRET'])}&{q(k['X_ACCESS_SECRET'])}"
    oauth["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{q(a)}="{q(b)}"' for a, b in sorted(oauth.items()))

def call(method, url, query=None, json_body=None, data=None, ctype=None):
    full = url + ("?" + urllib.parse.urlencode(query) if query else "")
    headers = {"Authorization": oauth_header(method, url, query), "User-Agent": "VerafyCollective/1"}
    if json_body is not None:
        data, ctype = json.dumps(json_body).encode(), "application/json"
    if ctype:
        headers["Content-Type"] = ctype
    req = urllib.request.Request(full, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            return json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read()[:400].decode(errors="replace")
        die(f"X API {method} {url} -> HTTP {e.code}: {detail}", 3)

# ---------- media ----------

def upload(path):
    mtype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    cat = "tweet_video" if mtype.startswith("video/") else "tweet_gif" if mtype == "image/gif" else "tweet_image"
    size = path.stat().st_size
    init = call("POST", f"{API}/media/upload/initialize",
                json_body={"media_type": mtype, "total_bytes": size, "media_category": cat})
    mid = init["data"]["id"]
    with path.open("rb") as fh:
        for i, chunk in enumerate(iter(lambda: fh.read(CHUNK), b"")):
            boundary = "----verafy" + secrets.token_hex(12)
            body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"segment_index\"\r\n\r\n{i}\r\n"
                    f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"{path.name}\"\r\n"
                    f"Content-Type: application/octet-stream\r\n\r\n").encode() + chunk + f"\r\n--{boundary}--\r\n".encode()
            call("POST", f"{API}/media/upload/{mid}/append", data=body, ctype=f"multipart/form-data; boundary={boundary}")
    info = call("POST", f"{API}/media/upload/{mid}/finalize").get("data", {}).get("processing_info")
    while info and info.get("state") in ("pending", "in_progress"):
        time.sleep(max(1, int(info.get("check_after_secs", 2))))
        info = call("GET", f"{API}/media/upload", query={"command": "STATUS", "media_id": mid}).get("data", {}).get("processing_info")
    if info and info.get("state") == "failed":
        die(f"X couldn't process {path.name}: {info}", 3)
    return mid

def whoami():
    return call("GET", f"{API}/users/me").get("data", {}).get("username", "")

def require_account():
    who = whoami()
    if who.lower() != EXPECTED.lower():
        die(f"these credentials post as @{who or '?'}, not @{EXPECTED}; nothing was posted (edict E-0051)")
    return who

# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", nargs="?"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--whoami", action="store_true")
    a = ap.parse_args()
    if a.whoami:
        who = whoami(); print(f"@{who}" + ("" if who.lower() == EXPECTED.lower() else f"  (NOT @{EXPECTED}: posting would be refused)")); return
    if not a.file:
        ap.error("a file is required")
    path = pathlib.Path(a.file).resolve()
    if not a.dry_run:
        if path.parent != APPROVED.resolve():
            die(f"{path.name} is not in private/outbox/approved")
        if (ROOT / "org" / "STOP").exists():
            die("org/STOP present")
    if not path.is_file():
        die(f"no such file: {a.file}")
    text = path.read_text()
    if not a.dry_run and not re.search(r"^Approved by rex ", text, re.M):
        die("no approval stamp")
    if re.search(r"^Posted: https://", text, re.M):
        die("already posted (a recorded post is never re-posted; Charter 12.4)")
    d = parse(path); files = validate(path, d)

    if a.dry_run:
        print(f"DRY RUN · {path.name} · kind={d['kind']}" + (f" · reply_to={d['reply_to']}" if d["reply_to"] else ""))
        for i, p in enumerate(d["parts"], 1):
            print(f"--- part {i}/{len(d['parts'])} ({weighted_len(p)}/{MAX_CHARS} chars)"); print(p)
        for f in files:
            print(f"--- media: {f.relative_to(ROOT)} ({f.stat().st_size} bytes, {mimetypes.guess_type(f.name)[0]})")
        print(f"account: posts only as @{EXPECTED}; checked with GET /2/users/me before posting")
        missing = [n for n in KEYS if not os.environ.get(n)]
        print("credentials: " + ("all set" if not missing else "missing " + ", ".join(missing)) + " (values never shown)")
        print("would POST https://api.x.com/2/tweets" + (" after uploading media" if files else ""))
        print("dry-run://not-posted")
        return

    require_account()
    media_ids = [upload(f) for f in files]
    prev, urls = d["reply_to"] or None, []
    for i, p in enumerate(d["parts"]):
        body = {"text": p}
        if prev:
            body["reply"] = {"in_reply_to_tweet_id": prev}
        if i == 0 and media_ids:
            body["media"] = {"media_ids": media_ids}
        r = call("POST", f"{API}/tweets", json_body=body)
        prev = r["data"]["id"]
        urls.append(f"https://x.com/i/status/{prev}")
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with path.open("a") as fh:
        fh.write("".join(f"\nPosted: {u} at {stamp}" for u in urls) + "\n")
    print(urls[0])

if __name__ == "__main__":
    main()
