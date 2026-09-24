#!/usr/bin/env bash
# Wait until the setup agent has built the dashboard, then run it (used by launch.sh).
cd "$(dirname "$0")/.."
until [ -x agents/bin/dashboard.sh ]; do
  printf '\r⏳ Waiting for the setup agent to build the dashboard (P-001 version-001)… %s' "$(date +%H:%M:%S)"; sleep 10
done
echo; echo "Dashboard found. Starting it at http://127.0.0.1:4848"
exec agents/bin/dashboard.sh
