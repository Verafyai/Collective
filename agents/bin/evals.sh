#!/usr/bin/env bash
# Run the Collective's eval suite in W&B Weave (P-005; evals/REGISTRY.md).
#   agents/bin/evals.sh [--suite all|E1,E4,...] [--budget USD]
# Results: the Weave Evals tab, evals/results/E*.json, the event log (eval.run), and a #eval board thread for any failure.
set -euo pipefail
cd "$(dirname "$0")/../.."
. agents/bin/env.sh
[ -x agents/.venv/bin/python ] || { echo "no agents/.venv: run setup/bootstrap.sh first"; exit 1; }
exec agents/.venv/bin/python evals/run.py "$@"
