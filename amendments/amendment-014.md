---
id: A-0014
title: Amendments folder, projects, and launch
class: B
status: ratified
proposer: Rex St. John (Steward), edict E-0035
proposed: 2026-09-24
charter_version: v6.2.0
log_entry_hash: 378d4acef88527983516725a89acd109bfe9cf7e975d1249dc57e45d3c221528
---

# Amendment 014 · Amendments folder, projects, and launch

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.2.0 (`charter/history/CHARTER-v6.2.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.2.0`.

## Reason

Implements edict E-0035 (case C-0010). New Article 7.12: every amendment is amendments/amendment-NNN.md, attached to the Charter, moving proposed → deliberating (text frozen) → voting → passed/rejected → ratified; numbers match the log and never skip; ratified files must agree with the verified log (amendment.py check, run daily by the Auditor); files for A-0000 to A-0013 generated from the log. New Article 21: every prototype is a project in projects/NNN-<slug>/ (PROJECT.md, spec.md, numbered versions/version-NNN.md, append-only discussion.md), created only from an approved spec, iterated in versions released only after Auditor acceptance with honest release notes, and released as a product on the dashboard; projects/PROPOSED.md lists candidates. New Article 18.7: the dashboard's only write is human comments on projects; public comments come in via GitHub Discussions. The dashboard is project P-001 (its spec moved to projects/001-dashboard/spec.md, with a pointer left at specs/dashboard.md). New launch.sh starts the Collective: the setup phase (the first Claude Code agent with its instructions, a live event feed, and a dashboard tab that starts once v1 is built) and, after private/.setup-complete, the operating phase (every office, live feed, dashboard, approvals); herdr via herdr-plus, with a tmux fallback and a dry run. playback.py gains --follow. Offices, permissions, tool grants, setup plan, README, and User Guide updated.

## Discussion

Board thread: org/board/2026-09-25-amendment-projects.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.2.0 on 2026-09-24.
Amendment log entry hash: `378d4acef88527983516725a89acd109bfe9cf7e975d1249dc57e45d3c221528` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.2.0). File generated from the verified amendment log.
