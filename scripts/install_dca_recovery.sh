#!/usr/bin/env bash
set -Eeuo pipefail

python3 - <<'PY'
from pathlib import Path

p = Path("core/dca_fill_monitor.py")
text = p.read_text()

if "async def recover_dca_positions()" not in text:

    recovery = '''

async def recover_dca_positions():
    logger.info("Recovering DCA positions from exchange...")

    from core.app_context import app_context

    executor = app_context.executor

    try:
        positions = await executor.get_open_positions()
        orders = await executor.get_open_orders()
    except Exception:
        logger.exception("Failed to fetch exchange state")
        return

    restored = 0

    for p in positions:

        coin = p.get("coin")

        if not coin:
            continue

        if coin not in state.OPEN_POSITIONS:
            state.OPEN_POSITIONS[coin] = {}

        pos = state.OPEN_POSITIONS[coin]

        pos["entry"] = float(
            p.get("entryPx", p.get("entry_price", 0))
        )

        pos["avg_entry"] = pos["entry"]

        pos["size"] = abs(
            float(
                p.get("szi", p.get("size", 0))
            )
        )

        pos.setdefault("side", "BUY")

        active = []

        for o in orders:

            if o.get("coin") != coin:
                continue

            active.append(
                {
                    "order_id": o.get("oid"),
                    "price": o.get("limitPx"),
                    "size": o.get("sz"),
                    "status": "OPEN",
                }
            )

        if active:

            pos["dca"] = {
                "active_orders": active,
                "filled_levels": [],
            }

            restored += 1

    state.save_positions()

    logger.info(
        "Recovered %d DCA position(s)",
        restored,
    )

'''

    text = text.replace(
        "async def monitor_dca_fills():",
        recovery + "\nasync def monitor_dca_fills():",
        1,
    )

    text = text.replace(
        'logger.info("DCA Fill Monitor started")',
        '''logger.info("DCA Fill Monitor started")

    await recover_dca_positions()
''',
        1,
    )

    p.write_text(text)

    print("✓ Startup DCA recovery installed")

else:
    print("Already installed")

PY

python3 -m py_compile core/dca_fill_monitor.py

echo
echo "✓ DCA startup recovery ready"

