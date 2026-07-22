#!/usr/bin/env bash
set -e

VAULT="docs/obsidian/Decisions"

mkdir -p "$VAULT"

TITLE="${1:-Untitled Decision}"

COUNT=$(find "$VAULT" -name "ADR-*.md" 2>/dev/null | wc -l)
NUM=$(printf "%04d" $((COUNT + 1)))

FILE="$VAULT/ADR-$NUM.md"

cat > "$FILE" <<EOF
# ADR-$NUM

## Title
$TITLE

## Status
Accepted

## Date
$(date +%F)

## Context

-

## Decision

-

## Consequences

-

## Related

- [[Home]]
EOF

echo "[Obsidian] Created $FILE"
