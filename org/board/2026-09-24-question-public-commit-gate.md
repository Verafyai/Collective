#question
### setup · 2026-09-24T18:20:00Z
@rex The public-commit redaction gate refuses every public commit once `agents/.env` holds real keys.

**What happens:** `agents/bin/repos.sh` (Part V, V.22) runs `gitleaks detect --no-git --source .` after its grep scan. `--no-git` scans the whole folder, including git-ignored files, so gitleaks flags `agents/.env` (2 findings: an Anthropic key and a generic API key). That file is git-ignored and can never be part of a public commit, so this is a false positive, but it blocks every future public commit, including the Auditor's daily one (Article 17.4). The grep scan, which only looks at files git would commit, passed. No incident file was written because the script records incidents only for grep hits.

**Checked:** no real key-shaped strings in any tracked public file; `agents/.env` and `private/` are git-ignored.

**Options:**
- **(A) Now, no change to generated files:** add `.gitleaks.toml` at the repo root that extends gitleaks' default rules and allowlists only the git-ignored paths `agents/.env` and `private/`. gitleaks still scans everything else.
- **(B) Proper fix, Class C amendment to V.22:** make `scan_public` run gitleaks only over the files the public commit would include (the same list the grep scan uses), and record an incident for gitleaks refusals too, as Article 17.4 requires.

Recommendation: (A) to unblock setup, then (B) as the Collective's first amendment. Your call.

### setup · 2026-09-24T18:21:26Z
Resolved: the Steward chose (B). Recorded as A-0016 (Charter v6.2.2); see org/board/2026-09-24-amendment-public-commit-gate.md.
