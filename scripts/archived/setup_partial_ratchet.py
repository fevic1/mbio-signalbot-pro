import os

# 1. Math Engine (Partial Close Calculation)
with open('core/profit_ratchet.py', 'w') as f:
    f.write('''import json
import os
import logging

logger = logging.getLogger(__name__)
RATCHET_FILE = "ratchet_state.json"
TARGET_NET_PROFIT = 1.00
EXIT_FEE_PCT = 0.001  # 0.1% taker fee buffer for the partial exit

def is_ratchet_enabled():
    if not os.path.exists(RATCHET_FILE): return False
    try:
        with open(RATCHET_FILE, 'r') as f: return json.load(f).get("enabled", False)
    except: return False

def toggle_ratchet():
    enabled = is_ratchet_enabled()
    new_state = not enabled
    with open(RATCHET_FILE, 'w') as f: json.dump({"enabled": new_state}, f)
    return new_state

def calculate_partial_close_size(entry_price, current_price, side, target_net=1.0):
    """Calculates the exact size to close to yield $1.00 NET after exit fees."""
    if side.upper() == "BUY":
        diff = current_price - entry_price
    else:
        diff = entry_price - current_price
        
    if diff <= 0: return 0.0
    
    # Net profit per unit = price diff - exit fee
    net_per_unit = diff - (current_price * EXIT_FEE_PCT)
    if net_per_unit <= 0: return 0.0
    
    return target_net / net_per_unit
''')

# 2. Execution Loop (Partial Close + Move SL to Breakeven)
with open('monitoring/ratchet_loop.py', 'w') as f:
    f.write('''import asyncio
import logging
from core.profit_ratchet import is_ratchet_enabled, calculate_partial_close_size, TARGET_NET_PROFIT
from core.data_fetcher import get_current_price
import core.state as state

logger = logging.getLogger(__name__)

async def ratchet_monitor_loop():
    logger.info("🏹 Partial-Profit Ratchet Monitor started (checks every 15s)")
    while True:
        try:
            if is_ratchet_enabled():
                for asset, pos in list(state.OPEN_POSITIONS.items()):
                    if not isinstance(pos, dict) or "entry" not in pos or "size" not in pos: continue
                    if pos.get("ratchet_extracted"): continue # Only extract once per trade
                    
                    entry = float(pos.get("entry", 0))
                    size = float(pos.get("size", 0))
                    side = pos.get("side", "BUY")
                    exchange = pos.get("exchange", "hyperliquid")
                    
                    current_price = get_current_price(f"{asset}-USD")
                    if current_price <= 0: continue
                        
                    size_to_close = calculate_partial_close_size(entry, current_price, side, TARGET_NET_PROFIT)
                    max_closeable = size * 0.90  # Leave at least 10% for the bot to run to TP2/TP3
                    
                    if 0 < size_to_close <= max_closeable:
                        close_side = "SELL" if side == "BUY" else "BUY"
                        try:
                            from execution.exchange_router import route_order
                            result = route_order(
                                asset_name=asset,
                                side=close_side,
                                size=size_to_close,
                                reduce_only=True,
                                target_exchange=exchange
                            )
                            
                            if result and result.get("success"):
                                new_size = size - size_to_close
                                state.OPEN_POSITIONS[asset]["size"] = new_size
                                state.OPEN_POSITIONS[asset]["sl"] = entry # Move SL to Breakeven (Even)
                                state.OPEN_POSITIONS[asset]["ratchet_extracted"] = True
                                state.save_state()
                                logger.info(f"💰 RATCHET: Extracted $1 net from {asset}. Closed {size_to_close:.6f}. SL moved to Breakeven.")
                        except Exception as e:
                            logger.error(f"❌ Ratchet execution failed for {asset}: {e}")
        except Exception as e:
            logger.error(f"❌ Ratchet loop error: {e}")
        await asyncio.sleep(15)
''')

print("✅ Partial-Profit Ratchet logic successfully updated.")
