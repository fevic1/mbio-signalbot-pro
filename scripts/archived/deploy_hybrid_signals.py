import os
import re

print("🔍 Deploying Hybrid Signal Architecture...\n")

# =========================================================
# 1. CREATE WEBHOOK ROUTE FILE
# =========================================================
webhook_code = '''"""
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
'''

os.makedirs('routes', exist_ok=True)
with open('routes/tradingview_webhook.py', 'w') as f:
    f.write(webhook_code)
print("✅ Created routes/tradingview_webhook.py")

# =========================================================
# 2. REGISTER ROUTE IN MAIN.PY
# =========================================================
main_path = 'main.py'
with open(main_path, 'r') as f:
    main_content = f.read()

if 'tradingview_webhook' not in main_content:
    # Add import
    main_content = main_content.replace(
        'from fastapi import FastAPI',
        'from fastapi import FastAPI\nfrom routes.tradingview_webhook import router as tv_router'
    )
    # Register router after app creation
    main_content = main_content.replace(
        'app = FastAPI()',
        'app = FastAPI()\napp.include_router(tv_router)'
    )
    with open(main_path, 'w') as f:
        f.write(main_content)
    print("✅ Registered webhook route in main.py")

# =========================================================
# 3. ADD SIGNAL_SOURCE TO YAML CONFIG
# =========================================================
import yaml
yaml_path = 'config/strategy_config.yaml'
with open(yaml_path, 'r') as f:
    cfg = yaml.safe_load(f) or {}

if 'execution' not in cfg:
    cfg['execution'] = {}
if 'signal_source' not in cfg['execution']:
    cfg['execution']['signal_source'] = 'both'  # Options: internal, tradingview, both

with open(yaml_path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
print("✅ Added signal_source to strategy_config.yaml")

# =========================================================
# 4. ADD TELEGRAM TOGGLE COMMAND
# =========================================================
am_path = 'monitoring/alert_manager.py'
with open(am_path, 'r') as f:
    am_content = f.read()

if 'cmd_signal_source' not in am_content:
    toggle_cmd = '''

async def cmd_signal_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle signal source: internal / tradingview / both"""
    import yaml, config_loader
    args = context.args
    valid = ["internal", "tradingview", "both"]
    
    if args and args[0].lower() in valid:
        new_mode = args[0].lower()
    else:
        # Cycle through modes
        cfg = config_loader.get_config()
        current = cfg.get("execution", {}).get("signal_source", "both")
        idx = valid.index(current) if current in valid else 2
        new_mode = valid[(idx + 1) % len(valid)]
    
    # Update YAML
    yaml_path = "config/strategy_config.yaml"
    with open(yaml_path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("execution", {})["signal_source"] = new_mode
    with open(yaml_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
    
    icons = {"internal": "🧠", "tradingview": "📡", "both": "🔄"}
    msg = f"{icons.get(new_mode, '❓')} *Signal Source*\\n━━━━━━━━━━━━━━━━━━━━\\nMode: *{new_mode.upper()}*\\n\\n"
    if new_mode == "internal":
        msg += "Using only internal AI/Deterministic signals."
    elif new_mode == "tradingview":
        msg += "Using only TradingView webhook signals."
    else:
        msg += "Accepting signals from BOTH sources."
    await update.message.reply_text(msg, parse_mode="Markdown")
'''
    with open(am_path, 'a') as f:
        f.write(toggle_cmd)
    print("✅ Added /signalsource command to alert_manager.py")

# Register handler in main.py
if 'cmd_signal_source' not in main_content:
    with open(main_path, 'r') as f:
        main_content = f.read()
    main_content = main_content.replace(
        'from monitoring.alert_manager import',
        'from monitoring.alert_manager import cmd_signal_source,'
    )
    handler_match = re.search(r'(application\.add_handler\(CommandHandler\([^)]+\)\))', main_content)
    if handler_match:
        main_content = main_content.replace(
            handler_match.group(1),
            handler_match.group(1) + '\n    application.add_handler(CommandHandler("signalsource", cmd_signal_source))'
        )
    with open(main_path, 'w') as f:
        f.write(main_content)
    print("✅ Registered /signalsource handler in main.py")

print("\n🎉 Hybrid Signal Architecture Deployed.")
