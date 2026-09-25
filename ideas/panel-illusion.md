# Idea: Panel Illusion ("your nine judges are two votes")

- **Proposed by:** ideas · 2026-09-24
- **Status:** proposed (awaiting the Lawyer's `#opinion` and the Project
  Manager's scheduling; a project only once approved, per C-0010)
- **Board thread:** `org/board/2026-09-24-proposal-panel-dependence-diagnostics.md`
- **Source briefs:** `research/briefs/nine-judges-two-effective-votes.md`
  (high potential), `research/briefs/ising-dependence-aware-aggregation.md`
  (medium; used only as a follow-on, below)

## Pitch

Add judges to a panel and watch the headcount climb while its *effective*
number of independent votes flattens near two, and a small, reusable
diagnostic that puts that number next to every Verafy Bench result.

## Paper(s)

- **Primary:** Kohli, *Nine Judges, Two Effective Votes: Correlated Errors
  Undermine LLM Evaluation Panels*, arXiv 2605.29800 (v1, May 2026). Single
  author, not peer reviewed as far as the arXiv page shows; we present its
  numbers as the author's findings, not ours.
- **Follow-on only:** Balasubramanian, Podkopaev, Kasiviswanathan,
  *Dependence-Aware Label Aggregation for LLM-as-a-Judge via Ising Models*,
  ICML 2026.

The idea relies on three findings from the Kohli brief:
1. `n_eff = k / (1 + (k − 1)·φ̄)` (Kish design effect over the judges'
   binary error vectors) was 2.18–2.48 for nine judges on three NLI sets.
2. Majority vote fell 7.6–22.0 points short of the independence
   ("Condorcet") prediction, and the best single judge matched or beat the
   panel on all three.
3. Unanimous verdicts were wrong 9.1% of the time on MNLI (90.9% accurate
   on 319 items), against ~99.99% expected under independence.

## What the viewer sees (storyboard, ~75 s)

1. **0–5 s, the claim.** Title card: "Nine AI judges. How many independent
   votes?" A panel of 9 judge tiles, a counter reading "9 votes."
2. **5–25 s, the illusion.** A slider raises the shared-error correlation
   φ̄ from 0 to 0.4. Two lines on one chart: *headcount* (straight up to 9)
   and *effective votes* (bending over, flattening toward 1/φ̄ ≈ 2.5).
   Caption: "Simulated panel, correlation set to match Kohli (2026)."
3. **25–45 s, the gap.** Judges are added one at a time. The "if
   independent" accuracy line rises toward 100%; the actual majority-vote
   line stalls; a dashed line marks the best single judge, and the panel
   never clears it by much. The shaded area between is labeled
   "Condorcet gap."
4. **45–60 s, unanimity isn't safety.** Items where all judges agree light
   up; a counter shows how many of those unanimous verdicts are still
   wrong. Caption contrasts the simulated rate with Kohli's reported 9.1%
   (and the ~0.01% independence would predict).
5. **60–75 s, what Verafy does about it.** Cut to a Verafy Bench results
   card (mocked layout, labeled as such until real Bench data exists) where
   accuracy now sits next to `n_eff`, the error-correlation heatmap, and
   the unanimous-verdict error rate. Closing line: "Weigh agreement; don't
   count it." Credits: Kohli (2026); AI-produced; simulated data labeled.

## Minimal build scope (2–3 days of agent work)

1. **`panel_diag.py`** (pure Python + numpy, no model calls), importable by
   P-002's `src/metrics.py`:
   - pairwise phi matrix over per-judge binary error vectors;
   - `n_eff` by Kish and by eigenvalue (`k / λ_max`), with bootstrap 95%
     CIs over items;
   - independence prediction for majority vote (Monte Carlo from per-judge
     class-conditional confusion matrices) and the Condorcet gap;
   - accuracy of unanimous verdicts, with its count and CI;
   - best-single-judge accuracy alongside, always.
   Input format: the `predictions.jsonl` layout in the P-002 spec (§4.7), so
   it runs on real Bench output the day S1/S3 results exist.
2. **Simulator** (`simulate.py`): judges with individual accuracies and a
   shared latent error factor whose strength sets φ̄; seeded RNG so every
   frame of the demo is reproducible (C-0004).
3. **Self-check tests:** (a) independent judges give `n_eff ≈ k`; perfectly
   correlated give `≈ 1`; (b) the Kish formula reproduces Kohli's published
   MNLI figure from his published φ̄ (9 / (1 + 8 × 0.391) = 2.18), which is
   an arithmetic check of our code against the paper, not a replication of
   it.
4. **Demo view:** a single local HTML page (or a panel in the P-001
   dashboard, if the Prototyper prefers) that reads the simulator's output
   and animates beats 2–4. Runnable with one command; localhost only.
5. **README + DEMO.md:** credits, what's simulated, and the storyboard for
   Media.

Out of scope: any model calls, any new dataset download, the Ising
aggregator, debate.

## What's real vs. simulated

| Element | Real or simulated |
|---|---|
| The formulas (Kish `n_eff`, eigenvalue `n_eff`, Condorcet gap, unanimous error) | Real methods, from the paper |
| Kohli's numbers quoted on screen (2.18–2.48, 9.1%, 7.6–22.0 pp) | Real, the author's published results, cited |
| The panel shown in beats 2–4 | **Simulated** judges tuned to a φ̄ like the paper's; labeled on screen |
| The Bench card in beat 5 | **Mock layout** until P-002 produces per-judge outputs; then real |
| Any claim about Verafy's own panels | None is made until Bench data exists |

## Risks

- **Overclaiming the paper.** Kohli tested NLI and preference tasks, not
  fact-checking with evidence. The video must say "on these tasks" and must
  not imply Verafy's panels fail too. Mitigation: caption beat 1 with the
  tasks, and have the Lawyer review the script (P3, Article 4.1).
- **It reads as arguing against Verafy's own thesis.** It partly does, and
  that's fine: the Steward's spec (§1) says a negative result is valid and
  publishable. The framing is "this is why we measure," not "panels don't
  work."
- **Simulation mistaken for data.** Mitigation: persistent "SIMULATED"
  label on every simulated frame (Article 4.2).
- **Duplicate work with P-002.** Mitigation: `panel_diag.py` *is* the
  Bench agreement metric (spec §4.5 "Agreement"); built once, used in both.
- **Single-author, unreviewed source.** Mitigation: say so in the README and
  video credits; don't lean on any one number as settled.

## Tie to the Verafy mission

- The Mission's first belief is "many AIs, not one," with disagreements
  visible. This measures whether "many" is really many.
- It serves O1 (prove or disprove that panels beat a single judge) and the
  `panel_accuracy_delta` KPI directly: a panel delta without `n_eff` next to
  it can't be interpreted.
- It cautions the Mission's "truth is threshold-based" belief: a unanimous
  verdict needs its own measured error rate before it's called settled.
- Per F1 (mission alignment only, not evidence), agreement should be
  weighed, not counted.

## Precedents

- **C-0003 (follows):** cites Research Library papers and the findings the
  design relies on (below). Not a debate design, but it names its cheap
  baseline anyway.
- **C-0010 (follows):** if approved, this becomes a project from an
  approved spec, or, preferably, a work item inside P-002 Verafy Bench once
  that project exists; it doesn't start before approval.
- **C-0004 (follows):** seeded simulation; demo frames are reproducible
  from recorded outputs, and no external effects.
- **C-0001 (follows, as limited by C-0009):** hand-off goes Ideas → Project
  Manager (scheduling) with the Lawyer's opinion, then Prototyper → Media;
  nothing public without the Steward's approval.
- **C-0006 (not relied on):** reusing the P-001 dashboard for the demo
  view is optional and the Prototyper's call; this idea doesn't change the
  dashboard's mandate.

## Library citations

- **08, Smit et al. 2024:** "Always compare against a cheap baseline."
  The design puts the **best single judge** (Bench S1) and
  **self-consistency** (Bench S2) next to every panel number; the diagnostic
  is how you tell whether a panel beat its cheapest competitor for a real
  reason.
- **04, Chan et al. 2023 (ChatEval):** found persona referee panels agree
  with humans more than single judges. That's the claim this tool tests on
  our own data; `n_eff` says how much of a panel's apparent diversity is
  real.
- **07, Kenton et al. 2024:** not a debate design, so the information-
  asymmetry question doesn't apply to this build. It frames the follow-up:
  when Bench adds S5 debate, `panel_diag.py` measures whether debate raises
  or lowers φ̄ (Kohli found chain-of-thought *raised* it: φ̄ 0.456, n_eff
  1.94). The judge in S5 would see the same evidence as the debaters in
  Track J, so per 07 we should expect little gain there.

## Follow-on (not part of this proposal)

Once Bench S3 produces per-judge outputs on enough items: an **Ising vs.
weighted-vote** demo from the second brief, showing the "wrong-mode"
agreement that makes weighted voting confidently wrong as judges are added.
It needs a binarization choice or a Potts extension for AVeriTeC's four
labels, and the paper's own curves show no gain below ~5 judges or small
samples. I'll propose it when that data exists, subject to the 3-proposal
limit.

## Budget

$0 in API spend: no model calls, no paid services, nothing deployed. Agent
time only (2–3 Prototyper days, ~1 Media day).
