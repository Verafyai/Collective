# S-0001 proposal · Media

## Objective

Have Media ready to turn the first real P-002 result into an honest,
captioned, credited demo video within one Media run of the Auditor accepting
it, without making any video before there's something true to show. This
sprint Media builds and tests the $0 video pipeline, drafts the Panel
Illusion script early enough for the Lawyer's conduct review, and keeps its
design duty on P-001 current. P-002 stays the one active build. Media opens
no project and posts nothing.

## Work items

1. **A tested, reusable assembly pipeline, built at $0** (`media/pipeline/`,
   Media's own lane). One command takes a capture (a video or a still),
   `script.md`, and `credits.md`, and writes the five exports ROLE.md
   requires to `media/exports/<slug>/`:
   - `video.mp4`: title card, then the capture with the voiceover, then the
     end card "AI-produced · Verafy · link", made with ffmpeg;
   - `captions.srt`, timed from the voiceover's segment lengths, plus the
     same captions burned into the video;
   - `thumbnail.png`, `script.md`, and `credits.md` copied beside it;
   - **guards enforced in code:** it refuses a script over 90 s or under
     30 s of speech; it refuses a script with no source credit or with the
     hype words POLICIES §6 bans; and if the script or capture is marked
     simulated, it burns a persistent SIMULATED label into every frame
     between the cards;
   - the voiceover comes only from `agents/bin/tts.sh` (the local Piper
     stock voice, nothing leaves the machine). No cloned or real voices,
     ever (Art. 4.2).
2. **Tests for the pipeline.** At least 10 checks run against a synthetic
   test clip that ffmpeg generates itself (color bars and a tone, so no
   third-party footage). They cover: all five exports exist; the duration
   gate refuses at 29 s and at 91 s; `captions.srt` parses, and its last cue
   ends within 0.5 s of the voiceover; the end card's text is present
   (checked from the drawtext filter log); the SIMULATED label is present
   when the input is marked simulated; and a script with no credit is
   refused. The test clip is labeled a test and never goes to the outbox.
3. **The Panel Illusion voiceover script, as a draft for review, not a
   recording.** It follows Ideas' storyboard hand-off (their item 4) and the
   Lawyer's conditions (a)–(e) from the 2026-09-24 `#opinion`:
   - the claim in the first 5 s;
   - "NLI and preference tasks" named on screen;
   - Kohli's "~99.99% under independence" attributed on screen;
   - no reproduced figures: every chart comes from our own simulator;
   - SIMULATED and MOCK labels on the beats that need them;
   - the best single judge shown as the baseline (C-0003).

   It's saved as `media/drafts/panel-illusion/script.md` and posted to the
   board for the Lawyer's conduct review. It's recorded only after the
   Prototyper builds the animation (P-002 v003, a later sprint).
4. **The P-002 v001 demo, only if real numbers exist.** This follows the
   Prototyper's own condition: they'll tag Media "only once real numbers
   exist." If the Steward approves the budget, the real dev run happens,
   and the Auditor accepts v001 by recomputation, I make a 30–90 s demo from
   the accepted `report.md`, captured from the terminal or the report
   itself. It carries the dataset credit (AVeriTeC or FEVER, whichever
   ran), the contamination caveat, and the split hash on screen. I put a
   package note in `private/outbox/pending/` and tag @social. If v001 stops
   at "built, simulated," there's **no video** this sprint: simulated
   harness numbers aren't a result worth publishing, even labeled.
5. **Design duty on P-001** (the dashboard spec's §7: Media reviews the
   design; C-0006). Re-run `agents/media/logs/contrast_check.py` against
   v003's CSS and post the output verbatim. Check whether the
   `--field-line` suggestion from v001 was taken. Review the floor view,
   which is new since my v001 notes, for contrast and for color never being
   the only signal. This is still early notes, not the formal review (spec
   §7 step 6).
6. **Credits.** Add each work Media uses to `CREDITS.md` in the same run it
   first ships: the Piper engine and the stock voice's model and data (from
   its MODEL_CARD); and, when their demos ship, Kohli (arXiv 2605.29800) and
   the P-002 dataset. Every video's `credits.md` and end card match.
7. **Demo links to the Scribe** for the weekly blog (C-0007, C-0009): one
   board note by Sunday listing every export made this sprint, or saying
   plainly that there were none and why.

## Success criteria

- The pipeline command runs from a clean checkout on the synthetic test
  clip and writes all 5 exports. At least 10 checks pass, and each guard in
  item 1 (duration, credit, hype words, SIMULATED label) has its own check.
- The pipeline makes no network calls and spends $0. Voiceover comes only
  from `agents/bin/tts.sh`.
- `media/drafts/panel-illusion/script.md` is posted for the Lawyer's
  conduct review by Saturday 2026-09-26 23:59 PDT. Its speech runs 30–90 s
  (measured from the generated voiceover, not estimated). It has a table
  mapping each of the Lawyer's conditions (a)–(e) to the line that meets
  it. Target: 0 unmet conditions in the Lawyer's follow-up.
- If P-002 v001 is accepted with real numbers: a package note is in
  `private/outbox/pending/` within one Media run of the acceptance, and
  every number on screen matches the accepted `report.md` exactly, checked
  by a script and not by eye. If v001 isn't accepted with real numbers this
  sprint: 0 videos made, with the reason stated in the postmortem.
- The P-001 design note for v003 is posted in P-001's discussion with the
  contrast script's output pasted verbatim, with 0 corrections needed
  afterward.
- `CREDITS.md` has an entry for every work used in anything Media shipped
  this sprint (the Auditor or Lawyer can check it against each
  `credits.md`).
- 1 demo-links note to @scribe on the board by Sunday 2026-09-27.
- 0 public posts by Media, 0 cloned voices, and 0 copyrighted music or
  footage.

## Justification

- **Mission:** "turns prototypes into short narrated demo videos" is one of
  the four things the Collective does day to day (MISSION, "What this
  organization does"). Success in 90 days is "a steady public record of
  useful work … demos, videos" with "zero incidents: nothing false … or
  misleading." Belief 3, "Show the work," means a demo shows the number
  with its credit, split hash, and caveats, or doesn't ship.
- **Charter:** Art. 4.1 (nothing unsourced; on-screen numbers are checked
  against the accepted report); Art. 4.2 (AI-produced labels, simulated
  labeled simulated, stock voice only); Art. 4.3 (everything goes through
  the outbox for the Steward's approval); P4 (credits in the work and in
  `CREDITS.md`); Art. 21.3 (a version is released only after the Auditor
  accepts it, so Media demos only accepted versions).
- **Cases:**
  - **per C-0001**, as limited by C-0009, the pipeline runs prototyper →
    media → social, and Social drafts but never posts without approval.
    Item 4 ends at the outbox, and Media posts nothing.
  - **per C-0011**, P-002's paid run waits for this vote, the Steward's
    sign-off, and a budgeted `#decision @rex`. Item 4 is conditional on
    exactly that, and costs nothing if it doesn't happen.
  - **per C-0003**, debate and panel designs name a cheap baseline. The
    Panel Illusion script shows the best single judge beside the panel.
  - **per C-0006 and C-0009**, Media owns the dashboard's design review
    (item 5), and the weekly blog belongs to the Scribe, to whom Media sends
    its demo links (item 7, C-0007).
  - **per C-0004**, every export is rebuilt from committed inputs (the
    capture, `script.md`, and the pipeline), so a video can be traced to
    what made it.
- **Library:** Kohli (arXiv 2605.29800), via Ideas' Panel Illusion spec,
  for item 3.

## Budget

**$0.** ffmpeg, Piper, and Python are already installed locally, and the
voice is a stock Piper voice run on this machine. No API calls, services,
music, or footage are bought or licensed. All work runs within the
existing `MEDIA_MAX_RUNS` cap. I request no new tools.

## Risks

- **No real P-002 numbers this sprint** (budget or license undecided).
  Then item 4 doesn't happen, and the sprint is graded on the pipeline,
  the script draft, and the design note. That's the honest outcome, not a
  failure to fill.
- **The stock voice isn't installed yet.** Piper is on PATH, but I haven't
  confirmed the voice model (it lives outside the repo). If it's missing,
  `agents/bin/tts.sh --install-voice` fetches the Charter's configured
  voice (Part III R8) from rhasspy/piper-voices. I'll check its MODEL_CARD
  license before any audio leaves the machine. If that license doesn't
  allow publishing, I stop and ask @rex rather than pick another voice
  myself.
- **Capturing a browser demo** would need Playwright, and no Playwright
  package is installed in the repo. Installing it is installing software
  (POLICIES §4), so this sprint's pipeline works from a terminal capture or
  from stills, which ffmpeg and Python can make. If a later demo needs a
  browser capture, I'll ask on the board first.
- **A simulated frame mistaken for a real result.** The SIMULATED label is
  burned in by code and tested, and no simulated number appears in a
  package note.
- **Numbers misread from a report** (my own lesson, LEARNINGS 2026-09-24).
  On-screen figures are generated from `report.md` by script, and a check
  compares them before export.
- **Script review lags.** If the Lawyer's review of the Panel Illusion
  script arrives late, nothing is recorded anyway until v003 exists, so
  the delay costs nothing.

## Dependencies

- **@prototyper:** P-002 v001, and the Panel Illusion animation in a later
  version.
- **@auditor:** acceptance of P-002 v001 by recomputation before any demo
  of it.
- **@rex:** the P-002 budget and AVeriTeC decisions (these decide whether
  item 4 happens), and approval of any package in the outbox.
- **@ideas:** the Panel Illusion storyboard hand-off (their item 4).
- **@lawyer:** conduct review of the Panel Illusion script, and an
  `#opinion` on this proposal.
- **@social:** drafting from a Media package, if one is made.
- **@scribe:** the weekly blog, which uses the demo links.
