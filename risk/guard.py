import time
from config.config_loader import load_config
from state.state_manager import state
from alerts.telegram_bot import send_telegram

class PerformanceGuard:
    def __init__(self):
        self.trade_results = []
        self.consecutive_losses_limit = 5

    def record(self, pnl: float):
        # Only count a trade as a loss if it actually lost more than a cent
        if pnl <= -0.01:
            self.trade_results.append(False)
        else:
            self.trade_results.append(True)
        if len(self.trade_results) > 20:
            self.trade_results.pop(0)

    def allow_trading(self) -> bool:
        if len(self.trade_results) < self.consecutive_losses_limit:
            return True
        last_n = self.trade_results[-self.consecutive_losses_limit:]
        if all(not x for x in last_n):
            print(f"🔴 {self.consecutive_losses_limit} consecutive losses — pausing")
            return False
        return True

guard = PerformanceGuard()

def emergency_monitor():
    # Wait a few seconds so main loop can initialise PnL tracking
    time.sleep(10)
    state.hour_start_pnl = state.total_realised_pnl
    state.hour_start_time = time.time()

    while True:
        time.sleep(300)   # check every 5 minutes
        drop = state.hour_start_pnl - state.total_realised_pnl

        # Only trigger if the actual dollar loss exceeds $5 (≈5% of the account)
        if drop > 5.0:
            state.emergency_brake_active = True
            send_telegram(f"🚨 EMERGENCY BRAKE ACTIVATED: lost ${drop:.2f} in the last hour")
            print(f"🚨 EMERGENCY BRAKE ACTIVATED: PnL dropped ${drop:.2f}")

        # Reset the baseline every hour
        if time.time() - state.hour_start_time >= 3600:
            state.hour_start_pnl = state.total_realised_pnl
            state.hour_start_time = time.time()

def liquidation_monitor(open_positions, all_data, account_value):
    config = load_config()
    actions = []
    if state.emergency_brake_active:
        for pos in open_positions:
            actions.append({
                "coin": pos["coin"],
                "decision": "SELL" if pos["side"] == "LONG" else "BUY",
                "size": pos["size"],
                "is_market": True,
                "closing": True,
                "pnl": 0,
                "reason": "emergency_brake",
            })
        if open_positions:
            send_telegram("🚨 EMERGENCY BRAKE: All positions closed")
        state.emergency_brake_active = False
        return actions

    for pos in open_positions:
        coin = pos["coin"]
        if coin not in all_data:
            continue
        cur_price = all_data[coin]["midPx"]
        entry = pos["entry_px"]
        side = pos["side"]
        size = pos["size"]
        position_value = size * entry

        if coin not in state.position_watermarks:
            state.position_watermarks[coin] = entry
        if side == "LONG":
            state.position_watermarks[coin] = max(state.position_watermarks[coin], cur_price)
        else:
            state.position_watermarks[coin] = min(state.position_watermarks[coin], cur_price)

        liq_price_raw = pos.get("liquidationPx")
        if liq_price_raw and float(liq_price_raw) > 0:
            liq_price = float(liq_price_raw)
        else:
            n_pos = max(len(open_positions), 1)
            collateral_used = account_value / n_pos
            liq_price = compute_liquidation_price(side, entry, position_value, collateral_used)

        liq_dist = compute_liq_distance_pct(side, cur_price, liq_price)

        log_line = f"   {coin} ({side}): price=${cur_price:.4f}, liq=${liq_price:.4f}, dist={liq_dist*100:.1f}%"
        if liq_dist < config["risk"]["liquidation_monitor"]["min_liq_distance_emergency"]:
            print(f"🆘 EMERGENCY CLOSE {log_line}")
            send_telegram(f"🆘 EMERGENCY: {coin} {side} liquidation in {liq_dist*100:.1f}%! Closing now.")
            actions.append({
                "coin": coin,
                "decision": "SELL" if side == "LONG" else "BUY",
                "size": size,
                "is_market": True,
                "closing": True,
                "pnl": 0,
                "reason": "emergency_close",
            })
        elif liq_dist < config["risk"]["liquidation_monitor"]["liq_warning_threshold"]:
            print(f"⚠️  LIQ WARNING {log_line}")
            send_telegram(f"⚠️ LIQ WARNING: {coin} {side} is {liq_dist*100:.1f}% from liquidation.")
        else:
            print(f"✅ {log_line}")
    return actions

def compute_liquidation_price(side, entry_price, position_value, collateral_used, mmr=0.005):
    if collateral_used <= 0 or entry_price <= 0:
        return 0.0
    leverage = max(position_value / collateral_used, 1.0)
    if side == "LONG":
        return max(entry_price * (1 - (1 / leverage) + mmr), 0.0)
    else:
        return max(entry_price * (1 + (1 / leverage) - mmr), 0.0)

def compute_liq_distance_pct(side, current_price, liq_price):
    if liq_price <= 0 or current_price <= 0:
        return 1.0
    if side == "LONG":
        return (current_price - liq_price) / current_price
    else:
        return (liq_price - current_price) / current_price
