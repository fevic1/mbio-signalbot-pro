#!/usr/bin/env bash
set -Eeuo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -a
[[ -f "$DIR/../../.env" ]] && source "$DIR/../../.env"
set +a

. "$DIR/load-config.sh"
"$DIR/provider-manager.sh"
"$DIR/memory-manager.sh"
"$DIR/session-manager.sh"
"$DIR/agent-manager.sh"
"$DIR/health.sh"

echo
echo "=============================="
echo " AIOS ACTIVE"
echo "=============================="
