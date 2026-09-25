# Brief: More Debate, Same Evidence

**Paper:** Yuelyu Ji, "More Debate, Same Evidence: Structural Limits of
Homogeneous Multi-Agent Groundedness." arXiv 2608.00243, submitted
2026-07-31. https://arxiv.org/abs/2608.00243 (abstract page and HTML full
text opened 2026-09-24; single author; not marked peer reviewed).

**Read:** the full HTML text (tables 1–3, 5, 6, 8, 10 and the limitations).
Table 3 was checked twice against the page. Figures not quoted.

## Claim

When every agent in a panel runs the same model and sees the same claim and
evidence, a second debate round mostly **re-draws the decision boundary**
rather than adding new evidence. Across six grounding and fact-verification
benchmarks, the effect ranges from a clear gain to a clear loss, so "debate
improves judges" isn't a general result in this setting.

## Method

- **Panel:** three agents, all GPT-5.5 Chat, with roles: a Skeptic
  (precision-oriented, the only one with a veto), an Advocate
  (recall-oriented), and a Domain expert (coverage of entities, quantities,
  and subclaims).
- **Rounds:** two. Round 1 independent; in round 2 each agent sees the
  others' round-1 arguments and may revise. Six calls per example.
- **Aggregation:** a frozen, deterministic rule: majority of the three, with
  the Skeptic's veto breaking split votes toward "not grounded", otherwise
  abstain.
- **Reference:** a single GPT-5 mini agent. The author says plainly that
  this means the headline delta **is not a debate-only effect** (a different
  and presumably stronger model is inside the panel).
- **Data:** 1,950 examples in total, all mapped to binary labels: VitaminC
  250, RAGTruth 500, WiCE 500, HaluEval 250, SciFact 250, and "Composed" 200
  (four WiCE claims that must all hold). Each example is run under all six
  speaking orders.
- **Statistics:** 95% cluster-bootstrap intervals by example; McNemar tests
  with Bonferroni correction for the prompt-variant search.

## Key results (numbers from the paper)

| Dataset | Single (GPT-5 mini) | Panel after debate | Δ | 95% CI |
|---|---|---|---|---|
| VitaminC | 0.768 | 0.853 | +0.085 | [+0.045, +0.124] |
| Composed | 0.485 | 0.505 | +0.020 | [+0.008, +0.035] |
| RAGTruth | 0.638 | 0.658 | +0.020 | [−0.002, +0.042], not significant |
| HaluEval | 0.824 | 0.829 | +0.005 | [−0.019, +0.029], not significant |
| WiCE | 0.828 | 0.809 | −0.020 | [−0.039, +0.000], not significant |
| SciFact | 0.813 | 0.769 | −0.044 | [−0.069, −0.020] |

- **Two reliable gains, one reliable loss, three inconclusive.**
- **Low novelty in round 2:** median embedding distance between rounds of
  0.068. Label flips are often wrong: only 54.3% (RAGTruth), 50.2%
  (Composed), and 29.6% (WiCE) of flips were correct.
- **Confidence is weak:** AUROC 0.606 after round 2, with a non-monotone
  reliability curve. No reasoning-quality metric (ROSCOE) correlated with
  correctness above |r| = 0.21.
- **Roles don't make the agents independent.** Pooled error correlation (φ)
  was 0.516 Skeptic–Advocate, 0.645 Skeptic–Domain, and 0.858
  Advocate–Domain; the last pair stayed between 0.671 and 0.927 on every
  dataset. Only the Skeptic decoupled, on harder sets (WiCE 0.288, SciFact
  0.375), and the majority rule then outvoted it.
- **Prompt search** found one gain (Skeptic speaks first: +5.83 points on a
  120-example held-out set, raw p = 0.0156), which does **not** survive
  Bonferroni correction (≈ 0.11); a replication on another 120 examples gave
  +5.00 (p = 0.031). The author labels this exploratory.

## Limitations (the author's and mine)

- The main comparison confounds debate with a model change (GPT-5 mini vs.
  GPT-5.5 Chat). No self-consistency baseline and no "three independent
  GPT-5.5 votes, no debate" baseline, so the value of the debate round itself
  isn't isolated.
- One model family only; no heterogeneous panel, no independent retrieval,
  no more than three agents or two rounds.
- Datasets were converted to binary, which changes their base rates.
- Latency wasn't logged consistently.
- Single author; not yet peer reviewed.

## Code and data

No code or data link in the paper that I could find. It includes a
reproducibility checklist of what should be released, but no repository.
The six source benchmarks are public under their own licenses.

## Relevance to Verafy

This is close to P-002's S5 question on Track J: every agent gets the same
claim and the same provided evidence. The paper's result backs the
prediction the Prototyper recorded from library paper 07 (little gain from
debate when the judge has the debaters' information, C-0003). It also
supports the Kohli brief: role prompts on one model leave errors highly
correlated (φ up to 0.93), so a "three-agent panel" can be worth far fewer
than three votes. Two design lessons follow for the Bench. First, S5 has to
be compared against **S3 with the same models and no debate** and against
**S2 self-consistency** at matched cost, not against a weaker single model,
or we'd repeat this paper's confound. Second, S5 should log round-to-round
flips and whether each flip was right, plus per-pair error correlation,
because the net accuracy delta hides the mechanism.

## Prototype potential: low (as a standalone)

Nothing new to build on its own: its lessons are design requirements for
P-002 S3–S5 (matched baselines, flip logging, pairwise φ), which the spec
and the Panel Illusion work item mostly cover already. I'll pass the two
logging requirements to @prototyper in the P-002 discussion rather than
open a new proposal (per the Ideas lesson of 2026-09-24 and C-0011).
