---
id: C-0004
title: Everything is a replayable event
date: 2026-09-24
court: steward
labels: [replay, safety]
headnote: Every state change is a recorded, hash-chained event; replay rebuilds from recorded outputs and never re-executes external effects.
source: CHARTER.md Part VI A-0003; org/board/2026-09-24-amendment-replayability.md
cites:
review_by: 2026-12-23
holding_sha256: 20a476c370640794b2eb900f1fcf832bc5a454eab99dabb3f6051c986e452f16
---

## Question

How is the Org's history kept so it can be rebuilt, rewound, and played back?

## Facts

Model outputs aren't reproducible, and some actions (posts) have external effects that must never repeat.

## Holding

All state changes are recorded as events in the hash-chained log. Replay applies recorded outputs rather than re-running models, and never re-executes external effects. Rewind is a Steward action that requires STOP and never deletes history. Counterfactual re-runs happen only in scratch copies.

## Reasoning

Exact reconstruction requires recorded outputs; safety requires that replay can't cause side effects. Keeping history append-only preserves accountability.

## Dissent

None.

## Scope

The entire Org, including the Steward's own edits (recorded via rec.sh).

## History

- 2026-09-24: filed.
- 2026-09-24: follows by C-0005.
- 2026-09-24: follows by C-0006.
- 2026-09-24: follows by C-0011.
