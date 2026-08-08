#!/usr/bin/env bash
set -Eeuo pipefail

########################################
# 1. Wire monitor into main.py
########################################

python3 - <<'PY'
from pathlib import Path
import re

p = Path("main.py")
text = p.read_text()

if "from core.dca_fill_monitor import monitor_dca_fills" not in text:
    text = text.replace(
        "from core.dca_lifecycle import",
        "from core.dca_fill_monitor import monitor_dca_fills\nfrom core.dca_lifecycle import",
    )

if "create_task(monitor_dca_fills())" not in text:

    text = re.sub(
        r"(asyncio\.create_task\(monitor_positions\(\)\))",
        r"""\1

    logger.info("Starting DCA Fill Monitor...")
    asyncio.create_task(monitor_dca_fills())
""",
        text,
        count=1,
    )

p.write_text(text)
print("✓ main.py patched")
PY

########################################
# 2. Fix executor source
########################################

python3 - <<'PY'
from pathlib import Path

p=Path("core/dca_fill_monitor.py")
text=p.read_text()

text=text.replace(
"executor = state.executor",
"""from core.app_context import app_context
        executor = app_context.executor"""
)

p.write_text(text)
print("✓ executor fixed")
PY

########################################
# 3. Startup reconciliation
########################################

python3 - <<'PY'
from pathlib import Path
import re

p=Path("core/dca_fill_monitor.py")
text=p.read_text()

if "await reconcile_dca_fills()" not in text:
    text=re.sub(
r"async def monitor_dca_fills\(\):",
"""async def monitor_dca_fills():""",
text,
count=1)

    text=text.replace(
'logger.info("DCA Fill Monitor started")',
'''logger.info("DCA Fill Monitor started")

    await reconcile_dca_fills()
'''
)

p.write_text(text)
print("✓ startup reconciliation")
PY

########################################
# 4. Compile
########################################

python3 -m py_compile \
main.py \
core/dca_fill_monitor.py

echo
echo "==================================="
echo "Production DCA Patch Installed"
echo "==================================="

