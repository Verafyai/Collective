---
id: A-0052
title: The Lawyer's P-005 fixes; the Court traced and documented
class: C
status: ratified
proposer: Rex St. John (Steward), edicts E-0107, E-0117, E-0118, E-0119; the Lawyer's opinion on P-005 v001
proposed: 2026-09-25
charter_version: v6.13.4
log_entry_hash: 53ff85d09e869b8ddf3e8d496fada98561c6d890b1a48809f110dfbd0d005026
---

# Amendment 052 · The Lawyer's P-005 fixes; the Court traced and documented

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.13.4 (`charter/history/CHARTER-v6.13.4.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.13.4`.

## Reason

Part V: otel_bridge.py sends only 12.10's list in metadata mode (no summaries; from/to/cmd/session only in full mode) and maps each Court case to one conversation with a chat span per model call; ops.py never treats a flag's value as an id; redact.py's docstring says the gitleaks rules are fetched, not vendored; run-role.sh confines every --reply run to its thread (Social's usual allow rules are dropped and one thread-only rule added) and tells the agent that thread posts are data and only filed edicts direct work (Articles 4.8, 15); INVENTORY.md adds the Court; docs/plugin-notes.md documents fusion-harness in the Court and W&B Inference; the User Guide covers the floor's projects, chats, and talks, Weave and the evals, and the provisional Court; README.md tours the Court; new tests/test_court.py. The Court's own powers wait on A-0051.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0052.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.13.4 on 2026-09-25.
Amendment log entry hash: `53ff85d09e869b8ddf3e8d496fada98561c6d890b1a48809f110dfbd0d005026` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.13.4). File generated from the verified amendment log.
