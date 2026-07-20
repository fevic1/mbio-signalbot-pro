#!/usr/bin/env bash
set -Eeuo pipefail

echo "[Agents]"

COUNT=$(find "$AIOS_ROOT/agents" -name "*.md" | wc -l)

echo "$COUNT agents"

find "$AIOS_ROOT/agents" -name "*.md" | sort
