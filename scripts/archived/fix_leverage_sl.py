import yaml

# Fix run_trade() SL to respect leverage
path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

old_sl = '''    sl_atr_mult = tp.get("sl_atr_multiplier", 1.5)
    min_atr = tp.get("min_atr_pct", 0.02)
    sl_distance = entry_price * min_atr * sl_atr_mult'''

new_sl = '''    sl_atr_mult = tp.get("sl_atr_multiplier", 1.5)
    min_atr = tp.get("min_atr_pct", 0.02)
    sl_distance = entry_price * min_atr * sl_atr_mult

    # 🛡️ LEVERAGE GUARD: SL must never exceed safe margin distance
    _leverage = float(data.get("1h", {}).get("leverage", 20))
    _max_sl_pct = (1.0 / _leverage) * 0.4  # 40% of margin as max SL buffer
    _max_sl_distance = entry_price * _max_sl_pct
    if sl_distance > _max_sl_distance:
        logger.warning(f"⚠️ {asset_name} SL ${sl_distance:.2f} exceeds safe limit ${_max_sl_distance:.2f} at {_leverage}x. Capping.")
        sl_distance = _max_sl_distance'''

if old_sl in content:
    content = content.replace(old_sl, new_sl)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Fixed: SL now capped at 40% of margin for leverage safety")
else:
    print("⚠️ Could not find SL calculation block")

# Fix _sync_exchange_positions() to use same leverage-aware SL
old_sync_sl = '''            atr = entry * __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)
            if side == "BUY":
                sl = entry - (1.5 * atr)'''

new_sync_sl = '''            _lev = float(p.get("leverage", {}).get("value", 20)) if isinstance(p.get("leverage"), dict) else 20
            _safe_sl_pct = min(0.02 * 1.5, (1.0 / _lev) * 0.4)
            _sl_dist = entry * _safe_sl_pct
            if side == "BUY":
                sl = entry - _sl_dist'''

if old_sync_sl in content:
    content = content.replace(old_sync_sl, new_sync_sl)
    # Also fix the SELL side
    old_sell_sl = '''            else:
                sl = entry + (1.5 * atr)'''
    new_sell_sl = '''            else:
                sl = entry + _sl_dist'''
    content = content.replace(old_sell_sl, new_sell_sl)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Fixed: Sync SL now uses leverage-aware calculation")
else:
    print("⚠️ Could not find sync SL block")
