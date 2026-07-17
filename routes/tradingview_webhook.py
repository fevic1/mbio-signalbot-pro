"""
TradingView Webhook Endpoint for MBIO SignalBot Pro v9.0
Receives JSON alerts from Pine Script strategies and routes to execution engine.
"""
import logging
from fastapi import APIRouter, Request
from core.state import OPEN_POSITIONS, save_state
import config_loader

logger = logging.getLogger(__name__)
router = APIRouter()

def normalize_symbol(raw_symbol: str) -> str:
    """Convert TradingView symbols (BTCUSDT, BINANCE:BTCUSDT) to bot format (BTC)."""
    s = raw_symbol.upper().strip()
    s = s.split(":")[-1]           # Strip exchange prefix
    for suffix in ["USDT", "USD", "BUSD", "USDC"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
            break
    return s

@router.post("/webhook/tradingview")
async def tradingview_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"❌ Webhook parse error: {e}")
        return {"status": "error", "message": str(e)}

    action = payload.get("action", "").lower()
    raw_symbol = payload.get("symbol", "")
    sl = payload.get("sl")
    tp = payload.get("tp")
    strategy_name = payload.get("strategy", "TradingView")

    coin = normalize_symbol(raw_symbol)
    logger.info(f"📡 WEBHOOK: {strategy_name} | {coin} | {action} | SL={sl} TP={tp}")

    # Check signal source mode
    cfg = config_loader.get_config()
    mode = cfg.get("execution", {}).get("signal_source", "internal")

    if mode == "internal":
        logger.info(f"⏭️ Webhook ignored: signal_source=internal")
        return {"status": "ignored", "reason": "internal mode active"}

    # Map actions to bot signals
    signal_map = {
        "buy": "BUY", "enter_long": "BUY",
        "sell": "SELL", "enter_short": "SELL",
        "close_long": "CLOSE_LONG", "close_short": "CLOSE_SHORT",
    }
    signal = signal_map.get(action)
    if not signal:
        logger.warning(f"⚠️ Unknown webhook action: {action}")
        return {"status": "error", "message": f"Unknown action: {action}"}

    # Conflict resolution: block opposing signals on same asset
    existing = OPEN_POSITIONS.get(coin)
    if existing and signal in ("BUY", "SELL"):
        ex_side = existing.get("side", "")
        if (signal == "BUY" and ex_side == "SELL") or (signal == "SELL" and ex_side == "BUY"):
            logger.warning(f"🛑 CONFLICT: {coin} has {ex_side} open. Blocking {signal}.")
            return {"status": "blocked", "reason": f"opposing {ex_side} position exists"}

    # Route to execution engine
    try:
        from main import _execute_trade
        result = _execute_trade(
            asset_name=coin,
            signal=signal,
            entry_price=float(payload.get("price", 0)),
            sl=float(sl) if sl else None,
            tp1=float(tp) if tp else None,
            tp2=None, tp3=None,
            size=0,  # Will be calculated by risk engine
            strategy=strategy_name,
            regime="WEBHOOK"
        )
        logger.info(f"✅ Webhook executed: {coin} {signal} via {strategy_name}")
        return {"status": "executed", "coin": coin, "signal": signal}
    except Exception as e:
        logger.error(f"❌ Webhook execution failed: {e}")
        return {"status": "error", "message": str(e)}
