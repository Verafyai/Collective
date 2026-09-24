#!/usr/bin/env bash
# Run the Collective Dashboard (project P-001; Charter Article 18) on http://127.0.0.1:4848.
#   agents/bin/dashboard.sh            private mode (the Steward's view)
#   agents/bin/dashboard.sh --public   public mode: nothing from the private repo
# Read-only, local only, Python standard library. Code: dashboard/.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec python3 dashboard/server.py "$@"
