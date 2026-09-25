#!/usr/bin/env bash
# The Collective's two repositories (Charter Article 17).
#   public : this folder        → git@github.com:Verafyai/Collective.git
#   private: this folder/private → git@github.com:Verafyai/CollectivePrivate.git (git-ignored by public)
#
#   repos.sh init [--offline]     set up both repos and their remotes (clones private if it exists)
#   repos.sh status               show both
#   repos.sh commit "message"     commit private (always) and public (only if the redaction scan passes)
#   repos.sh push [--public]      push private; push public only with --public (Steward) or PUBLIC_AUTO_PUSH=1
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f agents/config.env ] && source agents/config.env
PUBLIC_REMOTE="${PUBLIC_REMOTE:-git@github.com:Verafyai/Collective.git}"
PRIVATE_REMOTE="${PRIVATE_REMOTE:-git@github.com:Verafyai/CollectivePrivate.git}"
cmd="${1:-status}"; shift || true

scan_public() {  # redaction gate over everything the public commit would include
  local files; files="$(git ls-files -mo --exclude-standard)"
  [ -z "$files" ] && return 0
  local hits
  hits="$(printf '%s\n' "$files" | tr '\n' '\0' | xargs -0 grep -HInE \
    -e '(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9_-]{20,}' -e 'gh[pous]_[A-Za-z0-9]{30,}' -e 'xox[abprs]-' -e 'AKIA[0-9A-Z]{16}' \
    -e '\b[0-9]{8,10}:[A-Za-z0-9_-]{35}\b' -e '(API_KEY|SECRET|TOKEN|PASSWORD)[A-Z_]*=[^[:space:]'"'"'"]{6,}' \
    -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' -e 'AGE-SECRET-KEY-1[0-9A-Z]{20,}' 2>/dev/null | cut -d: -f1-2 || true)"
  if [ -z "$hits" ] && command -v gitleaks >/dev/null; then
    # gitleaks sees exactly the files this commit would include, never git-ignored ones (agents/.env)
    local stage; stage="$(mktemp -d)"
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      # vendored third-party code (dashboard/vendor/*) skips gitleaks only while it still matches its committed SHA256SUMS
      d="$(dirname "$f")"; b="$(basename "$f")"
      if [[ "$f" == dashboard/vendor/* ]] && [ -f "$d/SHA256SUMS" ] && [ "$b" != SHA256SUMS ] \
         && grep -q "^$( (command -v sha256sum >/dev/null && sha256sum "$f" || shasum -a 256 "$f") | awk '{print $1}')  $b\$" "$d/SHA256SUMS"; then continue; fi
      mkdir -p "$stage/s/$d" && cp -p "$f" "$stage/s/$f"
    done <<< "$files"
    if ! gitleaks detect --no-git --no-banner --redact --source "$stage/s" \
         --report-format json --report-path "$stage/r.json" >/dev/null 2>&1; then
      hits="$(python3 -c 'import json,os,sys
for x in json.load(open(sys.argv[1])):
    print("%s:%s: gitleaks %s" % (os.path.relpath(os.path.join(sys.argv[2], x["File"]), sys.argv[2]), x["StartLine"], x["RuleID"]))' \
        "$stage/r.json" "$stage/s" 2>/dev/null || true)"
      [ -n "$hits" ] || hits="gitleaks: scan failed, no report (fail closed)"
    fi
    rm -rf "$stage"
  fi
  if [ -n "$hits" ]; then   # locations only: the matched text is never printed or stored (Article 4.7)
    echo "REFUSED: public commit blocked; possible secrets at:"; echo "$hits"
    mkdir -p private/incidents
    printf '#incident\n### system · %s\nPublic commit blocked by redaction scan. @rex review.\n%s\n' "$(date -Iseconds)" "$hits" \
      > "private/incidents/$(date +%F-%H%M%S)-public-commit-blocked.md"
    return 2
  fi
}

case "$cmd" in
  init)
    [ -d .git ] || git init -q -b main
    git remote get-url origin >/dev/null 2>&1 || git remote add origin "$PUBLIC_REMOTE"
    grep -qxF 'private/' .gitignore || echo 'private/' >> .gitignore
    if [ ! -d private/.git ]; then
      if [ "${1:-}" != "--offline" ] && git ls-remote "$PRIVATE_REMOTE" >/dev/null 2>&1 && [ -n "$(git ls-remote "$PRIVATE_REMOTE")" ]; then
        tmp="$(mktemp -d)"; git clone -q "$PRIVATE_REMOTE" "$tmp/p"; cp -Rn "$tmp/p/." private/ ; rm -rf "$tmp"
      else
        git -C private init -q -b main
      fi
      git -C private remote get-url origin >/dev/null 2>&1 || git -C private remote add origin "$PRIVATE_REMOTE"
    fi
    [ -f private/.gitignore ] || printf '*.key\n*.pem\n.env\nsecrets/*.txt.plain\n' > private/.gitignore
    echo "public : $(git remote get-url origin)"; echo "private: $(git -C private remote get-url origin)";;
  status)
    echo "== public (Collective)";        git status -sb | head -15
    echo "== private (CollectivePrivate)"; git -C private status -sb | head -15;;
  commit)
    msg="${1:?commit message}"
    [ -f agents/config.env ] && cp agents/config.env private/config/config.env
    git -C private add -A && { git -C private commit -qm "$msg" && echo "private: committed"; } || echo "private: nothing to commit"
    scan_public || exit $?
    git add -A && { git commit -qm "$msg" && echo "public: committed"; } || echo "public: nothing to commit";;
  push)
    git -C private push -q -u origin HEAD && echo "private: pushed"
    if [ "${1:-}" = "--public" ] || [ "${PUBLIC_AUTO_PUSH:-0}" = 1 ]; then
      scan_public || exit $?
      git push -q -u origin HEAD --tags && echo "public: pushed"
    else echo "public: not pushed (Steward runs: agents/bin/repos.sh push --public)"; fi;;
  *) sed -n '2,12p' "$0"; exit 1;;
esac
