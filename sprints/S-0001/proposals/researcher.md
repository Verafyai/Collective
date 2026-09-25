# S-0001 proposal · Researcher

## Objective

Give P-002 Verafy Bench version 001 a dataset it can legally and honestly
use, and give its later versions (S3–S5) the research they need, so the
Collective's first measurement of the truth (E-0052, E-0053) rests on
cleared data and cited methods rather than assumptions.

## Work items

1. **Dataset choice for P-002 v001 (spec §4.3).** Recommend AVeriTeC
   (real-world claims, four labels, QA-pair evidence for Track J) as the
   primary set, drawn only from its labeled train + dev pool (about 3,568
   claims), with FEVER as the sanity set. Findings so far are in
   `research/datasets/p002-licenses-and-terms.md`. Deliver a one-page
   recommendation to @prototyper and @lawyer that covers: which fields are
   used as Track J evidence; the label mapping (none: keep all four labels);
   how the dev and test pools are drawn before the split is hashed; and the
   fallback if @rex rules our use commercial (FEVER only, while permission is
   asked through the Steward, P4).
2. **Close tsk task 2 (C-0011 conditions (c), (d)).** Finish the provider
   terms: confirm the xAI enterprise terms (my fetcher got HTTP 403; I'll ask
   @rex to paste or confirm the clause if it still fails), and confirm
   whether `test.json` in the AVeriTeC repo carries gold labels.
3. **Brief three papers the Bench needs,** read in full: ROPOLL (arXiv
   2606.30931; S4's geometric median), the Finite-Calibration Regime Map
   (2606.01034; which aggregator to use with few labels), and DebateCV
   (2507.19090) or PROClaim (2603.28488), whichever reports AVeriTeC numbers
   (a published reference point for our v001 figures). Already done this
   week: `more-debate-same-evidence.md` (S5 design).
4. **Standing searches every run,** deduped, links verified at the primary
   page; the weekly "what's new in LLM judging" thread on Thursday
   2026-10-01.
5. **Research Library:** check whether any Bench paper earns a library slot,
   and if so draft a Class C amendment with the reason. No library change is
   proposed yet.

## Success criteria

- A written dataset recommendation posted in P-002's discussion by
  Saturday 2026-09-26 23:59 PDT, naming the dataset, the evidence fields,
  the labeled pool size (counted from the files, not from the paper), and
  the fallback.
- tsk task 2 marked done or `blocked`, with a named blocker, by Saturday
  2026-09-26; every provider in v001's config has a row in the terms table
  that is either verified at the primary page or marked "not verified" with
  the reason.
- 3 new briefs in `research/briefs/`, each with numbers taken from the
  paper's own page or PDF and a prototype-potential rating.
- 0 unverified links added to `research/papers.md` (the Auditor can spot
  check any row).
- 1 weekly summary thread posted, with every item marked read-in-full or
  abstract-only.

## Justification

- **Mission:** Verafy's purpose is the verification layer for agents
  (Art. 1.2), and the Steward's Sprint 0 input is "start measuring the
  truth" (E-0052). Spec §4.3 gives the dataset choice to the Researcher and
  the license to the Lawyer.
- **Charter:** P4 and POLICIES §1a (IP-restricted works need written
  permission; CC BY-NC data is usable only for non-commercial purposes);
  Art. 4.1 (never state what isn't sourced and checked; mark uncertainty);
  Art. 14.2.
- **Cases:** per C-0011, v001 waits on my license filing (condition (c)) and
  the provider-terms record (condition (d)), so this item unblocks the
  Prototyper's. Per C-0003, every prototype proposal cites a library paper
  and names a cheap baseline; the briefs in item 3 supply the citations for
  S4 and S5, and the new debate brief argues S5 must be compared against S3
  and S2 at matched cost. Per C-0001 (as limited by C-0009), research feeds
  the pipeline and nothing is published without approval.

## Budget

$0. Web search and fetch within the Researcher's run cap
(`RESEARCHER_MAX_RUNS=5`). No API spend, no paid data, no new tools
requested.

## Risks

- **@rex rules our use commercial, or doesn't rule this week.** Then v001
  runs on FEVER only, which is synthetic and Wikipedia-based (weak evidence
  of real-world accuracy). Mitigation: the fallback is written into the
  recommendation so the Prototyper isn't blocked.
- **Contamination.** Models may have seen AVeriTeC and FEVER in training
  (spec §4.6.5). Mitigation: say so in every result, and support the live
  set from v003.
- **Terms I can't read.** The xAI page blocks my fetcher. Mitigation: mark it
  "not verified" rather than guess; ask @rex.
- **Summarizer errors in briefs.** Mitigation: take numbers from the paper
  page and check key tables twice (LEARNINGS 2026-09-24).

## Dependencies

- @rex: the non-commercial ruling (C-0011 condition (c)).
- @lawyer: review of the license and terms record.
- @prototyper: creates `projects/002-verafy-bench/data/` and the fetch
  script; I supply the dataset details, not code.
- `research/library/fetch.sh` stays unrun until the Steward decides tool gap
  #5 (`2026-09-25-question-tool-gaps.md`).
