import re

with open('main.py', 'r') as f:
    content = f.read()

# A. Add _check_btc_trend function before _hard_news_filter
btc_trend_code = """
# ============================================
# 📉 BTC TREND FILTER (Market Regime Check)
# ============================================
async def _check_btc_trend() -> bool:
    \"\"\"Returns False if BTC is in a strong downtrend (prevents altcoin longs).\"\"\"
    try:
        btc_data = await asyncio.wait_for(get_mtf_data("BTC-USD"), timeout=10.0)
        if not btc_data or '1h' not in btc_data: return True
        
        rsi_1h = btc_data['1h'].get('rsi', 50)
        rsi_4h = btc_data.get('4h', {}).get('rsi', 50)
        price = btc_data['1h'].get('price', 0)
        
        # Hard veto: If BTC 4H RSI is extremely oversold (< 30), market might be crashing
        if rsi_4h < 30:
            logger.warning(f"🛑 BTC 4H RSI is {rsi_4h:.1f} (Crash Risk). Blocking trades.")
            return False
        return True
    except Exception as e:
        logger.warning(f"⚠️ BTC Trend check failed (proceeding): {e}")
        return True

"""

if '_check_btc_trend' not in content and 'async def _hard_news_filter' in content:
    content = content.replace('async def _hard_news_filter', btc_trend_code + 'async def _hard_news_filter')
    print("   ✅ Added _check_btc_trend function")

# B. Wire it up in run_trade (before Hard News Filter)
if 'await _check_btc_trend()' not in content:
    content = content.replace(
        'if not await _hard_news_filter(asset_name, signal):',
        'if not await _check_btc_trend(): return\n        if not await _hard_news_filter(asset_name, signal):'
    )
    print("   ✅ Wired _check_btc_trend into run_trade")

# C. Add Debug Log before send_signal in analyze_tier
if 'DEBUG: Sending signal' not in content:
    content = content.replace(
        'await send_signal(asset_name, data, signal, conf, reason, trade_plan, provider, TELEGRAM_CHAT_ID)',
        'logger.info(f"📤 DEBUG: Sending signal for {asset_name} (Signal: {signal}, Conf: {conf})")\n                await send_signal(asset_name, data, signal, conf, reason, trade_plan, provider, TELEGRAM_CHAT_ID)'
    )
    print("   ✅ Added debug log for Telegram sending")

with open('main.py', 'w') as f:
    f.write(content)
