#!/usr/bin/env bash
set -Eeuo pipefail

MEM="$AIOS_ROOT/memory"

echo "[Memory]"

find "$MEM" -name "*.md" | sort | while read f
do
    echo "Loaded $(basename "$f")"
done

date > "$AIOS_ROOT/state/last-memory-load"
