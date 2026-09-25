---
id: C-0011
title: P-002 Verafy Bench is created under the Lawyer's conditions
date: 2026-09-24
court: officer
labels: [prototyping, budget, operations]
headnote: Project P-002 Verafy Bench is created from the Steward's E-0052 spec under the Lawyer's six conditions; its baseline run waits for a Sprint 0 vote, Steward sign-off, and a budgeted #decision @rex, and Panel Illusion joins it as a work item, not a separate project.
source: edicts E-0052, E-0053; org/board/2026-09-24-decision-create-p-002-verafy-bench.md; Lawyer #opinion in org/board/2026-09-24-proposal-mission-kpis-verafy-bench.md; specs/steward-2026-09-24-mission-kpis-verafy-bench.md; ideas/panel-illusion.md
cites:
  - {case: C-0001, treatment: follows}
  - {case: C-0003, treatment: follows}
  - {case: C-0004, treatment: follows}
  - {case: C-0006, treatment: follows}
  - {case: C-0009, treatment: follows}
  - {case: C-0010, treatment: follows}
review_by: 2026-12-23
holding_sha256: 7b9c9a034bacf3b5e4727e2512ae717f6360bb95109c016069d47d38b119f83f
---

## Question

How is the Steward's Verafy Bench spec (E-0052, with E-0053) turned into a project, and what must happen before any of it spends money?

## Facts

Edict E-0052 directed a benchmark project, Verafy Bench, from the spec in specs/steward-2026-09-24-mission-kpis-verafy-bench.md, and E-0053 added a reproducibility KPI. The Lawyer's #opinion advised proceeding with changes (a)–(f): create the project by a PM #decision; define reproducibility_rate as recomputation from committed artifacts; file the AVeriTeC license (CC BY-NC 4.0) and dataset-card terms; publish claim IDs rather than claim text, fetch data by script with a SHA-256 manifest, and record model providers' terms on publishing benchmark results; keep public output aggregate-only for political or named-person claims; and move source_support_rate to the Auditor or amend OFFICERS.md with a tool grant. The Ideas office had separately proposed Panel Illusion (ideas/panel-illusion.md), which the Lawyer advised be a P-002 work item under the one-active-prototype WIP limit. The Project Manager decided on the board on 2026-09-24.

## Holding

P-002 Verafy Bench is created from the E-0052 spec, owned by the Prototyper, and bound by the Lawyer's conditions (a)–(f). reproducibility_rate means recomputing metrics from committed predictions, config, and split hash; a paid re-call of the models would be a separate metric with a tolerance band and a budget. Until ownership of source_support_rate is settled it is unowned and shown as "not yet measurable". Version 001 (the baseline run) is not approved to run by this decision: it is a proposed Sprint 0 item and runs only after the sprint vote, Steward sign-off, and a #decision @rex that states a spend cap. Panel Illusion is a P-002 work item (spec §4.5, Agreement), not a separate project, scheduled through Sprint 0 and not built before then; the Ising follow-on is out of scope.

## Reasoning

The edict outranks a sprint item or a PM decision (Art. 9.1), and an operational direction becomes a board #decision (Art. 15.4), which is the channel the Lawyer advised. Projects are created from a spec and iterated in versions (C-0010). Every Bench system cites the Research Library (C-0003). Model outputs can't be reproduced exactly, so reproducibility means recomputation (C-0004). Results go through the outbox and nothing is posted without approval (C-0001 as limited by C-0009). The KPI panel extends P-001 without changing its mandate (C-0006). Folding Panel Illusion into P-002 avoids building the same metric twice and keeps the active-prototype slot free.

## Dissent

None recorded.

## Scope

Project P-002 Verafy Bench and its work items, including Panel Illusion. Questions left to the Steward: whether Verafy's use of AVeriTeC is non-commercial, how political and named-person claims are handled before v003 or P-003, and who owns source_support_rate.

## History

- 2026-09-24: filed.
