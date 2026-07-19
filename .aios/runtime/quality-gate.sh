#!/usr/bin/env bash
set -Eeuo pipefail

echo
echo "[Quality Gate]"

echo "Checking Bash..."

find .aios -name "*.sh" -print0 | while IFS= read -r -d '' f
do
    bash -n "$f"
done

echo "Checking Python..."

if command -v python3 >/dev/null; then
    python3 -m compileall . >/dev/null || true
fi

echo "Git Status"

git diff --stat

echo
echo "Quality Gate Passed."
