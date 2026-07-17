import os

path = 'monitoring/position_tracker.py'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
injected = False

target_str = 'logger.info(f"🔍 Checking {len(state.OPEN_POSITIONS)} open positions...")'

telemetry_code = """
{indent}# 🛡️ ARCHITECTURAL FIX: Institutional Position Telemetry
{indent}from datetime import datetime
{indent}try:
{indent}    from core.data_fetcher import get_current_price
{indent}except ImportError:
{indent}    pass
{indent}_now_ts = datetime.now().timestamp()
{indent}for _asset, _pos in list(state.OPEN_POSITIONS.items()):
{indent}    _entry = float(_pos.get("entry", 0))
{indent}    _size = float(_pos.get("size", 0))
{indent}    _side = _pos.get("side", "BUY")
{indent}    _sl = float(_pos.get("sl", 0))
{indent}    _created = _pos.get("created_at", _now_ts)
{indent}    _age_hrs = (_now_ts - _created) / 3600
{indent}    try:
{indent}        _current = get_current_price(f"{{_asset}}-USD")
{indent}        _pnl_pct = ((_current - _entry) / _entry * 100) if _side == "BUY" else ((_entry - _current) / _entry * 100)
{indent}        _r_mult = _pnl_pct / 2.0  # Approximate R-multiple based on 2% risk unit
{indent}        logger.info(f"📊 TELEMETRY: {{_asset}} {{_side}} | Entry: ${{_entry:.4f}} | Current: ${{_current:.4f}} | PnL: {{_pnl_pct:+.2f}}% | R: {{_r_mult:+.2f}} | SL: ${{_sl:.4f}} | Age: {{_age_hrs:.1f}}h")
{indent}    except Exception:
{indent}        logger.info(f"📊 TELEMETRY: {{_asset}} {{_side}} | Entry: ${{_entry:.4f}} | SL: ${{_sl:.4f}} | Age: {{_age_hrs:.1f}}h (Price fetch failed)")
"""

for line in lines:
    new_lines.append(line)
    if target_str in line and not injected:
        # Calculate exact indentation of the target line
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        new_lines.append(telemetry_code.format(indent=indent_str))
        injected = True

if injected:
    with open(path, 'w') as f:
        f.writelines(new_lines)
    print("✅ Successfully injected Institutional Position Telemetry.")
else:
    print("⚠️ Target string not found. Manual review required.")
