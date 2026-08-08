#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

pass() {
    echo -e "${GREEN}✓${NC} $1"
    PASS=$((PASS+1))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    FAIL=$((FAIL+1))
}

section() {
    echo
    echo "===================================================="
    echo "$1"
    echo "===================================================="
}

run_test() {
    local name="$1"
    shift

    if "$@" >/tmp/mbio_test.log 2>&1; then
        pass "$name"
    else
        fail "$name"
        cat /tmp/mbio_test.log
    fi
}

section "MBIO SYSTEM HEALTH"

echo "Repository: $ROOT"

section "1. Python"

run_test "Python available" python3 --version

section "2. Syntax"

while IFS= read -r file
do
    python3 -m py_compile "$file"
done < <(find . -name "*.py" ! -path "*/.venv/*")

pass "All python modules compile"

section "3. Configuration"

run_test "Load configuration" python3 -c "
from config_loader import get_config
cfg=get_config()
assert cfg
"

section "4. Strategy Engine"

run_test "StrategyManager" python3 -c "
import asyncio
from core.strategy_manager import StrategyManager

async def t():
    sm=StrategyManager()
    d={
        '1h':{'price':100,'rsi':35,'atr':2,'volume_ratio':2},
        '4h':{'rsi':40},
        '1d':{'rsi':45}
    }
    print(await sm.get_trade_signal(d))

asyncio.run(t())
"

section "5. MetaLearner"

run_test "MetaLearner" python3 -c "
from core.meta_learner import MetaLearner
m=MetaLearner()
print(m.get_weights('TRENDING'))
"

section "6. Indicator Engine"

run_test "Indicator Engine" python3 -c "
from core.indicator_engine import fallback_indicators
print(fallback_indicators(100))
"

section "7. Candidate Ranking"

run_test "Asset Universe" python3 -c "
from core.asset_universe import SCAN_COIN_LIMIT
assert SCAN_COIN_LIMIT>0
"

section "8. LLM"

run_test "Signal Generator imports" python3 -c "
import core.signal_generator
"

section "9. Risk"

run_test "Risk Manager" python3 -c "
from core.risk_manager import RiskManager
RiskManager()
"

section "10. Trade Ledger"

run_test "Ledger" python3 -c "
from core.trade_ledger import load_history
load_history()
"

section "11. Grid"

run_test "Grid Manager imports" python3 -c "
import core.grid_manager
"

section "12. DCA"

run_test "DCA imports" python3 -c "
import core.dca_lifecycle
"

section "13. Monitoring"

run_test "Position Tracker" python3 -c "
import monitoring.position_tracker
"

section "14. Telegram"

python3 - <<'PY'
import os
if os.getenv("TELEGRAM_BOT_TOKEN"):
    print("Configured")
else:
    raise SystemExit(1)
PY

pass "Telegram configured"

section "15. Exchange"

python3 - <<'PY'
from executor import executor
print(executor.get_account_summary())
PY

pass "Exchange reachable"

section "16. AI Pipeline"

python3 - <<'PY'
from core.signal_generator import analyze_batch
print("Signal generator loaded")
PY

pass "AI pipeline"

section "17. Learning"

python3 - <<'PY'
from core.meta_learner import MetaLearner
m=MetaLearner()
print(m.get_best_strategy("TRENDING"))
PY

pass "Learning engine"

section "18. Memory"

python3 - <<'PY'
import aios
print("AIOS OK")
PY

pass "AIOS"

section "19. Scanner"

python3 - <<'PY'
from core.asset_universe import get_universe
u=get_universe()
print(len(list(u.signal_scanner_coins())))
PY

pass "Scanner"

section "20. Final"

echo
echo "Passed : $PASS"
echo "Failed : $FAIL"

if [ "$FAIL" -eq 0 ]; then
    echo
    echo "###############################################"
    echo "# MBIO SYSTEM STATUS : OPERATIONAL"
    echo "###############################################"
    exit 0
else
    echo
    echo "###############################################"
    echo "# MBIO SYSTEM STATUS : FAILED"
    echo "###############################################"
    exit 1
fi
