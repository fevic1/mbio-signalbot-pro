#!/usr/bin/env bash
set -Eeuo pipefail

echo
echo "[Validation]"

git rev-parse --git-dir >/dev/null

test -d .aios

test -f .aios/constitution.md

echo "Repository OK"
echo "AIOS OK"
