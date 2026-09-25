#!/usr/bin/env bash
# Observability settings (P-005; Charter Article 12.10). Source it:  . agents/bin/env.sh
# Loads WANDB_API_KEY (and optional OBS_* / WEAVE_* overrides) from the git-ignored agents/.env without printing
# anything, then points OpenTelemetry at the Weave Agents endpoint. No key is ever written in this file.
_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -f "$_root/agents/.env" ]; then
  while IFS='=' read -r _k _v; do
    case "$_k" in WANDB_API_KEY|WEAVE_ENTITY|WEAVE_PROJECT_NAME|OBS_PRIVATE_MODE)
      [ -z "${!_k:-}" ] && export "$_k=${_v%\"}" && export "$_k=${!_k#\"}" ;; esac
  done < <(grep -E '^(WANDB_API_KEY|WEAVE_ENTITY|WEAVE_PROJECT_NAME|OBS_PRIVATE_MODE)=' "$_root/agents/.env")
fi
export WEAVE_ENTITY="${WEAVE_ENTITY:-rexstjohn-verafy}"
export WEAVE_PROJECT_NAME="${WEAVE_PROJECT_NAME:-The Collective}"
export WEAVE_PROJECT="$WEAVE_ENTITY/$WEAVE_PROJECT_NAME"          # for weave.init
export OBS_PRIVATE_MODE="${OBS_PRIVATE_MODE:-metadata}"            # full | metadata | off (E-0108: metadata)
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://trace.wandb.ai/agents/otel/v1/traces"
if [ -n "${WANDB_API_KEY:-}" ]; then export OTEL_EXPORTER_OTLP_TRACES_HEADERS="wandb-api-key=$WANDB_API_KEY"; fi
export OTEL_RESOURCE_ATTRIBUTES="wandb.entity=$WEAVE_ENTITY,wandb.project=$WEAVE_PROJECT_NAME"
unset _root _k _v
