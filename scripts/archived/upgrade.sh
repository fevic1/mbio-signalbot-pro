#!/bin/bash
set -e

echo "📦 Applying institutional upgrades (RiskGuard + ExecutionManager)..."

# 1. Create core/trade_signal.py
cat > core/trade_signal.py << 'EOF'
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class TradeSignal:
    asset: str
    side: str          # "BUY" or "SELL"
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    size: float
    confidence: int
    strategy_name: str
    timestamp: float
    extra: Dict[str, Any] = field(default_factory=dict)
EOF

# 2. Create core/execution_manager.py
cat > core/execution_manager.py << 'EOF'
import asyncio
import logging
from datetime import datetime, timezone
from core.trade_signal import TradeSignal
from core.state import OPEN_POSITIONS
from execution.hl_executor import execute_hl_order

logger = logging.getLogger(__name__)

class ExecutionManager:
    def __init__(self):
        self.pending_orders = []

    async def place_order(self, signal: TradeSignal) -> dict:
        logger.info(f"🛒 ExecutionManager: placing {signal.side} {signal.asset} {signal.size:.6f} @ {signal.entry_price:.2f}")
        result = await asyncio.to_thread(
            execute_hl_order,
            coin=signal.asset,
            side=signal.side,
            size=signal.size,
            limit_price=signal.entry_price
        )
        if result.get("success"):
            OPEN_POSITIONS[signal.asset] = {
                "side": signal.side,
                "entry": signal.entry_price,
                "size": signal.size,
                "sl": signal.stop_loss,
                "tp1": signal.take_profit_1,
                "tp2": signal.take_profit_2,
                "tp3": signal.take_profit_3,
                "order_id": result.get("order_id"),
                "opened_at": datetime.now(timezone.utc),
                "strategy": signal.strategy_name,
                "rsi": signal.extra.get("rsi"),
                "atr": signal.extra.get("atr"),
                "signal": signal.extra.get("signal_text", ""),
            }
        else:
            logger.error(f"❌ Order failed: {result.get('error')}")
        return result
EOF

# 3. Create core/risk_guard.py
cat > core/risk_guard.py << 'EOF'
import logging
from datetime import datetime, timedelta
from core.state import OPEN_POSITIONS
from config_loader import get_config
from core.data_fetcher import get_account_balance

logger = logging.getLogger(__name__)

class RiskGuard:
    def __init__(self):
        self.cfg = get_config().get("risk_guard", {})
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now()
        self.consecutive_losses = 0
        self.cooldown_until = None
        self.last_trade_time = datetime.now()

    def check(self, signal) -> tuple[bool, str]:
        self._reset_daily_pnl_if_needed()
        max_daily_loss = self.cfg.get("max_daily_loss_pct", -5.0)
        if self.daily_pnl <= max_daily_loss:
            return False, f"Daily loss limit reached ({self.daily_pnl:.2f}%)"

        max_losses = self.cfg.get("max_consecutive_losses", 3)
        cooldown_minutes = self.cfg.get("cooldown_minutes", 30)
        if self.consecutive_losses >= max_losses:
            if self.cooldown_until and datetime.now() < self.cooldown_until:
                return False, f"Cooldown active (consecutive losses: {self.consecutive_losses})"
            else:
                self.cooldown_until = None
                self.consecutive_losses = 0

        balance = get_account_balance()
        max_position_pct = self.cfg.get("max_position_pct", 0.5)
        if (signal.size * signal.entry_price) > balance * max_position_pct:
            return False, f"Position size {signal.size * signal.entry_price:.2f} exceeds {max_position_pct*100}% of balance"

        min_interval_sec = self.cfg.get("min_trade_interval_sec", 60)
        if (datetime.now() - self.last_trade_time).total_seconds() < min_interval_sec:
            return False, f"Trade too soon (last trade {int((datetime.now()-self.last_trade_time).total_seconds())}s ago)"

        max_positions = self.cfg.get("max_open_positions", 5)
        if len(OPEN_POSITIONS) >= max_positions:
            return False, f"Max open positions ({max_positions}) already reached"

        return True, "OK"

    def record_trade_outcome(self, pnl_pct: float):
        self.daily_pnl += pnl_pct
        if pnl_pct < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.cfg.get("max_consecutive_losses", 3):
                self.cooldown_until = datetime.now() + timedelta(minutes=self.cfg.get("cooldown_minutes", 30))
        else:
            self.consecutive_losses = 0
        self.last_trade_time = datetime.now()

    def _reset_daily_pnl_if_needed(self):
        if datetime.now().date() != self.daily_reset_time.date():
            self.daily_pnl = 0.0
            self.daily_reset_time = datetime.now()
EOF

# 4. Patch main.py: add imports and replace execution block
echo "📝 Patching main.py..."
python3 << 'PYTHON'
import re
with open('main.py', 'r') as f:
    content = f.read()

# Add imports if missing
if 'from core.trade_signal import TradeSignal' not in content:
    content = content.replace('from core.strategy_manager import StrategyManager',
                              'from core.strategy_manager import StrategyManager\nfrom core.trade_signal import TradeSignal\nfrom core.execution_manager import ExecutionManager\nfrom core.risk_guard import RiskGuard')

# Find the execution block and replace it
# We'll replace from "if ENABLE_AUTO_TRADING and size > 0:" to the end of that block.
# Simpler: replace the entire run_trade function? But we only want to change the execution part.
# We'll locate the line that says "if ENABLE_AUTO_TRADING and size > 0:" and replace from there to the next return/end.

# We'll use a safer approach: search for the existing execution block and replace with new code.
# The old block uses _execute_trade and manually updates state. We'll replace it with the new logic.

old_block = r'''if ENABLE_AUTO_TRADING and size > 0:
        logger\.info\(f"Executing {signal} {asset_name}\.\.\."\)
        order_response = _execute_trade\(asset_name, signal, entry_price, _sl, _tp1, _tp2, _tp3, size\)
        if order_response and order_response\.get\("success"\):
            order_id = order_response\.get\("order_id", "unknown"\)
            await send_execution\(asset_name, "BUY" if "BUY" in signal else "SELL",
                                 size, entry_price, _sl, _tp1, _tp2, _tp3, order_id, TELEGRAM_CHAT_ID\)
            state\.OPEN_POSITIONS\[asset_name\] = {
                "side": "BUY" if "BUY" in signal else "SELL",
                "entry": entry_price,
                "size": size,
                "sl": _sl,
                "tp1": _tp1,
                "tp2": _tp2,
                "tp3": _tp3,
                "order_id": order_id,
                "opened_at": datetime\.now\(timezone\.utc\),
                "strategy": strategy_name,
                "rsi": data\["1h"\]\["rsi"\],
                "atr": data\["1h"\]\["atr"\],
                "signal": signal,
            }'''

new_block = '''if ENABLE_AUTO_TRADING and size > 0:
        logger.info(f"Executing {signal} {asset_name}...")
        
        # Build trade signal
        trade_signal = TradeSignal(
            asset=asset_name,
            side="BUY" if "BUY" in signal else "SELL",
            entry_price=entry_price,
            stop_loss=_sl,
            take_profit_1=_tp1,
            take_profit_2=_tp2,
            take_profit_3=_tp3,
            size=size,
            confidence=conf,
            strategy_name=strategy_name,
            timestamp=time.time(),
            extra={"rsi": data["1h"]["rsi"], "atr": data["1h"]["atr"], "signal_text": signal}
        )
        
        # Risk Guard veto
        risk_guard = RiskGuard()
        allowed, reason = risk_guard.check(trade_signal)
        if not allowed:
            logger.warning(f"🚫 RiskGuard vetoed trade: {reason}")
            return
        
        # Execute
        exec_mgr = ExecutionManager()
        result = await exec_mgr.place_order(trade_signal)
        if result.get("success"):
            order_id = result.get("order_id", "unknown")
            await send_execution(asset_name, trade_signal.side,
                                 size, entry_price, _sl, _tp1, _tp2, _tp3, order_id, TELEGRAM_CHAT_ID)
            logger.info(f"✅ Trade executed: {asset_name}")
        else:
            logger.error(f"❌ Trade failed: {result.get('error')}")'''

content = re.sub(old_block, new_block, content, flags=re.DOTALL)
with open('main.py', 'w') as f:
    f.write(content)
print("✅ main.py patched.")
PYTHON

# 5. Patch position_tracker.py: add RiskGuard record_trade_outcome
echo "📝 Patching monitoring/position_tracker.py..."
python3 << 'PYTHON'
import re
with open('monitoring/position_tracker.py', 'r') as f:
    content = f.read()

# Add import if missing
if 'from core.risk_guard import RiskGuard' not in content:
    content = content.replace('from core.memory import store_trade',
                              'from core.memory import store_trade\nfrom core.risk_guard import RiskGuard')

# Find the place where pnl_pct is calculated and we call store_trade, then insert the risk_guard.record_trade_outcome.
# We'll insert after store_trade call (or after send_closure).
# We'll look for "store_trade(" and insert after it.
# Better: add it right after pnl_pct is calculated, before assets_to_remove.append(asset)
pattern = r'(assets_to_remove\.append\(asset\))'
replacement = r'''        # Record trade outcome for RiskGuard
        risk_guard = RiskGuard()
        risk_guard.record_trade_outcome(pnl_pct)
        \1'''
content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open('monitoring/position_tracker.py', 'w') as f:
    f.write(content)
print("✅ position_tracker.py patched.")
PYTHON

# 6. Add risk_guard config to strategy_config.yaml if not present
echo "📝 Adding risk_guard config to strategy_config.yaml..."
if ! grep -q "risk_guard:" config/strategy_config.yaml; then
    cat >> config/strategy_config.yaml << 'EOF'

risk_guard:
  max_daily_loss_pct: -5.0
  max_consecutive_losses: 3
  cooldown_minutes: 30
  max_position_pct: 0.5
  min_trade_interval_sec: 60
  max_open_positions: 5
EOF
fi

# 7. Copy all changed files into the container and restart
echo "📦 Copying files into container..."
docker compose cp core/trade_signal.py mbio-bot:/app/core/
docker compose cp core/execution_manager.py mbio-bot:/app/core/
docker compose cp core/risk_guard.py mbio-bot:/app/core/
docker compose cp main.py mbio-bot:/app/
docker compose cp monitoring/position_tracker.py mbio-bot:/app/monitoring/
docker compose cp config/strategy_config.yaml mbio-bot:/app/config/

echo "🔄 Restarting bot..."
docker compose restart mbio-bot

echo "✅ Institutional upgrades applied. Check logs with: docker compose logs -f mbio-bot"
