---
project: P-005
version: 001
title: Weave observability: traces, the Weave button, evals
status: released
date: 2026-09-25
---

# Weave Observability · version 001 · Weave observability: traces, the Weave button, evals

## Plan

P-005's spec (`specs/steward-2026-09-25-weave-observability.md`), edicts E-0107, E-0108, E-0112, E-0113 (and E-0115,
E-0116 from the Steward's use of the floor), under Charter Article 12.10 as rewritten by A-0047 (v6.13.0):
trace everything to Weave, a Weave button, an eval suite, and then a blog post.

## Changes

- **Inventory:** `agents/observability/INVENTORY.md`: every agent's runtime, launch, model, tools, and integration.
- **The bridge (3C):** `agents/observability/otel_bridge.py` exports the whole event log (backfilled from the founding
  seed) as OpenTelemetry GenAI spans to Weave's Agents view: each run an `invoke_agent` turn with a `chat` span per
  model call (model and tokens from the transcript) and an `execute_tool` span per tool call or recorded action.
  Span ids come from event hashes and the cursor only moves forward, so restarts never duplicate. Every roster agent
  (17) is registered, and events about an agent are filed under it.
- **Ops (3B):** `agents/observability/ops.py` records eleven scripts as Weave ops (`edict.new`, `spawn.propose`,
  `sprint.count_votes`, `governance.count_votes`, `auditor.verify_event_log`, `scribe.weekly_digest`, ...). An op is a
  local file append (about 0.1 s, no network); the bridge sends it.
- **Privacy:** `OBS_PRIVATE_MODE=metadata` (E-0108); one redaction function (`redact.py`: the event log's patterns,
  the gitleaks 8.30.1 rules, emails, phones); the key stays in `agents/.env` and on the server.
- **The Weave button:** a panel on the floor, /scope, and /records with Traces, Agents, and Evals tabs, fed by
  `/api/weave/status|recent|agents|evals`; View in Weave on every agent's profile; a W glyph over an agent when its
  run is exported; deep links even when Weave is unreachable.
- **Evals:** `evals/` (14 evals, seed datasets with locked test splits, pre-registered in `evals/REGISTRY.md`),
  `agents/bin/evals.sh`.
- **Also:** agents answer the Steward in floor chats at once (`run-role.sh --reply`), a talk starts with the agent
  greeting him, and tool environments are never swept into the event log.
- **Not used: native integrations (3A).** The Weave Claude Code plugin and Pi extension send full content with no
  redaction, which metadata mode rules out; the bridge covers every agent from its recorded transcript instead.

## First eval results (run 1, 2026-09-25; model spend $4.24, or $4.44 with the E3 and E9 reruns)

| # | Eval | Headline | Result |
|---|---|---|---|
| E1 | Verdict accuracy | panel accuracy 1.00 (n=17); panel minus best single 0.00, CI [0.00, 0.00] | pass |
| E2 | Calibration | Brier 0.001; ECE 0.026 | pass |
| E3 | Citation grounding | first run 0.57 (**fail**, the judge saw abstracts only); rerun with full sources 1.00 | pass |
| E4 | Charter compliance | violation recall 1.00; agreement 1.00 (n=10) | pass |
| E5 | Tamper detection | 14 of 14 tampered logs caught; 0 of 8 clean flagged | pass |
| E6 | Digest faithfulness | 0 unsupported citations; coverage 0.90 (n=2 weeks) | pass |
| E7 | Edict follow-through | first run 1.00 was a scorer bug (commits that only mention an edict counted); a preview with the corrected scorer gave 0.84 (not recorded as a run); the recorded rerun, after the missing outcomes were noted, is 0.98 | pass |
| E8 | Social policy | 0.50 (**fail**): every adversarial prompt refused, but Social also declined half the ordinary requests | fail |
| E9 | Research faithfulness | first run 0.57 (**fail**, abstracts only); rerun 0.89, key-claim recall 0.53 | pass |
| E10 | Reopen precision | F1 0.86 (precision 1.00, recall 0.75) | pass |
| E11 | Governance determinism | 12 of 12 identical on replay | pass |
| E12 | Format compliance | 0.52 (**fail**): every header is valid; most posts open with a summary line over 25 words | fail |
| E13 | Secret leakage | 0 leaks; 7 of 7 canaries caught | pass |
| E14 | Idea quality | 1 of 1 (n=1, seed) | pass |

## Release notes

Open the floor's **Weave** button to see every agent's recent runs, how much each has done, and the eval scoreboard,
with links to W&B Weave. Every agent appears in Weave's Agents view, with each run's model calls and tool calls, and
no private text leaves the machine.

**Known limits:**
- A sprint meeting hasn't happened yet (Sprint 0's deliberation waits on the Steward's governance keys), so no
  meeting conversation or sealed-ballot spans exist yet; the bridge will show one when it runs.
- The datasets are seeds (1 to 113 rows); E14 has one row and E6 two. Growing them is standing work for the
  Researcher and Ideas offices.
- Per-call times inside a run are interpolated (transcripts don't carry them); run start and end times are real.
- The Weave deep links open the project's Agents, Traces, and Evaluations pages, not one specific trace.
- Two evals fail (E8, E12); both are published, not hidden.

## Links

- Edicts E-0106 to E-0108, E-0112 to E-0116; amendment A-0047 (Charter v6.13.0); spec and INVENTORY above.

