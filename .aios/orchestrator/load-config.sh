#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CONFIG="$ROOT/config"

required=(
runtime.yaml
models.yaml
memory.yaml
agents.yaml
project.yaml
obsidian.yaml
)

echo "[Config]"

for f in "${required[@]}"; do
    if [[ ! -f "$CONFIG/$f" ]]; then
        echo "Missing $f"
        exit 1
    fi
done

export AIOS_ROOT="$ROOT"
export AIOS_CONFIG="$CONFIG"

echo "Configuration Loaded"
