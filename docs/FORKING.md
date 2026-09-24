# Forking the Collective

Verafy is meant to be forked (Charter P2, Article 20). This is how to grow
your own self-operating collective for the public good from its seed.

## What you get

`CHARTER.md` is the whole seed: a Constitution with founding principles,
the structure, a step-by-step rebuild sequence, the full text of every file,
and a verified amendment history.
- `agents/bin/charter.py materialize --include-live` builds the whole thing.
- `agents/bin/seed-check.sh` proves the build is exact.

## Steps

1. **Fork** `Verafyai/Collective` on GitHub, or copy `CHARTER.md` into an
   empty repo and materialize it.
2. **Create your private repo** and point `PUBLIC_REMOTE` and
   `PRIVATE_REMOTE` in `agents/config.env` at your own repos.
3. **Become the Steward.** Generate your own age key (`agents/bin/secrets.sh
   keygen`) and replace Rex's name in Article 2.
4. **Write your mission** in `org/MISSION.md` and Article 0 (P1, P2). Keep
   the principles that fit your purpose. The conduct, credit, transparency,
   and seed principles (P3–P5, P12) are strongly recommended.
5. **Choose your members:** edit Part II §2 and the role files. Membership
   can later change by majority vote (Article 3.6).
6. **Clear Verafy's history:** start a fresh amendment log with your own
   genesis entry, and fresh amendment files, case law, edicts, sprints,
   projects, and event log. Keep
   `CREDITS.md`, and add Verafy to it.
7. **Run `./launch.sh`**, which starts Claude Code on the setup plan.

## Credit

Forks credit Verafy and the authors in `CREDITS.md` (Charter P4). A fork is
fully independent: its Steward, decisions, and conduct are its own.
