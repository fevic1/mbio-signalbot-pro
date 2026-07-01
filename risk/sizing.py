from decimal import Decimal, ROUND_UP
from typing import Tuple
from config.config_loader import load_config
from core.signal_engine import calculate_atr
from state import state

def get_volatility_multiplier(coin: str) -> float:
    config = load_config()
    multipliers = config["risk"]["volatility_multipliers"]
    return multipliers.get(coin, multipliers["default"])

def exact_size(size: float, sz_dec: int) -> float:
    return float(Decimal(str(size)).quantize(Decimal("1." + "0" * sz_dec)))

def round_up_size(size: float, sz_dec: int) -> float:
    d = Decimal(str(size))
    quant = Decimal("1." + "0" * sz_dec)
    return float(d.quantize(quant, rounding=ROUND_UP))

def compute_order_size_with_rr(
    account_value: float,
    price: float,
    atr_pct: float,
    sz_dec: int,
    coin: str,
    free_collateral: float,
    decision_side: str,
) -> Tuple[float, float, float, float]:
    """
    Returns: size, order_usd, sl_price, tp_price
    """
    config = load_config()
    risk_pct = 0.015 if coin == "XAU" else config["trading"]["base_risk_per_trade"]
    max_risk_abs = config["trading"]["max_risk_absolute"]
    risk_usd = min(account_value * risk_pct, max_risk_abs)

    vol_mult = get_volatility_multiplier(coin)
    sl_distance = (atr_pct / 100) * vol_mult

    size = risk_usd / (price * sl_distance)

    max_order_value = min(account_value * config["trading"]["max_order_cap_pct"], max_risk_abs)
    max_size = max_order_value / price
    size = min(size, max_size)

    min_order_value = config["trading"]["min_order_value_usd"]
    min_size = min_order_value / price
    size = max(size, min_size)

    size = exact_size(size, sz_dec)
    order_usd = size * price

    min_free_buffer = account_value * config["trading"]["min_free_buffer_pct"]
    max_allowed_usage = free_collateral - min_free_buffer
    if max_allowed_usage < 0:
        return 0, 0, 0, 0
    if order_usd > max_allowed_usage:
        size = exact_size(max_allowed_usage / price, sz_dec)
        order_usd = size * price
        if order_usd < min_order_value:
            return 0, 0, 0, 0

    if order_usd > free_collateral * 0.35:
        return 0, 0, 0, 0
    if order_usd < min_order_value:
        return 0, 0, 0, 0

    rr_ratio = config["trading"]["rr_ratio"]
    if decision_side == "BUY":
        sl_price = price * (1 - sl_distance)
        tp_price = price * (1 + (sl_distance * rr_ratio))
    else:
        sl_price = price * (1 + sl_distance)
        tp_price = price * (1 - (sl_distance * rr_ratio))

    return size, order_usd, sl_price, tp_price
