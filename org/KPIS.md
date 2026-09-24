# The Collective: KPI definitions

Computed by `agents/bin/metrics.py` from versioned records (to be built under
T-0001, step 3). Snapshots are written daily to `metrics/YYYY-MM-DD.json` and
committed by the Auditor. Adding or changing a KPI is a Class C amendment.

| KPI | Formula | Source | Target | Owner |
|---|---|---|---|---|
| `briefs_written` | Count of `research/briefs/*.md` | research/ | 20 / quarter | Researcher |
| `proposals_open` | Ideas proposals without an outcome | ideas/, board | ≤ 3 | Ideas |
| `prototypes_shipped` | Prototypes marked done | prototypes/, board | 8 / quarter | Prototyper |
| `demos_published` | `effect.posted` events with a media package | event log | 8 / quarter | Media, Social |
| `posts_published` | `effect.posted` events | event log | ≤ 8/day cap respected | Social |
| `external_adoptions` | Forks, stars, or citations recorded by the Researcher | research/adoptions.md | 1 / quarter | Researcher |
| `sprints_closed` | Sprints with phase `closed` | sprints/ | 12 / quarter | Project Manager |
| `median_sprint_grade` | Median item grade across closed sprints | sprints/*/postmortem | ≥ B | Project Manager |
| `precedent_survival_rate` | From `case.py stats` | org/cases/ | ≥ 80% | Scribe |
| `public_incidents` | Incidents about public output | private/incidents/, event log | 0 | Lawyer |
| `integrity_days` | Days on which all verifiers passed | event log (`ledger.backup`, verify results) | 100% | Auditor |
| `edict_latency_days` | Days from edict issued to first outcome note | private/edicts/ | ≤ 7 | Project Manager |
| `approval_latency_hours` | Hours from a draft entering `private/outbox/pending` to approval or rejection | event log | ≤ 48 | Steward |
| `spend_by_role` | Model spend per role per day, from run transcripts | event log | within caps | Auditor |
