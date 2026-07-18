#!/usr/bin/env bash
set -Eeuo pipefail

AIOS=".aios"

echo "===================================="
echo " Installing AIOS Enterprise"
echo "===================================="

DIRS=(
agents
architecture
commands
compatibility
governance
hooks
incidents
knowledge
memory
metrics
playbooks
prompts
research
reviews
runbooks
templates
workflows
)

for d in "${DIRS[@]}"; do
    mkdir -p "$AIOS/$d"
done

FILES=(
README.md
constitution.md
memory/project.md
memory/architecture.md
memory/api-spec.md
memory/coding-standards.md
memory/decisions.md
memory/project-state.md
memory/risk-policy.md
memory/product.md
memory/changelog.md
memory/known-bugs.md
memory/tech-debt.md
)

for f in "${FILES[@]}"; do
    touch "$AIOS/$f"
done

echo
echo "AIOS installed successfully."
echo

find "$AIOS" | sort
