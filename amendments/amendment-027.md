---
id: A-0027
title: Auditor's version 003 findings: terminal edicts, same-origin writes
class: C
status: ratified
proposer: Rex St. John (Steward), edicts E-0080 and E-0082, at the Auditor's version 003 review
proposed: 2026-09-24
charter_version: v6.9.1
log_entry_hash: f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0
---

# Amendment 027 · Auditor's version 003 findings: terminal edicts, same-origin writes

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.9.1 (`charter/history/CHARTER-v6.9.1.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.9.1`.

## Reason

run-role.sh (V.18): an interactive conversation files the Steward's messages verbatim as one edict, as Article 18.8 requires (the Auditor's finding 2). tests/test_dashboard.py (V.126): writes are sent as a browser sends them, with this server's Origin, and a write without an Origin is refused. Outside Part V (P-001 code): every dashboard write now requires this server's Origin; huddles stay open until the Steward closes them (finding 3, Article 18.7(f)); the remaining roster values are escaped; malformed query numbers no longer raise. Not fixed here (finding 1): an office with unrestricted code execution (Bash(python3:*), Bash(node:*)) can still act as the Steward on this machine; that needs a tool change the Steward decides.

## Discussion

Board thread: org/board/2026-09-24-amendment-a-0027.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.9.1 on 2026-09-24.
Amendment log entry hash: `f3d51d229f1e6f7249800ffe8c7d10cf05e2cb223cd056a88d5aa758143cf3e0` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.9.1). File generated from the verified amendment log.
