# Plugin notes (written by the setup agent)

What each plugin and tool does, how the Collective uses it, where it keeps its
config, and **everything that sends data off the machine** (CLAUDE.md rules 2
and 7; Charter Part II §5). Written during setup on 2026-09-24 from each
plugin's README and a read of its source at the pinned commit. Herdr doesn't
review or sandbox plugins: a plugin's build and runtime commands run as the
Steward's user.

**Pinning.** Every plugin is installed at the exact commit that was reviewed:
`herdr plugin install <owner/repo> --ref <sha> --yes`. Updating a plugin means
reviewing the new commit first.

## Installed

| Plugin | Commit | License | Built how |
|---|---|---|---|
| cloudmanic/herdr-plus | f38df35 | MIT | Release binary v0.1.24 (Go isn't installed); verified: tarball SHA-256 matches the repo's Homebrew formula, installed binary identical to the release |
| smarzban/tsk | fbe0847 | MIT | `cargo build --release` from source (toolchain 1.96.0 pinned by the repo) |
| eliasstravik/herdr-projects | 5b7a0e6 | MIT | From source (`HERDR_PROJECTS_BUILD=source`), not the release download |
| dcolinmorgan/herdr-remote | f728695 | AGPL-3.0-or-later | No build; one event hook |
| eliasstravik/herdr-agent-progress | 7f3a3fe | MIT | `cargo build --release --locked` from source |

**Not installed, by the Steward's decision (edict E-0045):** nicosuave/memex
(649355e, MIT) and, for now, hhdebb/herdr-radar (92905fc, MIT). See below.
**Optional, not installed:** furkankly/zoetrope (MIT), IGUNUBLUE/hirc (no
license, no stars: don't install).

---

## herdr-plus (workspace templates, headless open)

- **Commands:** `herdr-plus open "<name>"` opens a project template headlessly
  (exact name match first, then case-insensitive); must run inside herdr.
  Also `projects`, `quick-actions`, `version`. The binary is inside the plugin
  folder, not on PATH (see launch.sh, A-0015).
- **Templates:** `~/.config/herdr/plugins/config/cloudmanic.herdr-plus/projects/*.toml`
  (`collective.toml`, `collective-setup.toml`, installed by bootstrap.sh).
  Schema: `name`, `description`, `group`, `working_dir`; `[[tabs]]` with
  `name` and either `command` or up to 4 `[[tabs.panes]]` (`command`,
  `split` down|right, `label`, `ratio`, `working_dir`).
- **Off-machine:** none at runtime (only herdr's local socket). Install
  downloaded the GitHub release. Its example quick actions open google.com or
  github.com, and only when picked.
- **Note:** it also loads quick actions from `<cwd>/.herdr-plus/quick-actions/`,
  so a cloned repo can add launcher entries (they run only when picked).

## tsk (task board)

- **Model:** not a Kanban board. Fixed statuses `open → ready → started →
  blocked → review → done`; tasks grouped by **project** (`-p`, default: the
  git repo) and **thread** (`--thread`). No custom columns or labels.
- **CLI (agents):** `tsk add -t "title" [-n notes] [-p project] [--thread X] [--json]`,
  `tsk list [--json] [-p P] [--thread X] [--open|--ready|--done|--all]`,
  `tsk status T3 started`, `tsk edit T3 --title/--notes`, `tsk guide`.
  Every command takes `--state-dir`.
- **TUI (Steward):** `tsk`, or herdr's "Open tsk board" action.
- **Data:** `~/.tsk/` (`tsk.json` plus backup, lock, trash). Env:
  `TSK_STATE_DIR`, `TSK_NO_UPDATE_CHECK`.
- **Off-machine:** an update check to api.github.com (latest release tag),
  at most daily, when the TUI opens; off with `TSK_NO_UPDATE_CHECK=1`.
  `tsk update` pipes `https://gettsk.sh/install.sh` into `sh` with no
  checksum: never run it; update by reviewing and re-pinning instead.
- **Don't run `tsk setup`:** it writes skills into the Steward's global
  `~/.claude/skills`, `~/.grok/skills`, and other agents' folders.

## herdr-projects (coordinator + worker threads)

- **Model:** a project has one coordinator agent that starts worker threads,
  each its own agent in a git worktree, tab, or checkout. Shared memory is
  plain files (`MEMORY.md`, `memory/`) inlined into each thread's brief.
- **Commands:** `herdr-projects new "<name>" --repo <path>`,
  `herdr-projects open <name> [--agent KIND]`,
  `herdr-projects thread start <proj> --title T --task-file F [--kind worktree|tab|checkout]`,
  `thread prompt|next|stop|restart`, `set coordinator_agent|thread_agent|max_parallel_threads`.
- **Data:** `~/.herdr-projects/<name>/`; safety config
  `~/.config/herdr-projects/config.toml`.
- **Off-machine:** no HTTP client of its own. It shells out to: `git fetch`
  on each worktree thread start; `gh api`/`gh pr view` for threads that report
  a PR; `git ls-remote` on `doctor`; ssh only for saved machines. The agents
  it starts call their own model APIs.
- **Not configured:** `herdr-projects configure` edits the Steward's global
  `~/.claude/settings.json` hooks and installs a skill. It refuses
  permission-skipping flags in `--agent-arg`, but config.toml's
  `*_agent_args` must never be given one (Charter 4.6).

## herdr-remote (phone approvals)

- **Installed part:** one hook, on `pane.agent_status_changed`, that sends a
  UDP packet (pane id, status, agent, cwd, hostname) to `127.0.0.1:8376`.
  With no relay running, the packet is dropped. **Inert.**
- **Not set up** (edict E-0039: no Telegram for now): the relay, the Telegram
  bot, the web app, and the phone apps.
- **If the relay is ever run:** set `HERDR_RELAY_TOKEN` and
  `HERDR_TUNNEL_MODE=none`, and never set `HERDR_SHELL_PANES`. Its
  `start.sh` opens a public cloudflared tunnel automatically if cloudflared is
  installed, and without a token any non-browser client with the URL can type
  into agent panes. The Telegram bot answers anyone unless
  `HERDR_TG_CHAT_ID` is set. Screen text (which can include secrets) goes to
  Telegram or push services.

## herdr-agent-progress (sidebar progress)

- **Commands:** `herdr-progress begin|report|status|context|clear --binding B`,
  e.g. `report --binding B --task ID --percent 65 --activity '...'`.
- **Data:** `~/.local/state/herdr/plugins/agent-progress/`.
- **Off-machine:** none (no network code; local herdr socket only).
- **Not configured:** its Configure action adds `SessionStart`,
  `PostToolUse`, and `UserPromptSubmit` hooks to the Steward's global
  `~/.claude/settings.json` and `~/.codex/hooks.json`, injecting text into
  every Claude session on the machine, not just the Collective's.

## Not installed for now: herdr-radar (sidebar skin)

- **Off-machine:** none (Unix sockets only; README says "No network").
- **Why not yet:** its install step runs `node bin/setup.js`, which edits herdr's
  `config.toml`, installs a font into the user font folder, and appends to
  existing Ghostty and Kitty terminal configs.

## Not installed: memex (transcript search, token tracking)

- **Why not:** by default it indexes **every** agent transcript on the
  machine (`~/.claude/projects` and those of Codex, Cursor, Grok, and a dozen
  others), in plaintext, into `~/.memex/`, starting automatically on herdr
  startup. There's no allowlist, only `exclude_paths` globs. The Steward's
  personal sessions (and any secret ever pasted into a session) would be
  copied into the index.
- **Off-machine:** an update check to api.github.com (off with
  `--no-update-check`); `memex share` / `S` in the TUI publishes a whole
  transcript to a public URL with no confirmation, via `agentexport`
  (not installed); an optional HTTP MCP server; HuggingFace model downloads if
  embeddings are turned on (local inference, no text sent).
- **Safe use, if adopted:** `MEMEX_ROOT` set to a Collective folder, with
  `exclude_paths` covering every source except the Collective's own agent
  transcripts; never install `agentexport`; keep the MCP server off.

## Other tools

- **Grok CLI 1.0.41** (xAI): the Social office. `SOCIAL_AGENT_CMD` in
  `agents/config.env` turns off its import of the Steward's Claude and Cursor
  MCP servers (including Gmail), skills, hooks, and rules
  (`GROK_*_ENABLED=0`, verified with `grok inspect`), and runs it with
  `--permission-mode dontAsk`, `--deny MCPTool`, `--disallowed-tools Agent`,
  and narrow `--allow` rules. **Off-machine:** model calls to xAI; session
  traces uploaded to xAI by default, with no documented opt-out.
- **gitleaks 8.30.1** (MIT): second layer of the public-commit redaction gate
  (A-0016). Local only.
- **age 1.3.2** (BSD-3-Clause): seals `agents/.env`. Local only.
