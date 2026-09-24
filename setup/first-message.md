You're the first Claude Code agent of the Collective, and you're setting it up. Everything you need is in this folder.

Read, in order:
1. CLAUDE.md
2. CHARTER.md, starting with Part I (Article 0, the twelve founding principles, then the rest of the Constitution)
3. org/OFFICERS.md and org/AGENT-PERMISSIONS.md
4. specs/setup-plan.md
5. projects/INDEX.md and projects/001-dashboard/ (the dashboard is project P-001: its spec, version-001, and discussion)

Record my instructions as edicts before acting (CLAUDE.md explains how).

Then work through specs/setup-plan.md in order, stopping for my review at every step marked ⏸:
- environment check;
- repositories and auth: link GitHub, seal agents/.env, commit edicts one by one, push the private repo, and show me what the public repo will contain so I can push it myself;
- credits;
- install and configure the herdr plugins;
- build the dashboard as P-001 version-001, release it with `projects.py release 1 1` once the Auditor's checks pass, and open http://127.0.0.1:4848 for me;
- the glue, including fusion-harness;
- the smoke test;
- Sprint 0, theme "What is the best course of action for the Collective right now?", stopping before sign-off.

When I confirm go-live, run `touch private/.setup-complete`, then tell me to re-run ./launch.sh, which starts every office.

Start with the environment check now.
