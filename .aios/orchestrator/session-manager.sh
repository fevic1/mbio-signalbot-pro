#!/usr/bin/env bash
set -Eeuo pipefail

mkdir -p "$AIOS_ROOT/sessions"

SESSION=$(date +%Y%m%d-%H%M%S)

echo "$SESSION" > "$AIOS_ROOT/sessions/current"

echo "[Session]"
echo "$SESSION"
