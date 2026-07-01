import json
import os
import logging

logger = logging.getLogger(__name__)
RATCHET_FILE = "ratchet_state.json"
TARGET_NET_PROFIT = 1.00
EXIT_FEE_PCT = 0.001  # 0.1% taker fee buffer for the partial exit

def is_ratchet_enabled():
    if not os.path.exists(RATCHET_FILE): return False
    try:
        with open(RATCHET_FILE, 'r') as f: return json.load(f).get("enabled", False)
    except: return False

def toggle_ratchet():
    enabled = is_ratchet_enabled()
    new_state = not enabled
    with open(RATCHET_FILE, 'w') as f: json.dump({"enabled": new_state}, f)
    return new_state

def calculate_partial_close_size(entry_price, current_price, side, target_net=1.0):
    """Calculates the exact size to close to yield $1.00 NET after exit fees."""
    if side.upper() == "BUY":
        diff = current_price - entry_price
    else:
        diff = entry_price - current_price
        
    if diff <= 0: return 0.0
    
    # Net profit per unit = price diff - exit fee
    net_per_unit = diff - (current_price * EXIT_FEE_PCT)
    if net_per_unit <= 0: return 0.0
    
    return target_net / net_per_unit
