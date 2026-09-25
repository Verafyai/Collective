# Credits

The Collective credits everyone whose work it builds on (Charter P4). Every
prototype, video, and post also credits its own sources. Maintained by Media;
additions are part of the work that uses them.

## Software

| Work | Author | License | Used for |
|---|---|---|---|
| fusion-harness | IndyDevDan (disler) | MIT | Governance sessions and Verafy Next: multi-model opinions, debate, collaboration |
| herdr | Herdr, Inc. (herdrdev/herdr) | Apache-2.0 | The Collective's agent workspace |
| herdr-plus | cloudmanic | MIT | Workspace template and headless open |
| tsk | smarzban | MIT | Task board |
| herdr-projects, herdr-agent-progress | eliasstravik | MIT | Coordination and progress |
| herdr-remote | dcolinmorgan | AGPL-3.0-or-later (commercial license also offered) | Phone and Telegram approvals |
| herdr-radar | hhdebb | MIT | Agent overview |
| memex | nicosuave | MIT | Transcript search |
| age | Filippo Valsorda and contributors | BSD-3-Clause | Sealing auth |
| Claude Code | Anthropic | commercial terms | Agent runtime |
| Grok CLI | xAI | commercial terms | Social agent |
| W&B Weave (weave 0.53.10) | Weights & Biases | Apache-2.0 | Tracing the Collective's runs and events to the Steward's private Weave project (Article 12.10) |
| gitleaks | Zachary Rice and contributors | MIT | Public-commit redaction gate |
| Barlow, Barlow Semi Condensed (fonts) | Jeremy Tribby (The Barlow Project Authors) | SIL Open Font License 1.1 | Dashboard floor and scope; served locally from `dashboard/fonts/` |
| Public Sans (font) | USWDS (The Public Sans Project Authors) | SIL Open Font License 1.1 | Dashboard records; served locally |
| xterm.js (@xterm/xterm 6.0.0) and @xterm/addon-fit 0.11.0 | The xterm.js authors (SourceLair, Microsoft, and contributors) | MIT | The dashboard's web terminal; vendored in `dashboard/vendor/xterm/` with SHA256SUMS |
| Source Serif 4 (font) | Adobe (The Source Serif 4 Project Authors) | SIL Open Font License 1.1 | Dashboard records; served locally |

Licenses confirmed against each project's repository during setup (2026-09-24).

## Research (the Research Library)

- Irving, Christiano, Amodei. *AI safety via debate* (2018).
- Du, Li, Torralba, Tenenbaum, Mordatch. *Improving Factuality and Reasoning
  in Language Models through Multiagent Debate* (2023).
- Liang et al. *Encouraging Divergent Thinking in Large Language Models
  through Multi-Agent Debate* (2023).
- Chan et al. *ChatEval* (2023).
- Michael, Mahdi, Rein, Petty, Dirani, Padmakumar, Bowman. *Debate Helps
  Supervise Unreliable Experts* (2023).
- Khan et al. *Debating with More Persuasive LLMs Leads to More Truthful
  Answers* (2024).
- Kenton et al. (Google DeepMind). *On scalable oversight with weak LLMs
  judging strong LLMs* (2024).
- Smit, Grinsztajn, Duckworth, Barrett, Pretorius. *Should we be going MAD?*
  (2024).
- Amazon Science judge and debate research (see `research/papers.md`),
  including the Ising dependence-aware aggregation, RoPoLL, CollabEval,
  initial-stance debate, SELENE, LRBench/Judge-R1, and JudgePanel papers.

## Ideas and inspiration

- Verafy's founding documents: the ETHDenver 2025 talk and the March 2025
  update (library F1, F2), by Rex St. John and the Verafy team.
- Certificate Transparency, OpenTimestamps, and Dung's argumentation
  frameworks (grounded semantics), whose ideas shaped the Collective's ledger
  and solver.
