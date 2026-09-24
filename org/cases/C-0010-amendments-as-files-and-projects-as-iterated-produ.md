---
id: C-0010
title: Amendments as files, and projects as iterated products
date: 2026-09-24
court: steward
labels: [governance, prototyping, operations]
headnote: Every amendment is a numbered file that attaches to the Charter and is voted on; every prototype is a project created from a spec, iterated in numbered versions with an ongoing discussion, and released as a product on the dashboard, which is project P-001.
source: edict E-0035; org/board/2026-09-25-amendment-projects.md; amendments/; projects/
cites:
  - {case: C-0006, treatment: follows}
  - {case: C-0009, treatment: follows}
review_by: 2026-12-23
holding_sha256: 1ca6e6c3eea3441918ba5c4cf6aa48b460aeaea451d2fd38cee9485a39259a2d
---

## Question

How are changes to the Charter and the Collective's products organized so they can be followed over time?

## Facts

Amendments existed only as entries in the Charter's log, and prototypes had no grouping of spec, versions, and discussion. The Steward asked for an amendments folder with numbered files that attach to the Charter and are voted on, and a projects folder where each project is created from a spec, iterated in numbered versions, carries a discussion, and is released as a product humans can see and comment on, starting with the dashboard.

## Holding

Every amendment is amendments/amendment-NNN.md, moving from proposal through deliberation (which freezes its text) and the vote to ratification; its number matches the log, numbers never skip, and ratified files must agree with the verified log. Every prototype is a project in projects/NNN-<slug>/ with PROJECT.md, spec.md, numbered versions, and an append-only discussion recording updates, decisions, and input from agents and humans. A project starts only from an approved spec, each version is released only after the Auditor accepts it with honest release notes, and the current version is released as a product on the dashboard, whose only write is human comments on projects. The dashboard is project P-001 (per C-0006), built and released by the Prototyper under the offices of C-0009.

## Reasoning

Changes and products are easier to follow, challenge, and improve when each has its own record with a clear lifecycle. Keeping amendment files consistent with the hash-chained log means the readable record can't drift from the verified one.

## Dissent

None.

## Scope

All amendments, all projects, and the dashboard's Projects panel.

## History

- 2026-09-24: filed.
