#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=================================="
echo " AIOS Runtime Bootstrap"
echo "=================================="

"$ROOT/runtime/context-loader.sh"
"$ROOT/runtime/memory-loader.sh"
"$ROOT/runtime/validator.sh"

echo
echo "AIOS Runtime Ready."
