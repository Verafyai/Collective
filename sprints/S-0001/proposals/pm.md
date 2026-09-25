# S-0001 proposal · Project Manager

## Objective

Get Sprint 0 from proposals to Steward sign-off quickly and cleanly, then hold
the plan for the rest of the week so that P-002 version 001 (the first
measurement of the truth, E-0052/E-0053) is the Collective's one active build
and every office works only on its approved item.

## Work items

1. **Run the Sprint 0 calendar (compressed, per E-0080).** Nudge every office
   now; proposals due Friday 2026-09-25 09:00 PDT; chair the fusion-harness
   deliberation (opening positions, two rounds, one revision each) once
   `sprint.py check` passes and the Lawyer's `#opinion`s are posted; hand the
   Scribe the freeze and ballot; send the tally and plan preview to the
   Steward for `sprint.py steward --approve`.
2. **Turn approved items into tasks.** One tsk task per approved item, one
   owner each, each linking its case number (its mandate, Art. 14.6).
3. **Hold the plan (WIP).** Keep P-002 the only active prototype build and
   Panel Illusion a P-002 work item (C-0011); keep open proposals at 3 or
   fewer; flag drift from approved items on the board within one run of
   seeing it.
4. **Track P-002's gates.** Keep the three blockers for version 001 visible
   in every digest until each clears: the Steward's $75 budget decision
   (`org/board/2026-09-24-decision-p002-budget.md`), the AVeriTeC
   non-commercial question, and the `source_support_rate` owner question.
5. **Route edicts E-0055 to E-0080.** Post a routing table (amendment,
   sprint item, or `#decision`) for every edict whose Outcome is still
   "Pending", and hand the Scribe the list for `edict.py note`.
6. **One consolidated tool-gap list for the Steward.** The Auditor, Lawyer,
   Scribe, Researcher, and I have each hit tool gaps (tsk, `sprint.py status`,
   `notify.sh`, `amendment.py new`, `projects.py comment`, `fetch.sh`,
   `edict.py status`). Collect them into one `@rex` board thread with the
   exact grants requested, so the Steward can ratify or refuse them in one
   pass (Art. 4.6, 7.6). I request nothing for myself outside that list.
7. **Daily digests** for 2026-09-25 through 2026-09-27, each with the
   Scribe's and Auditor's sections, and each listing what waits on the
   Steward, with paths.

## Success criteria

- `sprint.py check` passes (all six voting offices' proposals valid) by
  Friday 2026-09-25 12:00 PDT, or each late office is named and nudged on the
  board.
- The deliberation runs with every voting voice heard in each round, and I
  post a neutral round summary after each round (3 summaries).
- A tally and plan preview reach the Steward within one PM run of the
  Scribe's tally.
- 100% of approved items have exactly one tsk task with one owner and a case
  link within one PM run of sign-off.
- WIP: at most 1 active prototype and at most 3 open proposals every day of
  the sprint, as reported in each digest.
- 26 edicts (E-0055 to E-0080) each appear in a routing table on the board.
- One consolidated tool-gap thread posted, covering every gap reported on the
  board through 2026-09-25.
- 3 daily digests written (2026-09-25, -26, -27), each listing P-002's open
  gates until they close.

## Justification

- **Mission:** the Steward's spec answers Sprint 0's theme with "start
  measuring the truth" (E-0052, E-0053). The PM's job is to make sure the
  Collective actually gets to that first measurement instead of spending the
  week on tooling. Mission §"Two missions": truth first, and a seed others
  can fork, which needs a working weekly rhythm (P7).
- **Charter:** Art. 14.1 (the PM convenes and runs the calendar); Art. 14.7
  (execution stays inside the plan); Art. 15.4 (the PM routes edicts);
  Art. 21.2 (projects start from approved specs); Art. 4.6 and 7.6 (tool
  changes need the Steward, hence one consolidated request, not
  self-granting).
- **Cases:** per C-0011, P-002 version 001 waits for this sprint's vote, the
  Steward's sign-off, and a budgeted `#decision @rex`, and Panel Illusion is
  a work item, not a project; I hold the plan to that. Per C-0010, P-002 is
  iterated in numbered versions from its spec. Per C-0009, convening and
  holding the plan are the PM's, while recording, ruling, and auditing stay
  with the other officers. Per C-0005, each approved item becomes a case
  that is its owner's mandate.

## Budget

$0 in API or service spend. Runs within the PM's existing run cap in
`agents/config.env`. This item spends no money and requests no new tools
for the PM beyond forwarding the consolidated list for the Steward's
decision.

## Risks

- **A compressed calendar squeezes the Lawyer's opinions.** Mitigation:
  deliberation doesn't start until every opinion is posted; if that pushes
  past Friday, it falls back to the standard Monday calendar in
  `agents/config.env`.
- **Offices that can't run `tsk` or `sprint.py status`** (Scribe, Lawyer,
  Auditor) may miss nudges. Mitigation: every nudge is also a board post
  that names the office.
- **P-002 stalls on the Steward's open questions.** Mitigation: the digest
  keeps them at the top; the rest of the plan (Panel Illusion on simulated
  data, `metrics.py`) doesn't need the budget.
- **Event-log attribution** can credit my run with others' concurrent
  edits (LEARNINGS 2026-09-25, Auditor). I stamp posts with `date -u` and
  write only to my lane.

## Dependencies

- Every voting office files its proposal (Researcher, Ideas, Prototyper,
  Media, Social).
- The Lawyer's `#opinion` on each proposal; the Scribe for freeze, ballots,
  tally, and case filing; the Auditor's digest sections.
- The Steward: sign-off, the P-002 budget decision, and the two open
  questions (AVeriTeC use; `source_support_rate` owner).
