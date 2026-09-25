---
id: A-0028
title: A real terminal in the browser
class: B
status: ratified
proposer: Rex St. John (Steward), edicts E-0083 and E-0086 (ratification)
proposed: 2026-09-24
charter_version: v6.10.0
log_entry_hash: 49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5
---

# Amendment 028 · A real terminal in the browser

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.10.0 (`charter/history/CHARTER-v6.10.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.10.0`.

## Reason

Article 18.7(h): in private view only, a real terminal on the Steward's machine (a login shell or herdr) in the dashboard's Terminal drawer: Steward-only, same origin and a one-time token (30 s), at most 4 at once, killed on disconnect or 30 minutes idle; every session's output (5 MB cap) and every typed line recorded (lines typed without echo, such as passwords, counted and never recorded; all recorded text redacted). AGENT-PERMISSIONS (V.3): the web terminal is Steward-only; no agent is given a tool that opens it. eventlog.py (V.24): SECRET_RE also redacts xAI keys (xai-...), which it missed. Part V: new dashboard/shell_bridge.py and tests/test_shell.py. User Guide (V.112) section 6c, matching v6.10.0.

## Discussion

Board thread: org/board/2026-09-24-amendment-a-0028.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.10.0 on 2026-09-24.
Amendment log entry hash: `49750e86a14a980463096603771d0ce045b357424611552844788be8c8be4ca5` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.10.0). File generated from the verified amendment log.
