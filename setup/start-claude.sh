#!/usr/bin/env bash
# Start the first Claude Code agent with the setup message (used by launch.sh).
cd "$(dirname "$0")/.."
exec claude "$(cat setup/first-message.md)"
