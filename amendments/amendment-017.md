---
id: A-0017
title: Credits confirmed and plugin notes from the setup review
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0045, at setup Steps 1d and 2
proposed: 2026-09-24
charter_version: v6.2.3
log_entry_hash: c321a83b5b12fc29c55f30bbc55b542c0b0bb34abc6affe35ea8b1885dade7f4
---

# Amendment 017 · Credits confirmed and plugin notes from the setup review

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.2.3 (`charter/history/CHARTER-v6.2.3.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.2.3`.

## Reason

CREDITS.md (V.114): every "see repo" license confirmed against its repository: tsk, herdr-projects, herdr-agent-progress, herdr-radar, memex MIT; herdr-remote AGPL-3.0-or-later (commercial license also offered); herdr Apache-2.0 confirmed at herdrdev/herdr; Grok CLI and gitleaks (MIT, the redaction gate's second layer) added. docs/plugin-notes.md (V.121): the setup agent's review of each plugin at its pinned, reviewed commit: commands, config and data locations, every path off the machine, and what was deliberately not run (tsk setup and update, the Configure actions that hook the Steward's global Claude settings, herdr-remote's relay and tunnel). memex and, for now, herdr-radar are not installed (E-0045). Grok's isolation flags, gitleaks, and age documented.

## Discussion

Board thread: org/board/2026-09-24-amendment-credits-and-plugin-notes.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.2.3 on 2026-09-24.
Amendment log entry hash: `c321a83b5b12fc29c55f30bbc55b542c0b0bb34abc6affe35ea8b1885dade7f4` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.2.3). File generated from the verified amendment log.
