#!/usr/bin/env python3
"""Idempotent, fail-closed wiring for the adaptive DCA supervisor."""

from pathlib import Path

MAIN = Path("main.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if not MAIN.exists():
        raise SystemExit("main.py not found")

    text = MAIN.read_text(encoding="utf-8")
    if "adaptive_dca_supervisor_loop" in text and '("adaptive_dca", adaptive_dca_supervisor_loop())' in text:
        print("Adaptive DCA supervisor already wired; no changes required.")
        return

    import_block = """from monitoring.position_tracker import (
    entry_scanner_loop, full_analysis_loop,
    position_monitor_loop, quick_signal_scanner,
    update_trailing_dca, monitor_dca_profit_targets,
    monitor_grid_bots)
"""
    new_import_block = """from monitoring.position_tracker import (
    entry_scanner_loop, full_analysis_loop,
    position_monitor_loop, quick_signal_scanner,
    monitor_dca_profit_targets,
    monitor_grid_bots)
from monitoring.adaptive_dca_supervisor import adaptive_dca_supervisor_loop
"""
    text = replace_once(
        text, import_block, new_import_block, "position-tracker import block"
    )

    task_marker = '        ("trailing_dca", update_trailing_dca()),\n'
    text = replace_once(
        text,
        task_marker,
        '        ("adaptive_dca", adaptive_dca_supervisor_loop()),\n',
        "background task registration",
    )

    tmp = MAIN.with_suffix(".py.adaptive_dca_tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(MAIN)
    print("Adaptive DCA supervisor wired into main.py.")


if __name__ == "__main__":
    main()
