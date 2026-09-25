#!/usr/bin/env bash
# Start the Collective Dashboard (project P-001) at http://127.0.0.1:4848 and open it.
#   agents/bin/dashboard.sh            private view (everything)
#   agents/bin/dashboard.sh --public   public view (nothing from the private repo)
set -euo pipefail
cd "$(dirname "$0")/../.."
PORT="${DASHBOARD_PORT:-4848}"
if command -v open >/dev/null 2>&1; then (sleep 1.5; open "http://127.0.0.1:$PORT") & fi
exec python3 dashboard/server.py --port "$PORT" "$@"
