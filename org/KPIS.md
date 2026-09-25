# The Collective: KPI definitions

Mission-driven KPIs (edicts E-0052 and E-0053; spec:
`specs/steward-2026-09-24-mission-kpis-verafy-bench.md`). They measure whether
the Collective is **right**, **stays right**, and **gets cheaper at being
right**, not how busy it is. Computed by `agents/bin/metrics.py` from versioned
records; snapshots are written daily to `metrics/YYYY-MM-DD.json` and committed
by the Auditor. Adding or changing a KPI is a Class C amendment. Targets live
in `org/OKRS.md` and stay provisional until Sprint 1's baselines are measured.

**Every KPI can be gamed on its own,** so each one has a guardrail and is
never reported without it. A result showing Verafy's thesis fails is a valid,
publishable outcome (P3, Article 4.1; Research Library paper 08).

**North Star: `durable_claims_weekly`**, claims the Collective judged,
published with primary sources, and still standing 30 days later.

## Mission KPIs

| KPI | Definition | Source | Guardrail | Owner |
|---|---|---|---|---|
| `durable_claims_weekly` (**North Star**) | Published verdicts with ≥ 2 independent primary sources, still standing 30 days after publication, counted in the week they cross 30 days | P-003 verdict log (once it exists) | Report alongside the share of published claims rated hard | Project Manager |
| `panel_accuracy_delta` | Panel's macro-F1 on the locked test set, minus the best single model's, in points | P-002 Verafy Bench results | Only valid if `cost_ratio` ≤ the target | Prototyper |
| `cost_ratio` | Panel cost per claim ÷ best single model's cost per claim | P-002 cost logs | — | Auditor |
| `calibration_ece` | Expected calibration error of the panel's confidence (10 equal-width bins) | P-002 | Report with the reliability diagram, never alone | Prototyper |
| `reproducibility_rate` | Share of published results that the Auditor re-runs from committed artifacts (config, config hash, code commit, data manifest) and gets the same answer: the same headline numbers within the run's stated tolerance, or identical predictions where the run is deterministic. Two tiers, reported separately: **recomputed** (metrics rebuilt from the committed predictions: must match exactly) and **re-run** (the models called again on a sample: must agree within the stated tolerance; costs money, so sampled) | Auditor re-run log (`metrics/`) and P-002 `results/` | Report with the count of published results; a result that can't be re-run counts as not reproduced | Auditor |
| `verdict_survival_30d`, `verdict_survival_90d` | Share of published verdicts not reversed or materially changed at 30 and 90 days | P-003 verdict log | Report with the count published and its difficulty mix | Scribe |
| `correction_hours_median` | Median hours from evidence that a published verdict is wrong to the corrected verdict being published | Event log | — | Project Manager |
| `source_support_rate` | Share of cited sources that actually support the claim they're cited for, from a random weekly sample checked by the Lawyer (and humans when available) | Weekly audit sample | Sample of at least 20, or all if fewer | Lawyer (open question: the Lawyer has no web tools and doesn't audit; the Steward decides whether the Auditor owns it) |
| `cost_per_verified_claim` | Dollars per claim judged at or above the target accuracy | Run logs | Only compare runs at the same accuracy | Auditor |
| `fact_reuse_rate` | Share of new claims answered wholly or partly from already-verified atomic facts | P-004 fact store (future) | Reused facts must still pass the survival check | Researcher |
| `forks_first_sprint` | Outside forks that complete their first sprint; plus the median time from clone to that sprint | GitHub, plus forks' own reports | Must be independently run | Scribe |
| `steward_interventions_weekly` | Edicts, rulings, vetoes, and rejections per week, trending down | Event log | Only counts as progress with `public_incidents` = 0 | Auditor |
| `public_incidents` | Incidents about public output: anything false, spammy, or leaked | `private/incidents/`, event log | Counted, never hidden | Lawyer |

## Health metrics (on the dashboard; not goals)

These show the Collective's pulse. None of them is a target: stars measure
attention, not truth.

| Metric | Source |
|---|---|
| Public claims fact-checked | P-003 verdict log |
| GitHub commits (both repos) | git |
| Prototypes built, and versions per project | `projects/` |
| Experiments run (benchmark runs) | P-002 `results/` |
| Blog posts published | `blog/` |
| Cases filed (rulings) | `org/cases/` |
| GitHub stars and forks | GitHub |
| Research briefs written | `research/briefs/` |
| Integrity days: days on which every verifier passed | event log |
| Edict latency: days from an edict to its first outcome note | `private/edicts/` |
| Approval latency: hours from a draft entering `private/outbox/pending` to a decision | event log |
| Spend by office, per day, against caps | run transcripts, event log |
