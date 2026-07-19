#!/usr/bin/env bash
set -Eeuo pipefail

CMD="${1:-help}"

case "$CMD" in

bootstrap)
    .aios/runtime/bootstrap.sh
    ;;

validate)
    .aios/runtime/validator.sh
    ;;

memory)
    .aios/runtime/memory-loader.sh
    ;;

quality)
    .aios/runtime/quality-gate.sh
    ;;

sync)
    .aios/runtime/sync-memory.sh
    ;;

*)
cat <<EOF

AIOS Commands

bootstrap
validate
memory
quality
sync

EOF
;;

esac
