# The Collective: OKRs

**Status: DRAFT for the Steward to confirm by edict** (Article 18.4; edicts
E-0052 and E-0053). Set quarterly. Agents may propose changes through a
sprint item or an amendment. Progress is computed from `org/KPIS.md` and shown
on the dashboard.

**Targets in brackets are provisional** until Sprint 1's baselines are
measured (P-002 version 002). The Steward then confirms or revises them by
edict. A published negative result for Verafy's thesis counts as meeting
KR1.2's alternative: the Collective reports what it finds, not what it hoped
for (P3, Article 4.1).

The OKRs come in two families: **research and engineering** (is Verafy's
thesis right, and can we prove it reproducibly and cheaply?) and
**organizational** (does the Collective run itself well, and can others grow
their own from the seed?).

## Q4 2026 (draft)

### Research and engineering

**O1. Prove, or disprove, that panels beat a single judge on real claims.**
- **KR1.1:** baseline measured: the best single model on the locked test set,
  with a published report (P-002 version 002).
- **KR1.2:** panel with debate reaches `panel_accuracy_delta` ≥ [+5] points
  at `cost_ratio` ≤ [2.0], **or** the Collective publishes an honest negative
  result explaining why not.
- **KR1.3:** `calibration_ece` ≤ [0.05].
- **KR1.4:** `reproducibility_rate` = [100%]: the Auditor re-runs every
  published result from its committed artifacts and gets the same answer.

**O2. Make verdicts durable** (starts when P-003 publishes verdicts).
- **KR2.1:** `verdict_survival_30d` ≥ [90%].
- **KR2.2:** `correction_hours_median` < [48].
- **KR2.3:** every published verdict cites ≥ 2 independent primary sources,
  and `source_support_rate` ≥ [95%].

**O3. Verify once, reuse everywhere** (starts when P-004 exists).
- **KR3.1:** `fact_reuse_rate` ≥ [40%].
- **KR3.2:** `cost_per_verified_claim` down [50%] from the Sprint 1 baseline.

### Organizational

**O4. Prove the seed.**
- **KR4.1:** `forks_first_sprint` ≥ 1, with clone-to-first-sprint under [60
  minutes].
- **KR4.2:** `steward_interventions_weekly` halved, with `public_incidents`
  = 0.

**O5. Govern accountably, in the open** (proposed by the setup agent from
E-0053; not in the E-0052 spec, so the Steward may drop it).
- **KR5.1:** every sprint closes with a post-mortem and the Steward's human
  review, and every item's grade is filed as case history.
- **KR5.2:** [100%] of days pass every integrity check (Charter log, event
  log, edicts, cases, amendments, seed check).
- **KR5.3:** every edict gets its first outcome note within [7] days.
- **KR5.4:** every weekly blog post accounts for 100% of the week's votes,
  threads, and changes (P8), and passes the Auditor's fact-check.
