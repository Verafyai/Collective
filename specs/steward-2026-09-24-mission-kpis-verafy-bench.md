# Spec: mission-driven KPIs and OKRs, and P-002 Verafy Bench

<!-- Given by the Steward on 2026-09-24; recorded as edict E-0052. Kept verbatim. -->

**For:** the Claude Code agent working in the Collective's folder.
**From:** the Steward (Rex St. John).
**Status:** direction from the Steward. Record it as an edict before acting
(Charter Article 15).

---

## 0. What to do with this spec, in order

1. **Record the edict.** Use the Steward's words:
   *"These don't feel so toothsome. I am looking for mission-driven KPIs,
   like the Collective needs to be solving something numerically. Give
   Claude a spec to chew on for that."*
   Title: "Mission-driven KPIs and OKRs; P-002 Verafy Bench". Restatement:
   §1 of this spec.
2. **If setup is still in progress,** finish the current setup step first.
   Then treat this spec as the main input to **Sprint 0** (theme: "What is
   the best course of action for the Collective right now?"). The answer
   this spec proposes: start measuring the truth.
3. **The Lawyer** posts an `#opinion` on this spec: its compliance with
   Article 0 (P1, P4, P5) and Article 18.
4. **Replace the draft OKRs** in `org/OKRS.md` with §3. They stay marked
   DRAFT until the Steward confirms them by edict, and their targets stay
   provisional until the baselines in §5 are measured.
5. **Rewrite `org/KPIS.md`** per §2, as a Steward-directed Class C
   amendment: `python3 agents/bin/amendment.py new --title "Mission-driven
   KPIs" --class C --proposer steward --file <text>`. Apply it through the
   normal steps, then `amendment.py sync` and `check`.
6. **Create the project:** write §4 onward to a spec file, then
   `python3 agents/bin/projects.py new --name "Verafy Bench" --slug
   verafy-bench --owner prototyper --spec <that file>`.
7. **Plan version 001** (the baseline run; §6), and propose it as a Sprint
   0 item for the Prototyper, with the Researcher choosing the dataset.
8. **Add the future projects in §9** to `projects/PROPOSED.md`.
9. **Stop and show the Steward:**
   - the Lawyer's opinion;
   - the new `OKRS.md` and `KPIS.md`;
   - the P-002 folder;
   - the Sprint 0 items;
   - **the dataset license findings, the estimated cost of the baseline
     run, and the budget being requested** (§7). Nothing that spends money
     runs before the Steward approves it.

---

## 1. The problem the Collective is solving, as a number

Verafy's thesis: **a panel of AI judges, reasoning over evidence and
revisiting its decisions, gets closer to the truth than one confident model,
at a cost worth paying.**

That's testable. The Collective's job is to test it honestly, publish the
results, and improve them. The earlier draft KPIs (commits, posts, stars)
measured activity. The new ones measure whether the Collective is **right**,
**stays right**, and **gets cheaper at being right**.

**North Star: durable verified claims per week.** Claims the Collective
judged, published with primary sources, and still standing 30 days later.

Two cautions, written into the KPIs:
- **Every KPI can be gamed on its own,** so each one comes with a guardrail.
  Accuracy is paired with cost, and survival with volume and difficulty.
- **The research the Collective itself cites** (Research Library paper 08,
  Smit et al.) finds that multi-agent debate often does *not* beat cheaper
  methods. A result showing the thesis fails is a valid, publishable
  outcome. The Collective reports what it finds, not what it hoped for
  (P3, Article 4.1).

---

## 2. KPI definitions (new `org/KPIS.md`)

### 2.1 Mission KPIs

| KPI | Definition | Source | Guardrail | Owner |
|---|---|---|---|---|
| `durable_claims_weekly` (**North Star**) | Published verdicts with ≥ 2 independent primary sources, still standing 30 days after publication, counted in the week they cross 30 days | P-003 verdict log (once it exists) | Report alongside the share of published claims rated hard (§4.5) | Project Manager |
| `panel_accuracy_delta` | Panel's macro-F1 on the locked test set, minus the best single model's, in points | Verafy Bench results | Only valid if `cost_ratio` ≤ the target | Prototyper |
| `cost_ratio` | Panel cost per claim ÷ best single model's cost per claim | Verafy Bench cost logs | — | Auditor |
| `calibration_ece` | Expected calibration error of the panel's confidence (10 equal-width bins) | Verafy Bench | Report with the reliability diagram, never alone | Prototyper |
| `verdict_survival_30d`, `verdict_survival_90d` | Share of published verdicts not reversed or materially changed at 30 and 90 days | P-003 verdict log | Report with the count published and its difficulty mix | Scribe |
| `correction_hours_median` | Median hours from evidence that a published verdict is wrong to the corrected verdict being published | Event log | — | Project Manager |
| `source_support_rate` | Share of cited sources that actually support the claim they're cited for, from a random weekly sample checked by the Lawyer (and humans when available) | Weekly audit sample | Sample of at least 20, or all if fewer | Lawyer |
| `cost_per_verified_claim` | Dollars per claim judged at or above the target accuracy | Run logs | Only compare runs at the same accuracy | Auditor |
| `fact_reuse_rate` | Share of new claims answered wholly or partly from already-verified atomic facts | P-004 fact store (future) | Reused facts must still pass the survival check | Researcher |
| `forks_first_sprint` | Outside forks that complete their first sprint; plus the median time from clone to that sprint | GitHub, plus forks' own reports | Must be independently run | Scribe |
| `steward_interventions_weekly` | Edicts, rulings, vetoes, and rejections per week, trending down | Event log | Only counts as progress with `public_incidents` = 0 | Auditor |

### 2.2 Health metrics (tracked on the dashboard; not goals)

- Public claims fact-checked;
- GitHub commits (both repos);
- prototypes built and versions per project;
- experiments run (benchmark runs);
- blog posts published;
- cases filed (rulings);
- GitHub stars and forks;
- plus the existing integrity and spend metrics.

These show the Collective's pulse. None of them is a target. Stars measure
attention, not truth.

---

## 3. Q4 2026 OKRs (new `org/OKRS.md`, DRAFT)

Targets in brackets are **provisional until Sprint 1's baselines** are
measured. The Steward confirms or revises them by edict.

**O1. Prove, or disprove, that panels beat a single judge on real claims.**
- KR1.1: baseline measured: the best single model on the locked test set
  (§5), with a published report.
- KR1.2: panel with debate reaches `panel_accuracy_delta` ≥ [+5] points at
  `cost_ratio` ≤ [2.0], **or** the Collective publishes an honest negative
  result explaining why not.
- KR1.3: `calibration_ece` ≤ [0.05].

**O2. Make verdicts durable** (starts when P-003 publishes verdicts).
- KR2.1: `verdict_survival_30d` ≥ [90%].
- KR2.2: `correction_hours_median` < [48].
- KR2.3: every published verdict cites ≥ 2 independent primary sources, and
  `source_support_rate` ≥ [95%].

**O3. Verify once, reuse everywhere** (starts when P-004 exists).
- KR3.1: `fact_reuse_rate` ≥ [40%].
- KR3.2: `cost_per_verified_claim` down [50%] from the Sprint 1 baseline.

**O4. Prove the seed.**
- KR4.1: `forks_first_sprint` ≥ 1, with clone-to-first-sprint under [60
  minutes].
- KR4.2: `steward_interventions_weekly` halved, with `public_incidents` = 0.

---

## 4. P-002 Verafy Bench: what it is

An evaluation harness that measures, reproducibly and cheaply, how well
different ways of judging claims actually work. It is the instrument behind
O1, and the thing that makes every later accuracy claim honest.

### 4.1 Questions it answers

1. How accurate is the **best single model** at judging real-world claims,
   given evidence?
2. Does a **panel** (several models, independent verdicts, aggregated) beat
   it? At what cost?
3. Does **debate** among the panel beat plain aggregation? (The claim the
   Research Library is most skeptical of.)
4. Which **aggregation** works best? Majority, confidence-weighted,
   dependence-aware (the Ising approach), or robust (the geometric median in
   RoPoLL)?
5. Are the panel's confidences **calibrated**?

### 4.2 Two tracks

- **Track J (judging), built first:** the claim **plus the evidence the
  benchmark provides**. This isolates judging quality from search quality.
- **Track E (end-to-end), later:** the claim only; the system retrieves its
  own evidence. This measures the real product but mixes two problems.
  Version 004 or later.

### 4.3 Datasets

The **Researcher** chooses, and the **Lawyer** clears the license (P4).
Check each candidate's current availability, size, labels, and license
before choosing; don't assume.
- **Primary candidate: AVeriTeC.** Real-world claims from fact-checking
  organizations, with evidence and verdict labels. Verify its current
  license and terms.
- **Secondary sanity check:** FEVER or a similar, well-understood set, to
  compare with published numbers.
- **The Collective's live set:** recent claims, published after the models'
  training cutoffs, with verdicts from reputable fact-checkers. This guards
  against the models having memorized the benchmark. Built from version 003
  on.

**Data handling:** if a dataset's license forbids redistribution, don't
commit it. Store a fetch script and SHA-256 manifest (as
`research/library/fetch.sh` does), and keep the data in the private repo
or local cache.

### 4.4 Systems under test (each a config file)

| ID | System | Why it's here |
|---|---|---|
| S1 | Each single model, one call | Baselines; the best becomes the reference |
| S2 | Best single model with self-consistency (k samples, majority) | The cheap baseline paper 08 says debate must beat |
| S3 | Panel of 3–5 models from different families, independent verdicts, majority vote | The simplest panel |
| S4 | S3 with confidence-weighted, Ising, and geometric-median aggregation | Aggregation question (Research Library and the Amazon papers) |
| S5 | S3 plus debate: initial positions, 2 rounds, final sealed verdicts | The debate question (library papers 02, 03, 07) |
| S6 | S5 with the Verafy argument solver: arguments with cited evidence, attacks, and a grounded-semantics verdict | Verafy's own method |

### 4.5 Metrics per run

- **Accuracy and macro-F1** over the benchmark's labels (macro-F1 because
  labels are imbalanced), with a per-label confusion matrix.
- **Calibration:** ECE (10 bins), Brier score, and a reliability diagram.
- **Cost:** dollars and tokens per claim, by model, from real API usage.
- **Latency:** median and p90 seconds per claim.
- **Agreement:** pairwise judge agreement and error correlation. High
  correlation means the panel is less independent than it looks.
- **Difficulty:** each claim tagged easy, medium, or hard by how many single
  models got it right. Results are reported per band.
- **Uncertainty:** 95% bootstrap confidence intervals on every headline
  number. A difference inside the interval is not a win.

### 4.6 Scientific hygiene (non-negotiable)

1. **Split once, lock the test set.**
   - dev: for building and tuning;
   - test: run only at the end of a sprint.

   Record the split with a SHA-256 of the claim IDs.
2. **Pre-register every test run.** Commit the config (models, prompts,
   aggregation, sample sizes) and its hash **before** the test run. Results
   cite that hash. A result without a pre-registered config doesn't count.
3. **Never tune on test.** Using the test set to pick prompts or
   configurations invalidates the result; start a new split if that
   happens, and say so.
4. **Report every run,** including failures and negative results. Filing a
   disappointing result in a drawer is a violation of Article 4.1.
5. **Contamination caveat:** state plainly that models may have seen public
   benchmarks in training, and weigh the live set more heavily as it grows.
6. **Credit** every dataset, paper, and method used (P4), in the results
   and in `CREDITS.md`.

### 4.7 Layout

```
projects/002-verafy-bench/
  PROJECT.md  spec.md  discussion.md  versions/
  src/
    bench.py          # run a config on a split; resumable; never touches test without a pre-registered config hash
    adapters/         # one small adapter per model provider, keys from agents/.env
    aggregate.py      # majority, weighted, Ising, geometric median
    debate.py         # S5 rounds
    solver.py         # S6: port of the argument solver (grounded semantics)
    metrics.py        # accuracy, macro-F1, ECE, Brier, agreement, bootstrap CIs
    report.py         # results → report.md with charts
  configs/            # S1..S6 configs; each test run's config is committed and hashed first
  data/               # fetch.sh plus manifest.sha256 only; data itself isn't committed unless the license allows
  results/<date>-<config-hash>/
    predictions.jsonl  metrics.json  cost.json  report.md
```

- `agents/bin/metrics.py` (Article 18.3) reads the latest `metrics.json`
  into the daily snapshot.
- The dashboard's KPIs panel shows `panel_accuracy_delta`, `cost_ratio`, and
  `calibration_ece` with their confidence intervals.

---

## 5. Baselines first: what Sprint 1 must produce

Before any target in §3 is taken seriously:
1. the locked split, and its hash;
2. S1 on test for every configured single model, which picks the reference
   model;
3. S2 (self-consistency) on test;
4. a published results report, and a blog section explaining it in plain
   language;
5. the Steward revises or confirms the OKR targets by edict, now that there's
   a real starting point.

---

## 6. Versions (the P-002 roadmap)

| Version | Scope | Done when |
|---|---|---|
| 001 | Dataset chosen and cleared; fetch script and manifest; locked split; `bench.py` with S1 and S2; metrics with CIs; a dev run on 50 claims | The Auditor reproduces the dev metrics from the committed config and hash |
| 002 | Test-set baselines (S1, S2); results report; KPIs wired into `metrics.py` and the dashboard | Report published; the Steward re-sets the O1 targets |
| 003 | S3 and S4 panels and aggregations; agreement and error correlation; the live-set builder started | Panel results with CIs versus baseline |
| 004 | S5 debate; Track E prototype | Debate result, positive or negative, published |
| 005 | S6, the Verafy argument solver | Solver result versus S3–S5 |

Each version follows Article 21: plan, build, Auditor acceptance, release
notes, release on the dashboard, and human comments in the discussion.

---

## 7. Budget and safety

- **Money:** every run costs API money. Estimate each run before starting:
  claims × calls per claim × tokens × price per token, per model.
  - Start small: a 50-claim dev slice.
  - The first budget request goes to the Steward as a board `#decision
    @rex`, stating the cap.
  - Stop any run at its cap, and report spend daily (Auditor).
- **Keys:** only through `agents/.env` (sealed, Article 17.3). Never in
  configs, results, or logs.
- **Rate limits:** back off politely; never hammer an API.
- **Nothing public** until the Steward approves: result reports go through
  the outbox and the blog like everything else.

---

## 8. Acceptance for this whole spec

- An edict is recorded, and the Lawyer's opinion is posted.
- `org/OKRS.md` and `org/KPIS.md` are updated through the proper channels,
  with OKRs still marked DRAFT and targets provisional.
- P-002 exists with this spec, version 001 is planned, and it's on the
  Sprint 0 agenda.
- The Steward has seen the dataset license findings, the cost estimate, and
  the budget request before anything runs.
- `amendment.py check`, `projects.py check`, `case.py check`, and
  `seed-check.sh` all pass.

---

## 9. Future projects to add to `projects/PROPOSED.md`

| Candidate | Why it matters to the KPIs |
|---|---|
| **P-003 Verafy Verdicts:** a public, sourced verdict log with 30- and 90-day re-checks | Needed for the North Star, `verdict_survival`, and O2 |
| **P-004 Verafy Facts:** an atomic fact store with provenance, queried before judging | Needed for `fact_reuse_rate` and O3 |
| **Source linkage:** trace citations to primary sources and catch circular citation | Raises `source_support_rate` |
