import asyncio
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
