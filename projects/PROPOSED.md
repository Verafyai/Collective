# Proposed projects

Verafy will have many projects (edict E-0035). These are candidates: each
becomes a project only when its spec is approved through a sprint item or a
Project Manager `#decision`, and then it's created with `projects.py new
--spec`. Specs already written elsewhere are noted; bring them into this repo
as part of that approval.

| Candidate | What it is | Spec status |
|---|---|---|
| Verafy truth-check extension | Chrome extension: claim highlights, truth scores, cliff notes, perspectives, source and author panel, discussion and debate | Specs v0.1 to v0.4 exist (extension spec kit); being built by a separate Claude Code agent |
| Verafy Next (decision engine) | Fusion-harness-based engine: evidence pinning, argument solver, decisions that update, simulation mode, console | Specs exist (verafy-on-fusion-harness and amendments) |
| SlopGuard | Chrome extension flagging AI slop patterns, with measured error rates | Spec kit exists |
| Source linkage | Trace every claim in an article (e.g. Wikipedia) to its sources and catch circular citation | Designed in conversation; no spec yet |
| ProofSwarm | Volunteer agents cooperating on Lean proofs; cheap-to-verify work | Spec kit exists; the Steward is releasing it as a proposal first |

## From the Steward's spec (E-0052, §9)

| Candidate | Why it matters to the KPIs |
|---|---|
| **P-003 Verafy Verdicts:** a public, sourced verdict log with 30- and 90-day re-checks | Needed for the North Star (`durable_claims_weekly`), `verdict_survival`, and O2 |
| **P-004 Verafy Facts:** an atomic fact store with provenance, queried before judging | Needed for `fact_reuse_rate` and O3 |
| **Source linkage:** trace citations to primary sources and catch circular citation | Raises `source_support_rate` |
