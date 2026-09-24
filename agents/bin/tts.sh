#!/usr/bin/env bash
# Voiceover from a script with a local, stock, open voice (Charter Part III R8; Article 4.2).
#   agents/bin/tts.sh SCRIPT.txt OUT.wav|OUT.mp3|OUT.m4a
#   agents/bin/tts.sh --install-voice        download the configured stock voice (once)
# Provider: TTS_PROVIDER in agents/.env (default piper, local, nothing leaves the machine).
# Voice:    TTS_VOICE (default en_US-ljspeech-medium: MIT model, public-domain LJ Speech data).
# Only published stock Piper voices (rhasspy/piper-voices) are accepted: no cloning, ever.
set -euo pipefail
cd "$(dirname "$0")/../.."
if [ -f agents/.env ]; then set -a; source agents/.env; set +a; fi
PROVIDER="${TTS_PROVIDER:-piper}"
VOICE="${TTS_VOICE:-en_US-ljspeech-medium}"
VOICES="${TTS_VOICE_DIR:-$HOME/.local/share/collective/piper-voices}"
[ "$PROVIDER" = piper ] || { echo "REFUSED: only the local piper provider is set up (TTS_PROVIDER=$PROVIDER)"; exit 1; }
[[ "$VOICE" =~ ^([a-z]{2})_([A-Z]{2})-([a-z0-9_]+)-(x_low|low|medium|high)$ ]] \
  || { echo "REFUSED: TTS_VOICE must be a published Piper stock voice like en_US-ljspeech-medium"; exit 1; }
lang="${BASH_REMATCH[1]}"; region="${BASH_REMATCH[2]}"; name="${BASH_REMATCH[3]}"; quality="${BASH_REMATCH[4]}"
model="$VOICES/$VOICE.onnx"

if [ "${1:-}" = "--install-voice" ]; then
  mkdir -p "$VOICES"
  base="https://huggingface.co/rhasspy/piper-voices/resolve/main/$lang/${lang}_$region/$name/$quality/$VOICE"
  for ext in onnx onnx.json; do curl -fsSL -o "$VOICES/$VOICE.$ext" "$base.$ext"; done
  curl -fsSL -o "$VOICES/$VOICE.MODEL_CARD" "https://huggingface.co/rhasspy/piper-voices/resolve/main/$lang/${lang}_$region/$name/$quality/MODEL_CARD" || true
  (cd "$VOICES" && shasum -a 256 "$VOICE.onnx" "$VOICE.onnx.json" | tee "$VOICE.sha256")
  echo "installed $VOICE into $VOICES (check its MODEL_CARD license before publishing audio)"; exit 0
fi

in="${1:?script file}"; out="${2:?output .wav, .mp3 or .m4a}"
[ -f "$in" ] || { echo "no such script: $in"; exit 1; }
command -v piper >/dev/null || { echo "piper not installed: uv tool install piper-tts"; exit 1; }
[ -f "$model" ] || { echo "voice not installed: agents/bin/tts.sh --install-voice"; exit 1; }
if [ -f "$VOICES/$VOICE.sha256" ]; then (cd "$VOICES" && shasum -a 256 -c --quiet "$VOICE.sha256") || { echo "REFUSED: voice files changed since install"; exit 1; }; fi
mkdir -p "$(dirname "$out")"
case "$out" in
  *.wav) piper -m "$model" -i "$in" -f "$out" >/dev/null 2>&1 ;;
  *.mp3|*.m4a) tmp="$(mktemp -t tts).wav"; trap 'rm -f "$tmp"' EXIT
               piper -m "$model" -i "$in" -f "$tmp" >/dev/null 2>&1
               ffmpeg -loglevel error -y -i "$tmp" "$out" ;;
  *) echo "output must end in .wav, .mp3 or .m4a"; exit 1 ;;
esac
echo "$out ($VOICE, stock voice, AI-generated)"
