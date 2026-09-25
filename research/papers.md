# Papers index

Status values: `new` → `briefed` → `proposed` → `prototyped` → `published`.
Researcher keeps this current. Every entry links a brief in research/briefs/.

## Research Library

The eight foundational debate papers live in `research/library/`; see
`research/library/LIBRARY.md` (status `library`).

## Seed list (verify each link before briefing)

| Paper | Link | Topic | Status |
|---|---|---|---|
| Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | https://arxiv.org/abs/2306.05685 | Foundations | new |
| Replacing Judges with Juries (panel of diverse models) | https://arxiv.org/abs/2404.18796 | Panels | new |
| Dependence-aware label aggregation via Ising models (Amazon, ICML 2026) | https://www.amazon.science/publications/dependence-aware-label-aggregation-for-llm-as-a-judge-via-ising-models | Aggregation | briefed ([brief](briefs/ising-dependence-aware-aggregation.md)) |
| ROPOLL: Robust panel of LLM judges (Amazon) | https://arxiv.org/abs/2606.30931 | Aggregation | new (link verified 2026-09-24) |
| CollabEval (Amazon) | https://arxiv.org/abs/2603.00993 | Collaboration | new |
| Multi-agent debate with initial stance (Amazon, NAACL 2025) | https://arxiv.org/abs/2502.08514 | Debate | new |
| SELENE: selective, evidence-weighted debating (Amazon) | https://www.amazon.science/publications/selene-selective-and-evidence-weighted-llm-debating-for-efficient-and-reliable-reasoning | Debate | new |
| LRBench and Judge-R1 (Amazon) | https://www.amazon.science/publications/lrbench-and-judge-r1-principled-evaluation-and-training-of-llm-based-judges-for-long-context-reasoning | Benchmarks | new |
| JudgePanel (AWS) | https://arxiv.org/abs/2608.29168 | Distilled panels | new |
| Judging the Judges: position bias | https://arxiv.org/abs/2406.07791 | Bias | new |
| LLMs are not fair evaluators | https://arxiv.org/abs/2305.17926 | Bias | new |
| JudgeBench | https://arxiv.org/abs/2410.12784 | Benchmarks | new |
| LLMs-as-Judges survey (+ Awesome list) | https://arxiv.org/abs/2412.05579 | Survey | new |

## Found by standing searches

Every link below was opened and its title and authors checked on the date
shown.

| Paper | Link | Topic | Found | Status |
|---|---|---|---|---|
| Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels (Kohli) | https://arxiv.org/abs/2605.29800 | Panels, dependence | 2026-09-24 | briefed ([brief](briefs/nine-judges-two-effective-votes.md)) |
| A Finite-Calibration Regime Map for LLM Judge Panels (Zhu, Xie, Rao) | https://arxiv.org/abs/2606.01034 | Panels, calibration | 2026-09-24 | new |
| JEV-as-a-Judge: Accept When Confident, Escalate When Unsure (Li, Miao, Krishnan, Padman) | https://arxiv.org/abs/2609.26550 | Cost, cascades | 2026-09-24 | new |
| What Does Multi-Agent LLM Debate Actually Change? A Layered Analysis of Disagreement and Answer Quality (Qian) | https://arxiv.org/abs/2609.08016 | Debate | 2026-09-24 | new |
| Courtroom-Style Multi-Agent Debate with Progressive RAG and Role-Switching for Controversial Claim Verification (PROClaim; Chowdhury et al.) | https://arxiv.org/abs/2603.28488 | Debate, claim verification | 2026-09-24 | new |
| Debating Truth: Debate-driven Claim Verification with Multiple LLM Agents (DebateCV; He et al.) | https://arxiv.org/abs/2507.19090 | Debate, claim verification | 2026-09-24 | new |
| Stop Overvaluing Multi-Agent Debate: We Must Rethink Evaluation and Embrace Model Heterogeneity (Zhang et al.) | https://arxiv.org/abs/2502.08788 | Debate, baselines | 2026-09-24 | new |
| Multi-Agent Debate Strategies: Survey, Taxonomy, and Challenges (Motger, Oriol, Marco, Franch) | https://arxiv.org/abs/2607.26212 | Debate, survey | 2026-09-24 | new |
| Decomposing LLM-Judge Uncertainty to Target Expert Labels (Lail) | https://arxiv.org/abs/2609.06444 | Calibration, uncertainty | 2026-09-24 | new |
| VERDI: Single-Call Confidence Estimation for Verification-Based LLM Judges via Decomposed Inference (Qi, Dantsev, Sun) | https://arxiv.org/abs/2605.11334 | Calibration | 2026-09-24 | new |
| AgentJudgeBench: A Multi-Difficulty Benchmark for Evaluating LLM Judges on Agentic Tool-Calling (Verma et al.) | https://arxiv.org/abs/2608.26623 | Agent evaluation | 2026-09-24 | new |
| Auditing Automated Evaluation, Error Propagation, and Runtime Mitigation in Tool-Using Language Agents (AgentProp-Bench; Gurram) | https://arxiv.org/abs/2604.16706 | Agent evaluation | 2026-09-24 | new |
| Post-hoc Alignment of LLM-judges to Human Judgment Distribution (NAPHA; Steindl, Voskarides, Gasparin, Marcheggiani) | https://arxiv.org/abs/2609.01073 | Human label variation | 2026-09-24 | new |

Next to brief, for P-002 Verafy Bench: ROPOLL (S4 geometric median), the
Finite-Calibration Regime Map (aggregator choice under few labels), and
DebateCV / PROClaim (debate on claim verification, the S5 question).

## Standing searches (run every 6 h)
- arXiv cs.CL / cs.AI / cs.LG: "LLM-as-a-judge", "LLM judge", "evaluator
  model", "reward model evaluation", "multi-agent debate", "agent evaluation",
  "agent benchmark", "judge calibration", "judge bias"
- amazon.science publications on judges and evaluation
- OpenReview venues (ICLR, NeurIPS, ICML) for the same terms
