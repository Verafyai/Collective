---
id: C-0006
title: The Collective Dashboard is mandated
date: 2026-09-24
court: steward
labels: [operations, tooling, transparency]
headnote: The Collective builds and maintains a local, read-only, fully versioned observability dashboard per specs/dashboard.md, as task T-0001.
source: edict E-0031; org/board/2026-09-24-task-T-0001-dashboard.md; specs/dashboard.md
cites:
  - {case: C-0004, treatment: follows}
  - {case: C-0002, treatment: follows}
review_by: 2026-12-23
holding_sha256: c3727a3d2ee0b11ef6b81159bc0608ad5b3cc4fba612e593b4fcc2885c364efb
---

## Question

How does the Steward observe and monitor the Collective?

## Facts

The Steward asked for a comprehensive local dashboard covering mission, Charter, progress, KPIs and OKRs, current and past sprints, decisions with evidence, a calendar, and a live stream of agents and debates, all versioned in git.

## Holding

The Collective builds the dashboard specified in specs/dashboard.md as task T-0001: owner Prototyper, design review by Media, acceptance by the Chief. The dashboard is read-only, local by default, derives every panel from versioned records, shows what commit and event each view reflects, and can render any past point in time. Its later build steps are sprint items.

## Reasoning

Observability follows from replayability (C-0004): if everything is recorded, the Steward should be able to see it, live and as of any moment. Transparency (C-0002) favors a public mode that shows everything except private material.

## Dissent

None.

## Scope

The dashboard and its metrics. Changes to panels or KPIs follow the normal channels (sprint items; Class C amendments for KPI definitions).

## History

- 2026-09-24: filed.
- 2026-09-24: follows by C-0007.
- 2026-09-24: limits by C-0009.
- 2026-09-24: follows by C-0010.
- 2026-09-24: follows by C-0011.
