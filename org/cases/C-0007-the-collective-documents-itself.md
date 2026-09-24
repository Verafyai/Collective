---
id: C-0007
title: The Collective documents itself
date: 2026-09-24
court: steward
labels: [transparency, media, operations]
headnote: The Collective keeps a living User Guide in the public repo and publishes a weekly, human-readable, fully sourced blog post covering all of its activity, after Steward approval.
source: edict E-0032; org/board/2026-09-24-task-T-0002-user-guide-and-blog.md
cites:
  - {case: C-0001, treatment: follows}
  - {case: C-0006, treatment: follows}
review_by: 2026-12-23
holding_sha256: 01aaef9548c3ae3ccaa47745a89f6c24b7021071f401ab1189490041d55c5b51
---

## Question

How does the Collective explain itself to its Steward and to the public, week after week?

## Facts

The Steward asked for a persistent User Guide article kept current in GitHub, and for the Collective to document itself every week in a human-readable blog post covering its total activity, shown on the dashboard.

## Holding

Media maintains docs/USER-GUIDE.md, updating it in any sprint that changes how the Collective is operated and reviewing it weekly; the Chief flags it when it falls behind the Charter. Every week, after the sprint's human review, Media writes a blog post from the compiled facts (agents/bin/weekly-digest.py), covering every section of them, with each claim sourced and nothing private beyond counts. The Chief checks it against its sources, the Steward approves it (per C-0001), and it's published in blog/ and shown on the dashboard (per C-0006).

## Reasoning

A Collective that records everything should also explain itself in plain language. Compiling facts by code first ensures the post covers the whole week, not just the highlights, and sourcing every claim keeps it honest.

## Dissent

None.

## Scope

The User Guide, the weekly blog, and the dashboard's Blog panel.

## History

- 2026-09-24: filed.
- 2026-09-24: follows by C-0008.
- 2026-09-24: limits by C-0009.
