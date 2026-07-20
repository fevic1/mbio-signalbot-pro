#!/usr/bin/env bash
set -Eeuo pipefail

echo "[Providers]"

providers=(
GROQ_API_KEY
GROQ_API_KEY_1
GROQ_API_KEY_2
GROQ_API_KEY_3
CEREBRAS_API_KEY
OPENROUTER_API_KEY
ANTHROPIC_API_KEY
)

for p in "${providers[@]}"; do
    if [[ -n "${!p:-}" ]]; then
        echo "✓ $p"
    else
        echo "- $p"
    fi
done
