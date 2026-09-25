---
id: A-0047
title: Observability in Weave; chats answer; agents speak first
class: B
status: ratified
proposer: Rex St. John (Steward), edicts E-0106, E-0107, E-0108, E-0112, E-0113, E-0114, E-0115, E-0116; amends entrenched Article 12 (Article 2.2)
proposed: 2026-09-25
charter_version: v6.13.0
log_entry_hash: 7dd0f13223177b498184b8efbab219e5c1fa69f67bcc65bb8ad00d36e1c82dee
---

# Amendment 047 · Observability in Weave; chats answer; agents speak first

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.13.0 (`charter/history/CHARTER-v6.13.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.13.0`.

## Reason

Article 12.10 rewritten: the OpenTelemetry bridge from the event log to Weave's Agents view (every run a turn with its model and tool calls; every roster agent registered), ops from the Collective's own scripts (spooled locally, sent by the bridge), and the pre-registered eval suite; OBS_PRIVATE_MODE=metadata (E-0108); one redaction function; the key server-side only; Weave a view, never the record. Article 18.7(d): the agents in a floor chat answer the Steward's comment at once (run-role.sh --reply). Article 18.8: in a talk the agent speaks first. Part V: new agents/observability/ (redact.py, otel_bridge.py, ops.py, weave_query.py, INVENTORY.md), agents/bin/env.sh, agents/bin/evals.sh, tests/test_observability.py; ops wired into eleven scripts; eventlog.py ignores tool environments at any depth; run-role.sh (--reply, the opener, a clean environment); shell_bridge.py (a clean environment); the herdr weave tab runs the bridge; bootstrap installs the pinned OTel and Weave packages and fetches the gitleaks rules by SHA-256; CREDITS; tests follow the live roster and never copy .venv. Removed: agents/bin/weave_sync.py and tests/test_weave.py (superseded). The dashboard's Weave panel and the evals are project code (P-001, P-005).

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0047.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.13.0 on 2026-09-25.
Amendment log entry hash: `7dd0f13223177b498184b8efbab219e5c1fa69f67bcc65bb8ad00d36e1c82dee` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.13.0). File generated from the verified amendment log.
