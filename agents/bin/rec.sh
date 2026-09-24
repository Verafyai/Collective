#!/usr/bin/env bash
# Record the Steward's manual changes so they're part of the replayable history.
# Usage: agents/bin/rec.sh "why I changed it"
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 agents/bin/eventlog.py sync --actor steward --reason "${1:?reason}"
