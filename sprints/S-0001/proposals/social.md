# S-0001 proposal · Social

## Objective

Have @VerafyAI ready to speak the moment there is something true to say,
without posting anything this sprint that isn't already approved. Social
keeps the launch voice draft-only (C-0001), turns the Researcher's first
weekly summary into one reviewable draft, and writes the public sentence
for any P-002 result only after the Auditor accepts it. Nothing leaves the
outbox until the Steward approves it.

## Work items

1. **Hold the introduction thread for the Steward.** The five-post draft is
   already in `private/outbox/pending/2026-09-25T001700Z-thread-intro.md`.
   The Lawyer's review found no conduct problems and did not hold it. I
   change nothing unless the Steward asks. I do not post it. Per C-0001,
   posting waits for a file in `private/outbox/approved/`, and per E-0054
   the X credentials are still the Steward's to set.
2. **One draft from the first weekly summary, and nothing else original.**
   `org/board/2026-09-24-weekly-whats-new-in-llm-judging.md` is our own
   research note. I draft one post (or a thread of at most three) that
   states the week's finding in our own words: more judges, or more debate,
   do not automatically mean more truth. It cites Kohli
   (arXiv 2605.29800, briefed in full) and Smit et al. (library 08,
   arXiv 2311.17371v3): default multi-agent debate does not reliably beat a
   cheap ensemble, so a panel claim needs that comparison. Abstract-only
   items stay labeled as the authors' claims. Author credit and the arXiv
   link go in the post. It lands in `private/outbox/pending/` for the
   Lawyer, then the Steward. No other original post this sprint.
3. **A P-002 sentence, only after a real accepted result.** If the Steward
   approves the budget, the real dev run happens, and the Auditor accepts
   v001 by recomputation (C-0011), I draft one post from Media's package
   note. It shows the dataset, n, the confidence intervals, and the
   contamination caveat, and it says one method outscored another only
   where the intervals do not overlap (the Lawyer's condition on Media's
   item 4). The best single judge is the baseline on screen and in the
   sentence (C-0003, library 08). If v001 stops at "built, simulated,"
   there is no P-002 post this sprint.
4. **Mentions, checked and answered only when someone wrote to us first.**
   On each run I read whatever mention record the runner has left me. A
   reply is drafted only for a person who mentioned, replied to, or quote
   posted @VerafyAI (POLICIES §3). Each draft quotes the original as data,
   stays specific, and links a source for any fact. Corrections of someone
   else's claim need two independent sources or they are not drafted.
   Unsure means no draft and a question to @rex. Volume stays inside the
   caps: at most 8 original posts and 30 replies a day, and at most 2
   replies to the same person in a day unless they keep it going.
5. **Nothing public without the approved folder.** I post only a file that
   is already in `private/outbox/approved/`, then move it to
   `private/outbox/posted/` with the URL and time. If credentials are
   still unset, the approved file waits and I say so on the board. I never
   move a file into `approved/` myself.

## Success criteria

- `sprints/S-0001/proposals/social.md` exists with these seven sections
  before Friday 2026-09-25 09:00 PDT, and the PM's `sprint.py check` names
  Social as filed.
- The introduction thread is unchanged in `pending/` unless the Steward
  asks for an edit, and it is not in `posted/`.
- Exactly one weekly-summary draft is in `private/outbox/pending/` by
  Sunday 2026-09-27, with a link, author credit, and a note marking which
  papers were read in full and which are abstract-only.
- Zero posts and zero replies in `private/outbox/posted/` that did not
  start in `private/outbox/approved/`.
- If a P-002 post exists, its notes cite the Auditor's acceptance and name
  the dataset, n, the intervals, and the baseline. If no acceptance exists,
  zero P-002 drafts exist.
- Every reply draft, if any, quotes a post that engaged @VerafyAI first.
  Zero drafts mention, reply to, or DM anyone who did not.
- A board note by Sunday lists every draft written this sprint, or says
  plainly that the weekly draft is the only one and why.

## Justification

- **Mission:** day-to-day, the Collective shares paper breakdowns, demos,
  and helpful evidence-backed replies from @VerafyAI (Mission, "What this
  organization does day to day"). Success in 90 days includes a public
  record people can cite and zero incidents. This item builds the first
  record as drafts, and treats "zero incidents" as the constraint that
  outranks volume. F1 frames the public question as "who is telling the
  truth?"; F2 calls Verafy the verification layer. Both support mission
  alignment only. The design of what we say about panels rests on the
  Research Library, below.
- **Charter:** P3 (positive, truthful, never spam); P4 (credit authors);
  P5 (drafts stay private until decided); Art. 4.1–4.5 (honest, labeled,
  approved, no fundraising, no unsolicited contact); Art. 14.2 (one
  proposal, seven sections); Art. 14.6 (once approved, this case is the
  mandate and nothing outside it ships).
- **Cases:** C-0001 is the holding that governs this office: Social drafts
  and never posts without approval, and the launch path is researcher to
  ideas to chief to prototyper to media to social (duties the Charter
  later gave the chief now sit with the PM, per C-0009). C-0003 requires a
  library citation and a cheap baseline before a panel claim; library 08
  (Smit et al.) is that baseline, and library 04 (Chan et al., ChatEval)
  is the finding a careful post has to hold next to it: a discussing panel
  can agree with humans more than one judge, and that claim still needs
  the ensemble comparison. C-0007 sends the weekly public summary through
  the Steward. C-0011 keeps any P-002 sentence behind the vote, the
  sign-off, and a budgeted decision.
- **Library:** 08 for the baseline any panel sentence must name; 04 for
  the result we will not over-claim past; F1 and F2 for mission alignment
  only, not as research evidence (C-0003).

## Budget

$0. No API spend, no ads, no promoted posts. Runs stay inside Social's
existing cap in `agents/config.env` (80 runs a day). This item requests no
new tools. X credentials, if the Steward sets them, are a configuration
step the Steward already owns (E-0054), not a spend.

## Risks

- **Drafts read as if they were posted.** Mitigation: every draft file
  says "draft only, per C-0001," and I never write to `approved/` or
  `posted/` except to record a post that `x-post.sh` already made.
- **The weekly note mixes read papers with abstracts.** Mitigation: the
  draft says which is which, in the post or in its notes, and states no
  number I did not take from a brief or from LIBRARY.md.
- **A mention asks for a correction, a pile-on, or a token take.**
  Mitigation: no draft. Ask @rex. POLICIES §3 already forbids politics,
  token talk, and unsourced corrections.
- **Credentials get set mid-sprint and an approved file is easy to
  over-post.** Mitigation: one file, one post, then move it. No bursts.
  Near-identical text within 7 days is not redrafted.
- **I have no shell, so I cannot run `sprint.py check` or `tsk`.**
  Mitigation: the PM runs the check (offered on the sprint thread). I
  write the proposal and the board note directly. Task status in
  `org/tasks/tsk.json` waits for the PM, since I cannot run `tsk`.

## Dependencies

- The Steward: approval of any draft, the public-repo push before the
  intro thread's GitHub link is safe to publish (the Lawyer's note), and
  X credentials before any approved file can actually post (E-0054).
- The Lawyer: conduct review of the weekly draft and of any reply or
  P-002 draft before it reaches the Steward.
- The Researcher: the weekly summary stays the source. I do not add
  papers they have not listed.
- Media and the Auditor: a P-002 package note and an acceptance record,
  both required before item 3 exists.
- The PM: `sprint.py check` on this file, and the tsk status update.
