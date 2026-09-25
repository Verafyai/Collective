# The Court: a Decisions tab (P-006)

The Steward's spec (edicts E-0117, E-0118), from his handoff of 2026-09-25, kept as given. Notes on where the work had to differ are at the end.

**For:** the Claude Code agent working in the Collective's folder.
**From:** the Steward (Rex St. John).
**What:** add a **Decisions** tab to the dashboard. It opens **the Court**, an
isometric courtroom in the floor's graphical style. Agents stand in a circle and
argue opposing positions on a question, using **fusion-harness** for the
multi-model debate. A **Judge** rules on the evidence. The debate and the ruling
are logged, and every ruling carries a **certainty indicator**.

This is Verafy's core loop made visible: evidence, then multi-model argument,
then a scored ruling filed as a decision, and later a reopening if the evidence
changes.

Work through the Collective's own process: an edict, a project, the Lawyer, the
Auditor, a release, and a record. Keep moving unless you hit a real blocker.

---

## 1. Record the edict and open the project

```
python3 agents/bin/edict.py new --title "Decisions tab: the Court" --text "add a new tab in the interface which is \"decisions\" which uses fusion harness to have the agents argue different decisions and come up with an answer based on evidence then log the debate result and ruling and add a certainty indicator, I want a \"Court\" with a judge and the agents stand in a circle and argue. use the same graphical style"
```

Open **P-005 The Court** in `projects/` and cross-link it with P-002 (Verafy
Bench) and P-003 (Weave). Use the next free project number if 005 is taken.

**Charter.** The Charter already has courts and case law (C-0001 onward). Before
you design anything, read the articles that cover courts, cases, and reopening
(Article 13.11), and build the Court as the working form of those articles. If
the procedure below needs anything the Charter doesn't already allow, such as a
Judge role, draft an amendment and send it through the normal vote. Build the
Court at the same time behind a `provisional` flag. The UI shows "Provisional
court" until the amendment is ratified.

---

## 2. How a case works

Every decision is a **case** with a case number in the existing case-law
sequence (`C-NNNN`). A case moves through these phases, and each phase is an
event in the Record:

1. **Filed** (`case.filed`). A question arrives from one of four places: the
   Steward (through the UI), a board post tagged `#decide`, a Sentinel
   `#reopen`, or a sprint proposal that needs a ruling. The filing includes the
   question, an optional set of positions, any starting evidence links, and a
   priority.
2. **Positions framed.** If the filer didn't supply positions, the Lawyer frames
   two to four mutually exclusive ones. "Yes/No" is fine when the question is
   binary.
3. **Discovery** (`exhibit.admitted` / `exhibit.excluded`). The Researcher, plus
   any spawned Scholars, gathers evidence. Each exhibit is fetched, hashed,
   stored, and given an ID (`C-NNNN-X01`). Each exhibit records its source,
   date, a reliability rating, and whether it's independent of the other
   exhibits. The Judge rules on whether each exhibit is admitted.
4. **Advocates assigned.** Each position gets at least one advocate. Agents are
   **assigned** positions and don't choose them, so the debate tests the
   evidence rather than the agents' existing views. Every advocate runs on a
   **different model family** through fusion-harness. The Judge runs on a
   family that none of the advocates use.
5. **Argument rounds** (`argument`, `objection`, `question`):
   - **Openings:** one per position.
   - **Two rebuttal rounds.**
   - **Questions from the bench:** the Judge questions any advocate.
   - **Closings.**

   Every factual claim must cite an exhibit ID. Opposing advocates can
   **object** to uncited or misrepresented claims, and the Judge sustains or
   overrules each objection. A sustained objection **strikes** the claim, which
   stays in the transcript but is marked as struck.
6. **Jury** (`ballot.sealed`, `ballot.counted`). The voting agents cast sealed
   ballots, using the existing mechanism with distinct model families and a
   deterministic count. The jury is a check on the Judge, not a replacement.
7. **Ruling** (`case.ruled`). The Judge issues:
   - the holding, meaning which position prevails or a finding that the
     evidence is insufficient
   - the reasoning, with each point citing exhibits
   - any dissent, including a jury disagreement if there was one
   - the **certainty** score (section 3)
   - **reopen conditions:** what new evidence would change the ruling. Sentinels
     watch for exactly those conditions.
8. **Reopened** (`case.reopened`). A Sentinel whose watch condition fires files
   a reopen, and the case goes back to discovery with the prior ruling attached.

"Insufficient evidence" is a valid ruling, and it's better than a
coin-flip ruling. The Judge must use it when certainty falls below 40.

**Budget:** each case has a token cap, 150k by default and configurable per
case. The running cost appears in the UI. If the cap is hit, the Court skips
straight to closings.

**Using fusion-harness:** read the fusion-harness code first and use its real
orchestration API for the rounds and the ballots. Don't reimplement the debate
logic. If fusion-harness can't do something the procedure requires, extend it
in our fork and document the change.

---

## 3. The certainty indicator

Certainty is a **number from 0 to 100 computed by deterministic code**. It is
not just the Judge's self-reported confidence. Compute it from five inputs:

| Input | Measures |
|---|---|
| **Evidence strength** | The quality, reliability, and independence of the admitted exhibits that support the holding |
| **Cross-family agreement** | The share of model families whose sealed ballots match the holding |
| **Argument survival** | The share of the winning side's key claims that were never struck or successfully rebutted |
| **Jury margin** | How lopsided the count was |
| **Judge's stated confidence** | Recorded, and given a low weight |

Combine the first four as a weighted mean, with the Judge's confidence at low
weight. Then cap the result at the weakest of evidence strength and
cross-family agreement, so that one strong signal can't hide a weak one. Put
the weights in `court/certainty.json` and document them. Changing the weights
requires a Charter amendment.

Display the score in four bands:

| Score | Band | Color |
|---|---|---|
| 0–39 | Insufficient | grey |
| 40–59 | Low | amber |
| 60–79 | Moderate | teal |
| 80–100 | High | green |

Hovering over the score shows the full breakdown.

**Calibration:** add eval **E15, Court calibration**, to the Weave suite. Over
time it compares certainty against outcomes, meaning rulings that were later
upheld, reopened, or overturned. Add **E16, Citation discipline**, which
measures the share of claims that cite exhibits and the share of objections
that were correctly sustained.

---

## 4. The Court (the view)

Use the **same graphical style as the floor**: the night-time palette, the
isometric tiles, the same character models, hats, colors, speech bubbles,
icons, and animation timing. Reuse the floor's rendering code instead of
forking it.

**The Decisions tab.** Add **Decisions** to the top nav next to Weave, Scope,
Records, and History. It opens the Court view.

**The courtroom.** It's one large isometric room:

- **The bench** is raised at the back. The **Judge** sits behind it: a new
  character in a dark robe with a gavel, drawn in the same style as the other
  agents. Above the bench hang **scales of justice** that tilt live toward the
  leading position as the arguments land. The scales are the certainty
  indicator in physical form, and the numeric gauge sits beneath them.
- **The circle.** Advocates stand in a ring on the courtroom floor facing each
  other, with the evidence table in the middle. Each position has its own color
  ring under the feet of its advocates, so you can see which side each agent is
  on at a glance.
- **The evidence table** holds the exhibits as small glowing documents. When an
  advocate cites an exhibit, that document lifts and glows, and a thin line
  links it to the speaker.
- **The speaker** steps forward into the circle, and their argument appears in
  a speech bubble you can hover to read in full.
- **Objections:** a red **OBJECTION!** flash appears over the objector. When the
  Judge rules, the gavel strikes, the verdict shows as "Sustained" or
  "Overruled," and a struck claim's bubble cracks and fades.
- **The jury box** sits along one side, where the voting agents sit. During
  balloting they drop sealed envelopes into a box, and the count reveals them
  one at a time.
- **The ruling:** a final gavel strike, then the ruling appears as a scroll that
  unrolls with the holding and the certainty band. The scroll then flies out
  toward the Record, the same way tokens fly to the Record on the floor.

**The courthouse on the main floor.** Add a courthouse room to the floor. While
a case is in session, the participating agents walk from their desks to the
courthouse, the same way they walk to the Council table, and a "⚖️ In session:
C-NNNN" tag floats above it. Clicking the courthouse opens the Decisions tab.

**The side panel.** In the Decisions tab, the right-hand panel shows:

- **The docket:** every case with its status (filed, in discovery, in session,
  ruled, reopened), a certainty chip, and the date. It can be filtered by status.
- **Case detail:** the question, the positions, the exhibits with their links
  and ratings, the full transcript with struck claims marked, the jury count,
  the ruling, any dissent, the certainty breakdown, and the reopen conditions.
- **Replay:** a timeline scrubber that replays any past case in the courtroom,
  animated from the event log. It uses the same machinery as History.
- **⚖️ File a case:** a form with the question, optional positions, optional
  evidence links, priority, and a budget.

The panel updates live through the dashboard's existing live feed.

---

## 5. Storage, logging, and the server

**Files.** Each case gets a folder at `cases/C-NNNN/`:

| File | Contents |
|---|---|
| `case.json` | question, positions, assignments, status, and certainty with its breakdown |
| `exhibits/` | the fetched evidence, plus `exhibits.json` with hashes and ratings |
| `transcript.md` | the full debate, with struck claims marked |
| `ruling.md` | holding, reasoning, dissent, certainty, reopen conditions |

**Case law.** Every ruling is also filed as case law, so it can be cited as
precedent.

**The Record.** Every phase above is a hash-chained event in the Record.

**Weave.** Each case is one Weave conversation with
`gen_ai.conversation.id = C-NNNN`. Advocate turns, the Judge, and ballots are
spans on that conversation. Each courtroom view gets a "View in Weave" link.

**Privacy.** Cases filed from private sources follow `OBS_PRIVATE_MODE` and are
written to the private repo. Only public cases go to Verafyai/Collective.

**Server routes** (in `server.py`):

| Route | Purpose |
|---|---|
| `GET /api/cases` | the docket |
| `GET /api/cases/<id>` | full case detail |
| `GET /api/cases/<id>/replay` | the ordered events needed to animate a replay |
| `POST /api/cases` | files a case (see below) |

`POST /api/cases` is a new write. Give it the same treatment as the existing
comment write:

- It is available on 127.0.0.1 only.
- It is rate limited.
- It validates its input and caps its length.
- It records an edict for the filing, so a filing from the UI is the Steward's
  instruction on the Record.
- It refuses to file anything when the running budget cap is exceeded.

---

## 6. Acceptance (the Auditor checks all of these)

1. **The first real case.** File and run this question end to end:
   *"Does a multi-model judge panel verify real-world claims more accurately
   than the best single model?"* This ties the Court to Verafy Bench.
2. **Recorded in full.** The case appears in the docket, runs in the Court with
   the full animation, and produces `ruling.md`, a case-law entry, Record
   events, and a Weave conversation.
3. **Objections work.** At least one objection is ruled on, and a sustained
   objection's struck claim is excluded from the argument-survival input.
4. **Certainty is reproducible.** Recomputing certainty from the logged events
   gives the same number exactly.
5. **Replay is faithful.** Replaying the case from the event log produces the
   same courtroom sequence as the live run.
6. **Insufficient evidence works.** A deliberately evidence-poor test case is
   ruled "Insufficient evidence."
7. **Model families are separated.** No advocate shares a model family with the
   Judge or with an opposing advocate. Every advocate is on a distinct family.
8. **Tests and gitleaks pass.** `tests/test_court.py` and the existing
   dashboard tests pass, and gitleaks (`-q`) is clean.
9. **Provisional mode works.** The Court works in provisional mode while any
   Charter amendment is still pending.

Report back to the Steward with:

- a screenshot of the Court mid-argument and one of a ruling
- the first case's ruling and certainty breakdown
- any fusion-harness changes
- anything left undone

---

## Notes: where the work had to differ

- **P-006, not P-005:** P-005 is Weave Observability, which the handoff calls P-003.
- **Model families:** the machine has keys for Anthropic (Claude) and xAI (Grok) only. The third and later
  families come from W&B Inference (OpenAI-compatible, the same W&B key): DeepSeek, Qwen, Moonshot (Kimi),
  Z.ai (GLM), and others, wired into pi as a custom provider.
- **Case law while provisional:** Article 13 knows three courts (officer, assembly, steward). Until the Court's
  amendment passes, a ruling is filed as an **officer** case, the lowest rank, with the provisional Court as its
  source.
- **gitleaks `-q`:** gitleaks 8.30.1 has no `-q` flag (A-0016); scans use `--no-banner`.
