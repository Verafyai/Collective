# Weave observability for the Collective (P-005)

The Steward's spec (edicts E-0107, E-0108, E-0112), from his handoff of 2026-09-25. It's
kept as given, except for the notes at the end on where it had to differ.

**What:** make every agent in the Collective (and any other agent system running in this
herdr workspace) fully observable in W&B Weave:

1. Trace everything: agent runs, model calls, tool calls, governance, and the event log.
2. Add a **Weave** button to the dashboard.
3. Build a suite of evaluations.
4. Publish a blog post about it to the public repo.

**Weave project:** entity `rexstjohn-verafy`, project `The Collective`
(`https://wandb.ai/rexstjohn-verafy/The%20Collective/weave`), initialized as
`"rexstjohn-verafy/The Collective"`.

Do this through the Collective's own process: an edict, a project, the Lawyer's review,
the Auditor's acceptance, a release, and a record.

## 0. Ground rules

- **The key never enters the repo.** `WANDB_API_KEY` comes from the environment or the
  git-ignored `agents/.env`, loaded by `agents/bin/env.sh`. gitleaks passes on every commit.
- **The browser never sees the key.** All Weave calls from the dashboard go through
  `dashboard/server.py`.
- **Tracing never breaks an agent.** If W&B is unreachable or the key is missing, agents
  run exactly as before: one warning, then continue. Exports are wrapped and batched in
  the background.
- **Redact before export.** One function, `agents/observability/redact.py`, applied to
  every span attribute and every op input and output: API keys, tokens, email addresses,
  phone numbers, and anything matching the gitleaks rules.
- **Don't double-trace.** Where a native integration already traces a run, the bridge
  emits only governance-level spans for that run, linked by `gen_ai.conversation.id`.

## 1. The edict and the project

The Steward's words are edict E-0107. The project is **P-005 Weave Observability**, created
from this spec, cross-linked with P-002 (Verafy Bench), which the evals build on.

## 2. Inventory

`agents/observability/INVENTORY.md`: one row per agent in `agents/roster.json` and per
class in `agents/classes.json`, plus any other agent system in the workspace
(fusion-harness deliberations, Social on Grok, herdr panes): runtime, how it's launched,
models, tools, and the integration chosen. Unknown runtimes are traced through the bridge.

## 3. Tracing, in three layers

- **3A. Native integrations** (the Weave Claude Code plugin, the Pi extension, the Claude
  Agent SDK's autopatching) where available. ⏸ Stop for the Steward if moving a runner to
  the Agent SDK would change any agent's behavior, permissions, or cost.
- **3B. `@weave.op`** on the Collective's own machinery: edicts, spawning and membership
  motions, the sprint lifecycle (proposals, opinions, deliberation, the vote counter,
  sign-off, grading), the Auditor's integrity checks and hash-chain verification, the
  weekly digest, and board posting. Ops are named like `sprint.count_votes` and
  `auditor.verify_chain`.
- **3C. The OpenTelemetry bridge** (`agents/observability/otel_bridge.py`): reads the
  hash-chained event log (Article 12) and exports OTLP/protobuf spans to
  `https://trace.wandb.ai/agents/otel/v1/traces`, with `wandb.entity` and `wandb.project`
  as resource attributes. One agent run is an `invoke_agent` root span; each model call a
  `chat` child; each tool use or action an `execute_tool` child. Every span carries
  `gen_ai.agent.name` (the roster key) and `gen_ai.conversation.id` (the sprint and meeting,
  the edict, or `standup-<date>`), the GenAI model, token, and tool attributes where known,
  and `collective.event_hash`, `prev_hash`, `edict`, `case`, `project`, `sprint`, `office`,
  `votes`, and `room`. `follow` tails the log in its own herdr pane; `backfill` exports the
  whole history once; the last exported hash is kept in `agents/observability/.bridge_state`
  (git-ignored) so a restart never duplicates spans.
- ⏸ Before the first export of anything from CollectivePrivate, ask the Steward:
  `OBS_PRIVATE_MODE=full|metadata|off`, default `metadata`. (He chose **metadata**, E-0108.)

## 4. The Weave button

- `GET /api/weave/status`, `/api/weave/recent?agent=&limit=`, `/api/weave/evals`:
  read-only, 127.0.0.1 only, rate-limited, cached 30 s, the key on the server only, and
  `"live": false` with deep links when Weave is unreachable.
- A **Weave** button on the floor's HUD opening a slide-over panel with **Traces**,
  **Agents**, and **Evals** tabs; **View in Weave** on every agent's profile; a small
  Weave glyph over an agent when its run is exported; the same button on /scope and
  /records, where a record links to its event's trace. Light and dark themes.
- `tests/test_dashboard.py` covers the routes, the panel, the fallback, and that no
  response body ever contains the key.

## 5. Evaluations

`evals/`: each eval is a `weave.Evaluation` with a versioned `weave.Dataset` and
`@weave.op` scorers, and each target calls the real agent code path. Scientific rules
(from P-002): locked train and test splits, with the test split's hash recorded in the
event log before its first run; metrics and thresholds pre-registered in
`evals/REGISTRY.md`; bootstrap 95% confidence intervals on headline metrics; negative
results published; deterministic scorers preferred, and any LLM judge from a different
model family than the agent scored; seed datasets labeled `seed`.

| # | Eval | Target |
|---|---|---|
| E1 | Verdict accuracy | judge panel vs. each single model |
| E2 | Calibration | truth scores |
| E3 | Citation grounding | verdicts and research summaries |
| E4 | Charter compliance | Lawyer |
| E5 | Tamper detection | Auditor |
| E6 | Minutes and blog faithfulness | Scribe / weekly-digest |
| E7 | Edict follow-through | the whole Collective |
| E8 | Social policy | Social |
| E9 | Research summary faithfulness | Researcher |
| E10 | Reopen precision | Sentinel |
| E11 | Governance determinism | the vote counter |
| E12 | Format compliance | all offices |
| E13 | Secret leakage | all outputs and exported spans |
| E14 | Idea quality | Ideas |

`agents/bin/evals.sh [--suite all|E1,E4,...]` runs them; results go to the Weave Evals tab
and the event log. The full suite runs once per sprint as a standing item, and an eval below
its threshold opens a board thread.

## 6. Acceptance (the Auditor checks)

1. All nine offices, plus at least one spawned class, in the Agents view with real runs.
2. One full sprint meeting as a single conversation.
3. The backfill exported the full log; a restart duplicates nothing.
4. Killing network access to W&B leaves every agent running normally.
5. The Weave button works on the floor, /scope, and /records, including the fallback.
6. All 14 evals exist with at least one run each, pre-registered in `evals/REGISTRY.md`.
7. `tests/test_dashboard.py` and `tests/test_observability.py` pass.
8. gitleaks is clean; no key in the repo, any trace, or any response body; E13 passes.

The Lawyer reviews the project, with attention to privacy and public traceability; the
Auditor accepts it; then P-005 is released and recorded.

## 7. The blog post

After release, the Scribe writes `blog/<date>-weave-observability.md`, *Making an
Autonomous Organization Observable: Tracing the Collective with W&B Weave*: why
observability matters for an autonomous organization; the three layers; governance as
traces; the Weave button; the eval suite with its first real results, failures included;
what's next; and credit to W&B Weave and the OTel GenAI semantic conventions. Every claim
traceable to a record, commit, or trace; it passes E6 and E13; no private content, key, or
internal URL (the Weave project is linked only if it's public). After the Lawyer's and
the Auditor's checks it's committed and pushed to Verafyai/Collective and recorded.

## Notes: where the work had to differ

- **P-005, not P-003:** P-003 (Get a job) and P-004 (Pizza) were created first.
- **3A isn't installed.** W&B's own docs say the Claude Code plugin and the Pi extension send
  full prompts, responses, file contents, and shell output, with no redaction. That
  contradicts the Steward's metadata choice (E-0108), and the plugin would trace every Claude
  Code session on the machine. The bridge reads the agents' recorded transcripts instead
  (model, tokens, and tool names per call), so every agent appears in the Agents view with
  no change to how it runs, and no Agent SDK migration is needed.
- **Ops are spooled.** An op is appended to a local file and sent by the bridge's process,
  so it costs a script about 0.1 s and never a network call.
- **gitleaks `-q`:** gitleaks 8.30.1 has no `-q` flag (A-0016); scans use `--no-banner`.
- **The gitleaks rules** that redact.py uses are fetched by bootstrap, pinned by SHA-256,
  not committed: the file is full of sample secrets that the public commit gate rejects.
