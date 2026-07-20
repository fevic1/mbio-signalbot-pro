#!/usr/bin/env bash
set -Eeuo pipefail

echo "[Health]"

echo "Git:"
git rev-parse --short HEAD

echo

echo "Python:"
python3 --version

echo

echo "Disk:"
df -h /

echo

echo "Memory:"
free -h

echo

echo "Health OK"
