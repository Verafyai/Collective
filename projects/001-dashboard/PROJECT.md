---
id: P-001
name: The Collective Dashboard
owner: prototyper
status: released
created: 2026-09-24
code: dashboard/
current_version: 002
---

# The Collective Dashboard

Created from [spec.md](spec.md). Versions are in [versions/](versions/); the ongoing record of
updates, decisions, and input is in [discussion.md](discussion.md).

## Roadmap

Each step of the spec's build order (§7) becomes the next numbered version,
planned in a sprint and added with `projects.py version`:

| Version | Scope (spec §7) | Status |
|---|---|---|
| 001 | Skeleton, header, Mission, Charter, Versioning, time travel | released 2026-09-24 |
| 002 | The floor, classes, bios, spawning, and chats (replaced the original 002 scope, per E-0060) | released 2026-09-25 |
| 003 | KPIs and OKRs (`metrics.py`, daily snapshots); Progress | to plan |
| 004 | Calendar with `.ics` export; Blog and User Guide | to plan |
| 005 | Live stream: agent columns, debate view, replay; Discussion | to plan |
| 006 | Public mode; Media design review; Auditor acceptance | to plan |
| 007 | Public release on GitHub Pages (Steward approval) | to plan |

The code lives in `dashboard/`. Run it with `agents/bin/dashboard.sh`.
