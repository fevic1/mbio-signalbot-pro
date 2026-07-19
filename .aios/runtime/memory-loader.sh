#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo
echo "[Memory]"

FILES=(
project.md
project-state.md
architecture.md
decisions.md
risk-policy.md
coding-standards.md
known-bugs.md
tech-debt.md
api-spec.md
product.md
)

for f in "${FILES[@]}"; do
    if [[ -f "$ROOT/memory/$f" ]]; then
        echo "Loaded $f"
    else
        echo "Missing $f"
    fi
done
