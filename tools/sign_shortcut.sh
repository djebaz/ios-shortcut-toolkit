#!/usr/bin/env bash
set -euo pipefail

# Sign an unsigned Shortcut with Apple's macOS `shortcuts` CLI.
#
# Usage:
#   ./sign_shortcut.sh INPUT.shortcut OUTPUT.shortcut [MODE]
#
# MODE:
#   anyone                (default)
#   people-who-know-me

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 INPUT.shortcut OUTPUT.shortcut [anyone|people-who-know-me]" >&2
  exit 2
fi

INPUT=$1
OUTPUT=$2
MODE=${3:-anyone}

case "$MODE" in
  anyone|people-who-know-me)
    ;;
  *)
    echo "Invalid signing mode: $MODE" >&2
    exit 2
    ;;
esac

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Error: Apple Shortcut signing requires macOS." >&2
  exit 1
fi

if ! command -v shortcuts >/dev/null 2>&1; then
  echo "Error: Apple's 'shortcuts' CLI is not available." >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input file does not exist: $INPUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

echo "Signing Shortcut..."
echo "  input : $INPUT"
echo "  output: $OUTPUT"
echo "  mode  : $MODE"

shortcuts sign \
  --mode "$MODE" \
  --input "$INPUT" \
  --output "$OUTPUT"

echo "Signed Shortcut written to: $OUTPUT"
