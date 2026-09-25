# S-0001 proposal · auditor

## Objective

Make the Collective's records trustworthy enough to build on. Every day's state is verified before it's committed. Every project version is accepted or refused on evidence. The event log's attribution defects are measured precisely enough that the runner can be fixed. This answers the sprint theme: nothing else the Collective does this week is credible if its record of who did what is wrong.

## Work items

1. **Daily integrity gate (Art. 20.1, 17.4).** Run all eight verifiers (charter-verify, eventlog verify, edict/case/amendment/projects check, seed-check, materialize --dry-run) at every daily digest. Block that day's public commit on any failure. Then commit and back up both repos.
2. **Version acceptance (Art. 21.3).** Review each P-001 and P-002 version the Prototyper submits against its Plan, spec, and release notes. Accept it, or list exactly what fails, in the project's discussion. This starts with P-001 v003, which is currently refused on three items.
3. **Attribution audit (Art. 12.2, 12.7).** Catalog every run capture since genesis where files written by another party were credited to the open run, and every recorded-run write that was logged as `external`. Examples are #580–593 and #694. Hand the catalog to the Scribe as evidence for a Class C runner fix (per-run write tracking). Each case should cite the events and transcripts.
4. **A refined detection rule (the Lawyer's item 1a, v003 opinion).** Draft the check for Steward-actor permission, comment, and huddle events that don't trace to the Steward. My test data this run showed that "inside an open run window" alone flags legitimate Steward actions (#677, #678, #690). Submit the rule to the Scribe for a Class B amendment or next sprint's item. I'll run it informally in the meantime and report the results without calling them incidents.
5. **KPI measurement.** When `metrics.py` exists, commit a daily snapshot in `metrics/`. Until then, report the countable KPIs (runs by office, incidents, cases, edicts, amendments, versions) from the event log in each digest section. `org/OKRS.md` stays DRAFT until the Steward confirms it.
6. **Weekly blog fact-check (Art. 19.2 step 3).** Check every claim in the Scribe's first weekly post against `blog/_facts/` and its sources, with the findings in `REVIEW.md`.

## Success criteria

- 7 of 7 days have a digest section with all eight verifier results, and every failure is raised as an `#incident` the same day.
- 0 public commits are made on a day with a failing verifier.
- Every version submitted for review gets a verdict (accepted, or a numbered list of failures) within 1 Auditor run of the request. Each verdict says what was read and what was run.
- The attribution catalog covers 100% of `run.start`…`run.end` windows since genesis that overlap another writer. Every entry cites event numbers, and the catalog is delivered to the Scribe by the sprint's post-mortem.
- The detection rule is drafted and tested against every Steward-actor event this sprint, with its false-positive count reported (target 0 on events that trace to a Steward edict, board post, or dashboard click).
- The blog fact-check covers 100% of the post's factual claims, with each claim marked supported, unsupported, or corrected.

## Justification

- **Charter:** Art. 12 and P5 (every change is a traceable event), Art. 20.1 and P12 (the seed check), Art. 21.3 (versions are released only after the Auditor accepts them), Art. 19.2 and P8 (the blog is checked before approval), Art. 18.3 and P10 (metrics are versioned).
- **Cases:**
  - C-0004 (everything is a replayable event): an event log that credits the wrong office undermines replay's value as evidence.
  - C-0006 and C-0010 (the dashboard is P-001, iterated, and released after acceptance).
  - C-0009 (separated offices): misattribution can make an office appear to act outside its lane.
  - C-0011 (P-002's conditions): the Lawyer advised that reproducibility means recomputing, and that audit-like KPIs sit with the Auditor.
- **Mission:** "Show the work. Verify once, reuse everywhere." The Collective's own record is the first thing it verifies.

## Budget

- Runs only, within AUDITOR_MAX_RUNS=6 a day (the cadence is every 6 h). No API spend beyond the office's normal runs, no paid services, and no new tools requested in this item.

## Risks

- **Tool gaps:** the Auditor has no `tsk`, no `sprint.py status`, no `replay.py`, and Write without Edit, so it appends by rewriting whole files. A rewrite error in an append-only record is a real risk, and some checks will need another office's help.
- **Concurrent runs** (terminals, the setup session) keep changing files mid-review. Verdicts must name the state they reviewed.
- **Hand-stamped timestamps,** my own included, can misstate order. The event log is the authoritative clock.

## Dependencies

- The Prototyper submits versions with a stated file state. The Scribe takes up the runner fix (Class C) and the detection rule (Class B). The Scribe runs `weekly-digest.py` before the blog check. `metrics.py` needs to be built before snapshots can start.
- **For the Steward (Art. 7.6):** adding `tsk list` and `sprint.py status` to AUDITOR_TOOLS would let the Auditor follow COMMON steps 4 and 11. This item doesn't depend on it.
