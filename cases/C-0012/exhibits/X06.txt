# Spec: P-002 Verafy Bench

<!-- Sections 4 onward of specs/steward-2026-09-24-mission-kpis-verafy-bench.md (the Steward's spec; edict E-0052 with E-0053), copied verbatim per its §0 step 6. Created under the PM #decision org/board/2026-09-24-decision-create-p-002-verafy-bench.md and case C-0011. The Lawyer's conditions (a)–(f) bind this project; they are recorded in discussion.md. -->

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
