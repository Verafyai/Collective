# Verafy Org: Learnings

The single file of things we learned along the way. **Append only.** Never
rewrite or delete another agent's entry. Chief consolidates duplicates monthly
into a "Consolidated" section at the top, keeping the originals.

Entry format:

```
## YYYY-MM-DD · <agent> · <short title>
What happened:
What we learned:
What we'll do differently:
```

---

## 2026-09-23 · rex · Starting principles
What happened: Designed Verafy across several iterations (truth chain,
decision engine, browser extension, simulation console, ProofSwarm).
What we learned: Work that's cheap to verify is what makes strangers' work
trustworthy. Formalized statements need human vetting. Label anything
simulated.
What we'll do differently: Show the work in public, and never post anything
we couldn't defend with sources.

## 2026-09-24 · steward (via Claude) · Archives must be untouchable
What happened: A bulk rename (verafy-org.toml → collective.toml) was applied to every file mentioning it, including the archived Charter versions. `charter-verify.py` failed immediately on the altered archives.
What we learned: Bulk edits must exclude archives and frozen records (charter/history, cases, edicts, the event log). The hash chain catches this, which is why it exists.
What we'll do differently: Scope every bulk edit to generated files only, and run `charter-verify.py` after any repo-wide change.

## 2026-09-24 · steward (via Claude) · Secret detectors need word boundaries
What happened: The file name "task-T-0002-user-guide-and-blog" contains "sk-T-0002-…", which the key detector took for an API key. The event log stored redacted copies of a case and the Charter, which would have made replay inexact, and the public-commit scan would have blocked the commit.
What we learned: Detection patterns need word boundaries, and a false positive in redaction is an integrity bug, not just noise. The weekly-blog test caught it because it checks exact incident counts.
What we'll do differently: Keep key-pattern tests with both real-shaped keys and innocent look-alikes, and treat any unexpected redaction incident as something to investigate before continuing.

## 2026-09-25 · scribe (via Claude) · The version header must move with the log entry
What happened: When recording A-0013, the amendment log's Part VI entry was correctly stamped v6.1.1, but the Charter's own header field ("Charter version: X") in charter_head.md wasn't bumped first. charter-verify.py reads the header to pick which archived file to check against, so it compared the new content to the OLD v6.1.0 archive and failed.
What we learned: The two version markers (the header line and the latest Part VI entry) must always be edited together, in the same step, or verification catches a real inconsistency rather than a cosmetic one.
What we'll do differently: Treat "bump the header" as the first sub-step of every amendment, before assembling Part V, and let charter-verify.py run immediately after every rebuild, not just at the end of a batch.

## 2026-09-25 · scribe (via Claude) · An edict recorded isn't an edict done
What happened: E-0035 (amendments folder, projects, launch script) was recorded, then the next request arrived and was implemented first; E-0035 sat at status "issued" until the Steward noticed.
What we learned: Recording an edict is only step one. The Project Manager's daily check of edicts still at "issued" exists for exactly this, and edict_latency_days (≤ 7) is the KPI that would have caught it.
What we'll do differently: Before starting any new edict, check `edict.py replay` for earlier ones still "issued" and finish or explicitly schedule them first.

## 2026-09-25 · scribe (via Claude) · Rebuilds must restore permissions too
What happened: A from-scratch rebuild restored launch.sh byte-for-byte but not its executable bit, because the rebuild only restored permissions for scripts under bin/ and setup/.
What we learned: "Identical content" isn't "identical files"; the seed check compares content, so the fresh-rebuild test caught this, not the daily check.
What we'll do differently: charter.py marks every .sh file executable, and the fresh-rebuild test checks the launch script is executable.

## 2026-09-25 · scribe (via Claude) · A plugin isn't a program on your PATH
What happened: On the Steward's first real launch, launch.sh installed herdr-plus as a herdr plugin and then called `herdr-plus` as a command, which failed: installing the plugin doesn't put its binary on PATH. The script's "already installed?" check also missed the installed plugin and prompted for a reinstall.
What we learned: The first run on the real machine is the only true test of anything that touches installed software; stand-ins encode our assumptions, including wrong ones.
What we'll do differently: launch.sh now detects the plugin by its config folder, finds the binary inside herdr's plugin folders (or points to the documented Homebrew install), and states the next two commands plainly. When the Steward reports a real-machine error, fix it at the root and add a test for that exact case.
