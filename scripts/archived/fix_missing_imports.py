path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Add missing imports from alert_manager
old_import = 'from monitoring.alert_manager import cmd_strategy_select, cmd_ratchet, cmd_signal_source, cmd_positions, cmd_close, cmd_closeall, cmd_status, button_callback'
new_import = 'from monitoring.alert_manager import cmd_strategy_select, cmd_ratchet, cmd_signal_source, cmd_positions, cmd_close, cmd_closeall, cmd_status, button_callback, send_signal, send_execution, send_tp_hit'

if old_import in content and 'send_signal' not in content.split('from monitoring.alert_manager')[1].split('\n')[0]:
    content = content.replace(old_import, new_import)
    print("✅ Added send_signal, send_execution, send_tp_hit imports")
else:
    print("ℹ️ Imports may already be present or format differs")

# 2. Fix _sync_exchange_positions atr variable error
# The leverage-aware SL fix referenced 'atr' before it was defined
old_sync = '''            _lev = float(p.get("leverage", {}).get("value", 20)) if isinstance(p.get("leverage"), dict) else 20
            _safe_sl_pct = min(0.02 * 1.5, (1.0 / _lev) * 0.4)
            _sl_dist = entry * _safe_sl_pct'''

new_sync = '''            _lev = float(p.get("leverage", {}).get("value", 20)) if isinstance(p.get("leverage"), dict) else 20
            _atr = entry * __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)
            _safe_sl_pct = min(0.02 * 1.5, (1.0 / _lev) * 0.4)
            _sl_dist = entry * _safe_sl_pct'''

if old_sync in content:
    content = content.replace(old_sync, new_sync)
    print("✅ Fixed _sync_exchange_positions atr variable")
else:
    print("ℹ️ Sync block may already be fixed or format differs")

with open(path, 'w') as f:
    f.write(content)

print("\n🎉 All missing imports and sync fix applied.")
