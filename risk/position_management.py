from typing import List, Dict, Any
from config.config_loader import load_config
from core.signal_engine import calculate_atr
from state.state_manager import state
from risk.sizing import exact_size

def unrealised_pnl(position: dict, data: dict) -> float:
    entry = position["entry_px"]
    cur = data["midPx"]
    side = position["side"]
    if side == "LONG":
        return (cur - entry) / entry * 100
    else:
        return (entry - cur) / entry * 100

def create_close_action(position: dict, pnl_pct: float, reason: str) -> Dict:
    side = position["side"]
    return {
        "coin": position["coin"],
        "decision": "SELL" if side == "LONG" else "BUY",
        "size": position["size"],
        "is_market": True,
        "closing": True,
        "pnl": pnl_pct,
        "reason": reason,
    }

def check_atr_stops(position: dict, data: dict, actions: List[Dict]):
    coin = position["coin"]
    if coin in state.sl_tp:
        sl_info = state.sl_tp[coin]
        if sl_info.get("side") != position["side"]:
            return False
        cur_price = data["midPx"]
        side = position["side"]
        pnl_pct = unrealised_pnl(position, data)

        if side == "LONG":
            if cur_price <= sl_info["sl"]:
                actions.append(create_close_action(position, pnl_pct, "atr_stop_loss"))
                return True
            if cur_price >= sl_info["tp"]:
                actions.append(create_close_action(position, pnl_pct, "atr_take_profit"))
                return True
        else:
            if cur_price >= sl_info["sl"]:
                actions.append(create_close_action(position, pnl_pct, "atr_stop_loss"))
                return True
            if cur_price <= sl_info["tp"]:
                actions.append(create_close_action(position, pnl_pct, "atr_take_profit"))
                return True
    return False

def check_hard_stops(position: dict, data: dict, actions: List[Dict]):
    coin = position["coin"]
    pnl_pct = unrealised_pnl(position, data)
    config = load_config()

    if pnl_pct <= config["risk"]["emergency_stop_loss_pct"]:
        actions.append(create_close_action(position, pnl_pct, "emergency_stop_loss"))
        return True

    if pnl_pct <= -config["risk"]["stop_loss"]:
        actions.append(create_close_action(position, pnl_pct, "stop_loss"))
        return True
    return False

def check_trailing_stop(position: dict, data: dict, actions: List[Dict]):
    coin = position["coin"]
    cur_price = data["midPx"]
    entry = position["entry_px"]
    side = position["side"]
    pnl_pct = unrealised_pnl(position, data)

    # Activate trailing stop only after 3% profit
    if pnl_pct >= 3.0:
        watermark = state.position_watermarks.get(coin, entry)
        # Update watermark
        if side == "LONG":
            if cur_price > watermark:
                state.position_watermarks[coin] = cur_price
            # Trail by 1.5% below watermark
            if cur_price <= state.position_watermarks[coin] * 0.985:
                actions.append(create_close_action(position, pnl_pct, "trailing_stop"))
                return True
        else:
            if cur_price < watermark:
                state.position_watermarks[coin] = cur_price
            if cur_price >= state.position_watermarks[coin] * 1.015:
                actions.append(create_close_action(position, pnl_pct, "trailing_stop"))
                return True
    return False

def check_time_exit(position: dict, data: dict, cycle: int, actions: List[Dict]):
    coin = position["coin"]
    entry_cycle = state.position_entry_cycle.get(coin)
    if entry_cycle is None:
        return False
    hold_cycles = cycle - entry_cycle
    if hold_cycles >= 90:   # 90 minutes
        pnl_pct = unrealised_pnl(position, data)
        actions.append(create_close_action(position, pnl_pct, "time_stop"))
        return True
    return False

def check_partial_exits(position: dict, data: dict, actions: List[Dict]):
    # We no longer use partial exits in this strategy – return False
    return False

def apply_all_exits(open_positions: List[Dict], all_data: Dict, cycle: int, macro_bias: str) -> List[Dict]:
    actions = []
    for pos in open_positions:
        coin = pos["coin"]
        if coin not in all_data:
            continue
        data = all_data[coin]
        if check_atr_stops(pos, data, actions): continue
        if check_hard_stops(pos, data, actions): continue
        if check_trailing_stop(pos, data, actions): continue
        if check_time_exit(pos, data, cycle, actions): continue
        if check_partial_exits(pos, data, actions): continue
    return actions
