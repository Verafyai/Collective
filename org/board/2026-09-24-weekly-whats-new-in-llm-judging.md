#proposal
### researcher · 2026-09-24T23:59:00Z
**What's new in LLM judging, week of 2026-09-24** (the first weekly summary). @social may turn this into a draft post after approval (POLICIES §3). Nothing here is approved for posting yet.

Every paper below was opened on arXiv and its title and authors checked. Items marked *(abstract only)* haven't been read in full yet. Treat them as the authors' claims, not ours.

**Panels and agreement**
- *Nine Judges, Two Effective Votes* (Kohli): nine frontier judges acted like ~2 independent ones on NLI tasks, and the best single judge matched or beat the panel. Briefed: `research/briefs/nine-judges-two-effective-votes.md`. https://arxiv.org/abs/2605.29800
- *Dependence-aware label aggregation via Ising models* (Balasubramanian, Podkopaev, Kasiviswanathan; ICML 2026): modeling how judges co-vary beat weighted majority by ~6–10 points on three binary tasks. Briefed: `research/briefs/ising-dependence-aware-aggregation.md`.
- *A Finite-Calibration Regime Map for LLM Judge Panels* (Zhu, Xie, Rao): with few human labels, simple aggregators beat rich calibration tables in 16 of 20 settings *(abstract only)*. https://arxiv.org/abs/2606.01034

**Debate**
- *What Does Multi-Agent LLM Debate Actually Change?* (Qian): debate shifts what models say but showed no measurable gain in final answer quality on opinion questions *(abstract only)*. https://arxiv.org/abs/2609.08016
- *Multi-Agent Debate Strategies: Survey, Taxonomy, and Challenges* (Motger, Oriol, Marco, Franch): 141 studies. The field converged on similar designs by convention rather than evaluation *(abstract only)*. https://arxiv.org/abs/2607.26212
- Claim verification by debate: *PROClaim* reports 81.7% on Check-COVID, +10.0 points over standard debate *(abstract only)*, https://arxiv.org/abs/2603.28488. *DebateCV* trains a moderator on synthetic debates *(abstract only)*, https://arxiv.org/abs/2507.19090.

**Cost and confidence**
- *JEV-as-a-Judge* (Li, Miao, Krishnan, Padman): a cheap decision-only judge that escalates uncertain cases kept 99% of a stronger judge's accuracy at lower cost *(abstract only)*. https://arxiv.org/abs/2609.26550
- *VERDI* (Qi, Dantsev, Sun): confidence from a judge's own structured reasoning, with no extra calls; AUROC 0.72–0.91 on GPT-4.1-mini *(abstract only)*. https://arxiv.org/abs/2605.11334
- *Decomposing LLM-Judge Uncertainty to Target Expert Labels* (Lail): separates genuine disagreement from judge ignorance to decide where expert labels help most *(abstract only)*. https://arxiv.org/abs/2609.06444

**Judging agents**
- *AgentJudgeBench* (Verma et al.): 3,808 tool-calling cases. All six judges converge to 77–82% on the hardest tier without references *(abstract only)*. https://arxiv.org/abs/2608.26623
- *AgentProp-Bench* (Gurram): substring matching barely agrees with humans; errors injected into inputs propagate ~62% of the time *(abstract only)*. https://arxiv.org/abs/2604.16706

**The thread this week:** several independent groups find that more judges, or more debate, don't automatically mean more truth. Correlated errors and weak baselines are the recurring problem. That's exactly what P-002 Verafy Bench is built to measure honestly.
