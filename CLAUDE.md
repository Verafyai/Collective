# The Collective: setup instructions for Claude Code

You are setting up an autonomous research-and-media organization for Verafy on
Rex's Mac, running in herdr.

**`CHARTER.md` is the source of truth.** Read it in full, starting with Part I
(the Constitution), then `specs/setup-plan.md`. Every other file in the repo is
generated from Part V of the Charter. If you rebuild from scratch, follow Part
III (the reconstitution sequence) in order.

## Edicts: record Rex's instructions first

Every instruction Rex gives you about the Collective is an **edict** (Charter Article
15). Before acting on it:
1. record it verbatim with `python3 agents/bin/edict.py new --title "<short
   title>" --text "<his exact words>"`, which numbers it and commits it to
   git;
2. act on it;
3. note the outcome with `python3 agents/bin/edict.py note E-NNNN
   "<what was done: amendment, case, files>"`.

Questions and chit-chat aren't edicts. Directions are.

## Rules for this setup session

1. **Follow `specs/setup-plan.md` step by step.** Stop for Rex's review where
   it says so.
2. **Never guess tool or plugin APIs.** Before configuring any herdr plugin,
   read its README and write what you learned in `docs/plugin-notes.md`
   (commands, config paths, flags). Verify Claude Code flags with
   `claude --help`.
3. **Secrets:** Rex fills in `agents/.env` himself. Only its encrypted copy
   (`private/secrets/env.age`, via `agents/bin/secrets.sh seal`) is ever
   committed, and only to the private repo. Never print, log, echo, or
   commit its contents. Check only whether each variable is set.
4. **Never** use `--dangerously-skip-permissions` or equivalent flags for any
   agent. Each role gets only the tools in `agents/config.env`.
5. **Nothing posts publicly during setup,** and you never push the public repo;
   Rex does (`agents/bin/repos.sh push --public`). X posting stays behind
   `agents/bin/x-post.sh`, which only accepts files Rex approved.
6. **Don't edit** `CHARTER.md` or any generated file. Changes to the Collective go
   through a Charter amendment (Article 7). During setup, raise needed changes
   on the board with `@rex`.
7. **Plugin listings aren't reviewed by Herdr.** Install only what's in
   `setup/plugins.txt`. Skim each plugin's code for anything that sends data
   off the machine, and note it in plugin-notes.
