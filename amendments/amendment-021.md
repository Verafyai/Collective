---
id: A-0021
title: Moving agents between rooms; talking to an agent in a terminal
proposed_by: Rex St. John (Steward), edicts E-0064, E-0066, E-0067 (ratification)
thread: org/board/2026-09-24-amendment-a-0021.md
change: Article 18.7 now lists the dashboard's writes as items and adds (c): in private view only, the Steward's move of an agent to another room by dragging it on the floor, through spawn.py move, recorded; cosmetic, no change to powers, vote, tools, or schedule. New Article 18.8: Open terminal on each bio starts a recorded conversation with the agent (a herdr tab or a standalone Terminal window) with its own instructions and exactly its office's tools, never permission-skipping flags; the Steward's directions in it are edicts; refused in public view, cross-origin, and for unknown or retired agents. Part V: spawn.py (V.124, move), run-role.sh (V.18, --interactive: recorded prompt and transcript, the Steward's messages copied to org/board/<date>-talk-<role>.md), new agents/bin/terminal.sh.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 4528d7ea7997fcadc4c43a0287022b6d71064a80ade9541761a70666e138b817
prev_entry_hash: fbe7b2844da750e4e45db22a6ee0ac2d43d869f4475a3fbb1616701cf07888da
entry_hash: aa26a4a176bd52e6f45fcfb9acdc0ee2ba38984b86fe54956fda902c8a56011f

### A-0022 · v6.6.0 · 2026-09-24 · Class B · The Steward's comments in chats; post summaries
proposed_by: Rex St. John (Steward), edicts E-0068, E-0072 (ratification)
thread: org/board/2026-09-24-amendment-a-0022.md
change: Article 18.7(d): in private view only, the Steward's comment in a floor chat, appended to that board thread as `### rex · <timestamp>` and recorded; a comment that gives a direction is also recorded as an edict (Article 15). COMMON.md (V.6): every board post starts with a one-sentence summary of at most 25 words on the line after its header, then a blank line, then the details; the floor shows the summary and reveals the full text under Advanced.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 64c88ab0f17d4bcd057067c166e30d00b6a3932afa365ed1aadd2fca9ce3666a
prev_entry_hash: aa26a4a176bd52e6f45fcfb9acdc0ee2ba38984b86fe54956fda902c8a56011f
entry_hash: 38b4a581df90fe8679f8de5e1251d467828cae25d7731467ae4500f1bd602935

### A-0023 · v6.7.0 · 2026-09-24 · Class B · Ranks and permissions
proposed_by: Rex St. John (Steward), edicts E-0069, E-0070, E-0072 (ratification)
thread: org/board/2026-09-24-amendment-a-0023.md
change: New Article 3.9: the Steward grants or revokes an agent's capabilities (post to X, post to GitHub, send notifications, vote) on the dashboard's Permissions tab; a checked box is the ratification (Article 7.6), recorded by perms.py as an edict and an event, applied to the office's tools, and recorded by the Scribe; entrenched limits kept (4.3 approval of every post; 17.4 public pushes); email, Telegram, and text messages listed but unavailable. Ranks: I.C., Manager (a group the Steward picks), General Manager (every maker), Big Boss (every agent except the Scribe, Lawyer, and Auditor); a supervisor may pause, unpause, and reassign tasks within its group (supervise.py), never a pause the Steward set, a retirement, org/STOP, or the neutral officers' work; a rank never adds a vote or grants tools; the neutral officers never vote or rank above I.C. Article 18.7(e): the Permissions tab's changes are a dashboard write. Part V: new perms.py and supervise.py; AGENT-PERMISSIONS (V.3) and OFFICERS (V.2) updated; tests (V.125, V.126) cover moves, comments, permissions, ranks, supervision, and huddle gating.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 54917010373a62a5b430c319e60c34b39f8f534b810a5e539b7bb6c17cbac981
prev_entry_hash: 38b4a581df90fe8679f8de5e1251d467828cae25d7731467ae4500f1bd602935
entry_hash: 8de3db11acb31ba2af11ff2940f71ead3cb75ea877abaf002eacfedb7ee9afc5

### A-0024 · v6.8.0 · 2026-09-24 · Class B · Huddles at the coffee machine
proposed_by: Rex St. John (Steward), edicts E-0076, E-0077 (ratification)
thread: org/board/2026-09-24-amendment-a-0024.md
change: Article 18.7(f): in private view only, the Steward calls a huddle (the Huddle button or the floor's coffee machine), which starts a #huddle board thread addressed to every agent, and closes it; recorded as events. While it is open the floor gathers everyone at the coffee machine. COMMON.md (V.6): if a #huddle thread is open, each office answers it first, in one or two sentences, before any other work. A huddle pauses no one: agents answer on their next scheduled run.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 34df978daec52337de04f1b8d9476ae9b61543c090a0f42e62c0fb2454be4bdf
prev_entry_hash: 8de3db11acb31ba2af11ff2940f71ead3cb75ea877abaf002eacfedb7ee9afc5
entry_hash: 02143f668bcc5b0deefbd86682232e5717f0782cb27b7656cf18addb7968e541

### A-0025 · v6.8.1 · 2026-09-24 · Class C · Mission-driven KPIs and draft OKRs
proposed_by: Rex St. John (Steward), edicts E-0052 and E-0053 (the Steward's spec, specs/steward-2026-09-24-mission-kpis-verafy-bench.md)
thread: org/board/2026-09-24-amendment-a-0025.md
change: org/KPIS.md (V.104) rewritten per the spec's section 2: mission KPIs that measure whether the Collective is right, stays right, and gets cheaper at being right, each with a guardrail; North Star durable_claims_weekly; new reproducibility_rate (E-0053), reported in two tiers (recomputed from committed predictions; re-run on a sample within tolerance, per the Lawyer's opinion); the earlier activity KPIs become health metrics, not goals. org/OKRS.md (V.103) replaced by the spec's section 3, organized in two families (research and engineering; organizational, E-0053), still DRAFT with provisional targets until Sprint 1's baselines; O5 is the setup agent's suggestion, marked as such. Open question for the Steward: who owns source_support_rate (the Lawyer raised that it has no web tools and doesn't audit).
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 5757dff95b25e758aa7933e54ecd35478f936cc0869689be70bdd043a5d708f3
prev_entry_hash: 02143f668bcc5b0deefbd86682232e5717f0782cb27b7656cf18addb7968e541
entry_hash: 8eaba38ccdba2f8d4474eec1bbe16df72da73f91f4695ec8acc97b82fbbdd44d

### A-0026 · v6.9.0 · 2026-09-24 · Class B · Firing an agent from the dashboard
proposed_by: Rex St. John (Steward), edicts E-0081, E-0082 (ratification)
thread: org/board/2026-09-24-amendment-a-0026.md
change: Article 18.7(g): in private view only, the Steward's Fire button on a non-officer agent's bio pauses that agent at once (the Steward's pause) and drafts its retirement motion (spawn.py retire, Class M); the retirement takes effect only when the motion passes (Articles 3.6, 3.8) and the Scribe applies it; officers can't be fired this way; the agent's history is kept.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 32cba22ff780f7c0689c731e550aa54793d1b05d91a7062b3806827fa90c5b91
prev_entry_hash: 8eaba38ccdba2f8d4474eec1bbe16df72da73f91f4695ec8acc97b82fbbdd44d
entry_hash: 6a63bf4f07521d8fa7e36fb9a2a9bec69aedb9af4fe32b6be926fc1c08131a3c

### A-0027 · v6.9.1 · 2026-09-24 · Class C · Auditor's version 003 findings: terminal edicts, same-origin writes
proposed_by: Rex St. John (Steward), edicts E-0080 and E-0082, at the Auditor's version 003 review
thread: org/board/2026-09-24-amendment-a-0027.md
change: run-role.sh (V.18): an interactive conversation files the Steward's messages verbatim as one edict, as Article 18.8 requires (the Auditor's finding 2). tests/test_dashboard.py (V.126): writes are sent as a browser sends them, with this server's Origin, and a write without an Origin is refused. Outside Part V (P-001 code): every dashboard write now requires this server's Origin; huddles stay open until the Steward closes them (finding 3, Article 18.7(f)); the remaining roster values are escaped; malformed query numbers no longer raise. Not fixed here (finding 1): an office with unrestricted code execution (Bash(python3:*), Bash(node:*)) can still act as the Steward on this machine; that needs a tool change the Steward decides.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 020ed74a3c69a8e886d19ddc6480348dfdb7aa566eacf3eb12b1c382ad3157d1
prev_entry_hash: 6a63bf4f07521d8fa7e36fb9a2a9bec69aedb9af4fe32b6be926fc1c08131a3c
entry_hash: f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0

### A-0028 · v6.10.0 · 2026-09-24 · Class B · A real terminal in the browser
proposed_by: Rex St. John (Steward), edicts E-0083 and E-0086 (ratification)
thread: org/board/2026-09-24-amendment-a-0028.md
change: Article 18.7(h): in private view only, a real terminal on the Steward's machine (a login shell or herdr) in the dashboard's Terminal drawer: Steward-only, same origin and a one-time token (30 s), at most 4 at once, killed on disconnect or 30 minutes idle; every session's output (5 MB cap) and every typed line recorded (lines typed without echo, such as passwords, counted and never recorded; all recorded text redacted). AGENT-PERMISSIONS (V.3): the web terminal is Steward-only; no agent is given a tool that opens it. eventlog.py (V.24): SECRET_RE also redacts xAI keys (xai-...), which it missed. Part V: new dashboard/shell_bridge.py and tests/test_shell.py. User Guide (V.112) section 6c, matching v6.10.0.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: dd8f70ba529339b2af83591fab65716a4428eeca2d65c1e910d599d4684c3f1b
prev_entry_hash: f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0
entry_hash: 49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5

### A-0029 · v6.10.1 · 2026-09-24 · Class C · Vendored code and the redaction gate
proposed_by: Rex St. John (Steward), edicts E-0083 and E-0086, at the test failure found while recording A-0028
thread: org/board/2026-09-24-amendment-a-0029.md
change: repos.sh (V.22): gitleaks flagged minified vendored xterm.js as a generic API key, which would block every public commit. Vendored third-party files under dashboard/vendor/ now skip gitleaks only while each still matches its committed SHA256SUMS; a changed file is scanned as before, and the grep scan still covers every file.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 62ab8f7da0999f516ebe9204dceb3dae2d2e6813e92add528c34747eb7dbdfc0
prev_entry_hash: 49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5
entry_hash: 52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2

### A-0030 · v6.11.0 · 2026-09-25 · Class B · Projects on the floor; one chat per room; talking to agents in the web terminal drawer
proposed_by: Rex St. John (Steward), edicts E-0087 to E-0096, E-0098 (ratification: E-0097)
thread: org/board/2026-09-25-amendment-a-0030.md
change: Article 18.7(c): a move into a project room also assigns work. 18.7(h): the web terminal may also run a talk with one agent (Article 18.8). New 18.7(i): the Steward's new project from the floor (a codename and a spec, saved under specs/, recorded as an edict, created by projects.py new --spec with the Project Manager as owner, in a room of its own recorded in org/rooms.json by rooms.py); seating an agent in a project room gives it one tsk task and a note in the project's thread. New 18.7(j): renaming a room's codename. New paragraph **New projects from the floor.**: every room is a project; floor chats are per room; the whole Collective shares a chat only in a huddle. 18.8: Open terminal talks in the web terminal drawer by default. 21.2: the Steward's own spec from the dashboard is an approved spec, with the Lawyer's opinion afterward. Part V: new agents/bin/rooms.py (gated on this amendment's ratified log entry); spawn.py (rooms from org/rooms.json); shell_bridge.py (the agent command); COMMON.md (project rooms); CREDITS.md (xterm.js); tests.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 893cff2a34711cdc5e8be50272bace758d16e97851afd2047da1727cfed2a24d
prev_entry_hash: 52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2
entry_hash: d305e7bf5080e73fcef3487f81efc3d9e7aab2701532c216be475d799a718047

### A-0031 · v6.11.1 · 2026-09-25 · Class M · Spawn Get Scholar (Scholar)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0031.md
change: Membership: Get Scholar (`getscholar`, class Scholar) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 42926dc9f537e190620f95de45047433a19bdfa3dfcb897cd833b96108a07b87
prev_entry_hash: d305e7bf5080e73fcef3487f81efc3d9e7aab2701532c216be475d799a718047
entry_hash: ef38aa79616db62c3b94a9c7f8385b12405005522125806253f9ffb2e0a81de4

### A-0032 · v6.11.2 · 2026-09-25 · Class M · Spawn Get Inventor (Inventor)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0032.md
change: Membership: Get Inventor (`getinventor`, class Inventor) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 707235f3451028b943fe3b99e2ef7647cb77a296af69bceb0b8710c354ec0fac
prev_entry_hash: ef38aa79616db62c3b94a9c7f8385b12405005522125806253f9ffb2e0a81de4
entry_hash: 633ba53fdcccc2da2230b0c615d47e695fb08938a8c24c78e015e5985308bdeb

### A-0033 · v6.11.3 · 2026-09-25 · Class M · Spawn Get Verifier (Verifier)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0033.md
change: Membership: Get Verifier (`getverifier`, class Verifier) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 2cc073a37268e404d1dfeb62da48ec5fba38804f0ffb2b1fad79f9ddb8edfd05
prev_entry_hash: 633ba53fdcccc2da2230b0c615d47e695fb08938a8c24c78e015e5985308bdeb
entry_hash: 49fb4effa8fa04da03453b0d16dadd2c7e4b3e371ec3cf54feb9c1ae00f2a72d

### A-0034 · v6.11.4 · 2026-09-25 · Class C · A-0030 follow-up: tests independent of live state
proposed_by: Rex St. John (Steward), edict E-0097 (ratifying all of A-0030's open work)
thread: org/board/2026-09-25-amendment-a-0034.md
change: Part V: tests/test_shell.py and tests/test_dashboard.py simulate an unratified A-0030 by removing its log entry in their scratch copy (the gate reads the ratified log entry, not a marker), and check room chats against whatever rooms the roster seats agents in.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: a4e99fb4cd1e556f5d40bc2ff7e2e086f4ae2ec6e4855eb2f5bd15c5c888bc7f
prev_entry_hash: 49fb4effa8fa04da03453b0d16dadd2c7e4b3e371ec3cf54feb9c1ae00f2a72d
entry_hash: 26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a

### A-0035 · v6.11.5 · 2026-09-25 · Class C · New members' configuration recorded
proposed_by: The Scribe's record (Article 7.7) of A-0031 to A-0033, done by the setup session
thread: org/board/2026-09-25-amendment-a-0035.md
change: Part V: agents/config.example.env gains GETSCHOLAR_, GETINVENTOR_, and GETVERIFIER_ INTERVAL, MAX_RUNS, and base TOOLS (requested tools noted, awaiting the Steward, Article 7.6); herdr/projects/collective.toml gains their loop tabs.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 4412f58634680ce7b6c5a622bb159c7fefc03534ea325ea019430fb4a0901a81
prev_entry_hash: 26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a
entry_hash: 21e9446f5a584ade0b32e170d00466103f752afd17c8cdb2d005ce9f7c449f14
class: B
status: ratified
proposer: 
proposed: 2026-09-24
charter_version: v6.5.0
log_entry_hash: 
---

# Amendment 021 · Moving agents between rooms; talking to an agent in a terminal
proposed_by: Rex St. John (Steward), edicts E-0064, E-0066, E-0067 (ratification)
thread: org/board/2026-09-24-amendment-a-0021.md
change: Article 18.7 now lists the dashboard's writes as items and adds (c): in private view only, the Steward's move of an agent to another room by dragging it on the floor, through spawn.py move, recorded; cosmetic, no change to powers, vote, tools, or schedule. New Article 18.8: Open terminal on each bio starts a recorded conversation with the agent (a herdr tab or a standalone Terminal window) with its own instructions and exactly its office's tools, never permission-skipping flags; the Steward's directions in it are edicts; refused in public view, cross-origin, and for unknown or retired agents. Part V: spawn.py (V.124, move), run-role.sh (V.18, --interactive: recorded prompt and transcript, the Steward's messages copied to org/board/<date>-talk-<role>.md), new agents/bin/terminal.sh.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 4528d7ea7997fcadc4c43a0287022b6d71064a80ade9541761a70666e138b817
prev_entry_hash: fbe7b2844da750e4e45db22a6ee0ac2d43d869f4475a3fbb1616701cf07888da
entry_hash: aa26a4a176bd52e6f45fcfb9acdc0ee2ba38984b86fe54956fda902c8a56011f

### A-0022 · v6.6.0 · 2026-09-24 · Class B · The Steward's comments in chats; post summaries
proposed_by: Rex St. John (Steward), edicts E-0068, E-0072 (ratification)
thread: org/board/2026-09-24-amendment-a-0022.md
change: Article 18.7(d): in private view only, the Steward's comment in a floor chat, appended to that board thread as `### rex · <timestamp>` and recorded; a comment that gives a direction is also recorded as an edict (Article 15). COMMON.md (V.6): every board post starts with a one-sentence summary of at most 25 words on the line after its header, then a blank line, then the details; the floor shows the summary and reveals the full text under Advanced.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 64c88ab0f17d4bcd057067c166e30d00b6a3932afa365ed1aadd2fca9ce3666a
prev_entry_hash: aa26a4a176bd52e6f45fcfb9acdc0ee2ba38984b86fe54956fda902c8a56011f
entry_hash: 38b4a581df90fe8679f8de5e1251d467828cae25d7731467ae4500f1bd602935

### A-0023 · v6.7.0 · 2026-09-24 · Class B · Ranks and permissions
proposed_by: Rex St. John (Steward), edicts E-0069, E-0070, E-0072 (ratification)
thread: org/board/2026-09-24-amendment-a-0023.md
change: New Article 3.9: the Steward grants or revokes an agent's capabilities (post to X, post to GitHub, send notifications, vote) on the dashboard's Permissions tab; a checked box is the ratification (Article 7.6), recorded by perms.py as an edict and an event, applied to the office's tools, and recorded by the Scribe; entrenched limits kept (4.3 approval of every post; 17.4 public pushes); email, Telegram, and text messages listed but unavailable. Ranks: I.C., Manager (a group the Steward picks), General Manager (every maker), Big Boss (every agent except the Scribe, Lawyer, and Auditor); a supervisor may pause, unpause, and reassign tasks within its group (supervise.py), never a pause the Steward set, a retirement, org/STOP, or the neutral officers' work; a rank never adds a vote or grants tools; the neutral officers never vote or rank above I.C. Article 18.7(e): the Permissions tab's changes are a dashboard write. Part V: new perms.py and supervise.py; AGENT-PERMISSIONS (V.3) and OFFICERS (V.2) updated; tests (V.125, V.126) cover moves, comments, permissions, ranks, supervision, and huddle gating.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 54917010373a62a5b430c319e60c34b39f8f534b810a5e539b7bb6c17cbac981
prev_entry_hash: 38b4a581df90fe8679f8de5e1251d467828cae25d7731467ae4500f1bd602935
entry_hash: 8de3db11acb31ba2af11ff2940f71ead3cb75ea877abaf002eacfedb7ee9afc5

### A-0024 · v6.8.0 · 2026-09-24 · Class B · Huddles at the coffee machine
proposed_by: Rex St. John (Steward), edicts E-0076, E-0077 (ratification)
thread: org/board/2026-09-24-amendment-a-0024.md
change: Article 18.7(f): in private view only, the Steward calls a huddle (the Huddle button or the floor's coffee machine), which starts a #huddle board thread addressed to every agent, and closes it; recorded as events. While it is open the floor gathers everyone at the coffee machine. COMMON.md (V.6): if a #huddle thread is open, each office answers it first, in one or two sentences, before any other work. A huddle pauses no one: agents answer on their next scheduled run.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 34df978daec52337de04f1b8d9476ae9b61543c090a0f42e62c0fb2454be4bdf
prev_entry_hash: 8de3db11acb31ba2af11ff2940f71ead3cb75ea877abaf002eacfedb7ee9afc5
entry_hash: 02143f668bcc5b0deefbd86682232e5717f0782cb27b7656cf18addb7968e541

### A-0025 · v6.8.1 · 2026-09-24 · Class C · Mission-driven KPIs and draft OKRs
proposed_by: Rex St. John (Steward), edicts E-0052 and E-0053 (the Steward's spec, specs/steward-2026-09-24-mission-kpis-verafy-bench.md)
thread: org/board/2026-09-24-amendment-a-0025.md
change: org/KPIS.md (V.104) rewritten per the spec's section 2: mission KPIs that measure whether the Collective is right, stays right, and gets cheaper at being right, each with a guardrail; North Star durable_claims_weekly; new reproducibility_rate (E-0053), reported in two tiers (recomputed from committed predictions; re-run on a sample within tolerance, per the Lawyer's opinion); the earlier activity KPIs become health metrics, not goals. org/OKRS.md (V.103) replaced by the spec's section 3, organized in two families (research and engineering; organizational, E-0053), still DRAFT with provisional targets until Sprint 1's baselines; O5 is the setup agent's suggestion, marked as such. Open question for the Steward: who owns source_support_rate (the Lawyer raised that it has no web tools and doesn't audit).
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 5757dff95b25e758aa7933e54ecd35478f936cc0869689be70bdd043a5d708f3
prev_entry_hash: 02143f668bcc5b0deefbd86682232e5717f0782cb27b7656cf18addb7968e541
entry_hash: 8eaba38ccdba2f8d4474eec1bbe16df72da73f91f4695ec8acc97b82fbbdd44d

### A-0026 · v6.9.0 · 2026-09-24 · Class B · Firing an agent from the dashboard
proposed_by: Rex St. John (Steward), edicts E-0081, E-0082 (ratification)
thread: org/board/2026-09-24-amendment-a-0026.md
change: Article 18.7(g): in private view only, the Steward's Fire button on a non-officer agent's bio pauses that agent at once (the Steward's pause) and drafts its retirement motion (spawn.py retire, Class M); the retirement takes effect only when the motion passes (Articles 3.6, 3.8) and the Scribe applies it; officers can't be fired this way; the agent's history is kept.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 32cba22ff780f7c0689c731e550aa54793d1b05d91a7062b3806827fa90c5b91
prev_entry_hash: 8eaba38ccdba2f8d4474eec1bbe16df72da73f91f4695ec8acc97b82fbbdd44d
entry_hash: 6a63bf4f07521d8fa7e36fb9a2a9bec69aedb9af4fe32b6be926fc1c08131a3c

### A-0027 · v6.9.1 · 2026-09-24 · Class C · Auditor's version 003 findings: terminal edicts, same-origin writes
proposed_by: Rex St. John (Steward), edicts E-0080 and E-0082, at the Auditor's version 003 review
thread: org/board/2026-09-24-amendment-a-0027.md
change: run-role.sh (V.18): an interactive conversation files the Steward's messages verbatim as one edict, as Article 18.8 requires (the Auditor's finding 2). tests/test_dashboard.py (V.126): writes are sent as a browser sends them, with this server's Origin, and a write without an Origin is refused. Outside Part V (P-001 code): every dashboard write now requires this server's Origin; huddles stay open until the Steward closes them (finding 3, Article 18.7(f)); the remaining roster values are escaped; malformed query numbers no longer raise. Not fixed here (finding 1): an office with unrestricted code execution (Bash(python3:*), Bash(node:*)) can still act as the Steward on this machine; that needs a tool change the Steward decides.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 020ed74a3c69a8e886d19ddc6480348dfdb7aa566eacf3eb12b1c382ad3157d1
prev_entry_hash: 6a63bf4f07521d8fa7e36fb9a2a9bec69aedb9af4fe32b6be926fc1c08131a3c
entry_hash: f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0

### A-0028 · v6.10.0 · 2026-09-24 · Class B · A real terminal in the browser
proposed_by: Rex St. John (Steward), edicts E-0083 and E-0086 (ratification)
thread: org/board/2026-09-24-amendment-a-0028.md
change: Article 18.7(h): in private view only, a real terminal on the Steward's machine (a login shell or herdr) in the dashboard's Terminal drawer: Steward-only, same origin and a one-time token (30 s), at most 4 at once, killed on disconnect or 30 minutes idle; every session's output (5 MB cap) and every typed line recorded (lines typed without echo, such as passwords, counted and never recorded; all recorded text redacted). AGENT-PERMISSIONS (V.3): the web terminal is Steward-only; no agent is given a tool that opens it. eventlog.py (V.24): SECRET_RE also redacts xAI keys (xai-...), which it missed. Part V: new dashboard/shell_bridge.py and tests/test_shell.py. User Guide (V.112) section 6c, matching v6.10.0.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: dd8f70ba529339b2af83591fab65716a4428eeca2d65c1e910d599d4684c3f1b
prev_entry_hash: f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0
entry_hash: 49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5

### A-0029 · v6.10.1 · 2026-09-24 · Class C · Vendored code and the redaction gate
proposed_by: Rex St. John (Steward), edicts E-0083 and E-0086, at the test failure found while recording A-0028
thread: org/board/2026-09-24-amendment-a-0029.md
change: repos.sh (V.22): gitleaks flagged minified vendored xterm.js as a generic API key, which would block every public commit. Vendored third-party files under dashboard/vendor/ now skip gitleaks only while each still matches its committed SHA256SUMS; a changed file is scanned as before, and the grep scan still covers every file.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 62ab8f7da0999f516ebe9204dceb3dae2d2e6813e92add528c34747eb7dbdfc0
prev_entry_hash: 49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5
entry_hash: 52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2

### A-0030 · v6.11.0 · 2026-09-25 · Class B · Projects on the floor; one chat per room; talking to agents in the web terminal drawer
proposed_by: Rex St. John (Steward), edicts E-0087 to E-0096, E-0098 (ratification: E-0097)
thread: org/board/2026-09-25-amendment-a-0030.md
change: Article 18.7(c): a move into a project room also assigns work. 18.7(h): the web terminal may also run a talk with one agent (Article 18.8). New 18.7(i): the Steward's new project from the floor (a codename and a spec, saved under specs/, recorded as an edict, created by projects.py new --spec with the Project Manager as owner, in a room of its own recorded in org/rooms.json by rooms.py); seating an agent in a project room gives it one tsk task and a note in the project's thread. New 18.7(j): renaming a room's codename. New paragraph **New projects from the floor.**: every room is a project; floor chats are per room; the whole Collective shares a chat only in a huddle. 18.8: Open terminal talks in the web terminal drawer by default. 21.2: the Steward's own spec from the dashboard is an approved spec, with the Lawyer's opinion afterward. Part V: new agents/bin/rooms.py (gated on this amendment's ratified log entry); spawn.py (rooms from org/rooms.json); shell_bridge.py (the agent command); COMMON.md (project rooms); CREDITS.md (xterm.js); tests.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 893cff2a34711cdc5e8be50272bace758d16e97851afd2047da1727cfed2a24d
prev_entry_hash: 52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2
entry_hash: d305e7bf5080e73fcef3487f81efc3d9e7aab2701532c216be475d799a718047

### A-0031 · v6.11.1 · 2026-09-25 · Class M · Spawn Get Scholar (Scholar)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0031.md
change: Membership: Get Scholar (`getscholar`, class Scholar) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 42926dc9f537e190620f95de45047433a19bdfa3dfcb897cd833b96108a07b87
prev_entry_hash: d305e7bf5080e73fcef3487f81efc3d9e7aab2701532c216be475d799a718047
entry_hash: ef38aa79616db62c3b94a9c7f8385b12405005522125806253f9ffb2e0a81de4

### A-0032 · v6.11.2 · 2026-09-25 · Class M · Spawn Get Inventor (Inventor)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0032.md
change: Membership: Get Inventor (`getinventor`, class Inventor) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 707235f3451028b943fe3b99e2ef7647cb77a296af69bceb0b8710c354ec0fac
prev_entry_hash: ef38aa79616db62c3b94a9c7f8385b12405005522125806253f9ffb2e0a81de4
entry_hash: 633ba53fdcccc2da2230b0c615d47e695fb08938a8c24c78e015e5985308bdeb

### A-0033 · v6.11.3 · 2026-09-25 · Class M · Spawn Get Verifier (Verifier)
proposed_by: Rex St. John (Steward), from the New project form (Project Get a job, P-003); ratified by edict E-0101
thread: org/board/2026-09-25-amendment-a-0033.md
change: Membership: Get Verifier (`getverifier`, class Verifier) joins, seated in Project Get a job (room getajob, P-003). The Steward ratified the motion directly (Article 2.2, edict E-0101: 'they need to all get approved') instead of the Article 3.6 vote. Base tools only and no vote (Article 3.6 safeguards); requested tools still need the Steward (Article 7.6). The roster is a live record.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 2cc073a37268e404d1dfeb62da48ec5fba38804f0ffb2b1fad79f9ddb8edfd05
prev_entry_hash: 633ba53fdcccc2da2230b0c615d47e695fb08938a8c24c78e015e5985308bdeb
entry_hash: 49fb4effa8fa04da03453b0d16dadd2c7e4b3e371ec3cf54feb9c1ae00f2a72d

### A-0034 · v6.11.4 · 2026-09-25 · Class C · A-0030 follow-up: tests independent of live state
proposed_by: Rex St. John (Steward), edict E-0097 (ratifying all of A-0030's open work)
thread: org/board/2026-09-25-amendment-a-0034.md
change: Part V: tests/test_shell.py and tests/test_dashboard.py simulate an unratified A-0030 by removing its log entry in their scratch copy (the gate reads the ratified log entry, not a marker), and check room chats against whatever rooms the roster seats agents in.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: a4e99fb4cd1e556f5d40bc2ff7e2e086f4ae2ec6e4855eb2f5bd15c5c888bc7f
prev_entry_hash: 49fb4effa8fa04da03453b0d16dadd2c7e4b3e371ec3cf54feb9c1ae00f2a72d
entry_hash: 26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a

### A-0035 · v6.11.5 · 2026-09-25 · Class C · New members' configuration recorded
proposed_by: The Scribe's record (Article 7.7) of A-0031 to A-0033, done by the setup session
thread: org/board/2026-09-25-amendment-a-0035.md
change: Part V: agents/config.example.env gains GETSCHOLAR_, GETINVENTOR_, and GETVERIFIER_ INTERVAL, MAX_RUNS, and base TOOLS (requested tools noted, awaiting the Steward, Article 7.6); herdr/projects/collective.toml gains their loop tabs.
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: 4412f58634680ce7b6c5a622bb159c7fefc03534ea325ea019430fb4a0901a81
prev_entry_hash: 26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a
entry_hash: 21e9446f5a584ade0b32e170d00466103f752afd17c8cdb2d005ce9f7c449f14

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.5.0 (`charter/history/CHARTER-v6.5.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.5.0`.

## Reason



## Discussion

Board thread: —

## Vote


Ratified by: 

## Outcome

Ratified and applied to the Charter as v6.5.0 on 2026-09-24.
Amendment log entry hash: `` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.5.0). File generated from the verified amendment log.
- 2026-09-25: this file had held the Spawn Charlie motion by mistake (a numbering collision). That motion is now A-0036 (E-0102); this file matches the log again.
