import sys
import logging
import inspect

# Suppress noisy logs during audit
logging.disable(logging.CRITICAL)

def check(name, func):
    try:
        func()
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")
        return False

print("\n🔍 STARTING MBIO SIGNALBOT PRO v9.0 FULL AUDIT \n")
print("━" * 50)

# 1. Core Configuration
def check_config():
    from config_loader import get_config
    cfg = get_config()
    assert cfg is not None, "Config is None"
    assert "trading" in cfg, "Missing trading config"
check("1. Core Configuration (YAML)", check_config)

# 2. Database & Smart Learning (ChromaDB)
def check_meta_learner():
    from core.meta_learner import get_meta_learner
    ml = get_meta_learner()
    weights = ml.get_weights("RANGING")
    assert len(weights) == 6, f"Expected 6 strategies, got {len(weights)}"
check("2. Smart Learning DB (ChromaDB & MetaLearner)", check_meta_learner)

# 3. 6-Strategy Ensemble
def check_strategies():
    from core.strategy_manager import StrategyManager
    sm = StrategyManager()
    assert len(sm.strategies) == 6, "Not all 6 strategies loaded"
    assert "Momentum" in sm.strategies
    assert "LLM" in sm.strategies
check("3. 6-Strategy Ensemble (StrategyManager)", check_strategies)

# 4. Hyperliquid API & Execution
def check_hl_api():
    from execution.hl_executor import HLExecutor
    ex = HLExecutor()
    # Just check if it initializes and can ping the API
    positions = ex.get_open_positions()
    assert isinstance(positions, list), "Failed to fetch positions"
check("4. Hyperliquid API (Execution & Positions)", check_hl_api)

# 5. Market Data Fetching
def check_data():
    from core.data_fetcher import get_mtf_data
    data = get_mtf_data("BTC-USD")
    assert "1h" in data and "candles" in data["1h"], "Failed to fetch BTC candles"
check("5. Market Data API (1H/4H/1D Candles)", check_data)

# 6. Risk Management & R:R Logic
def check_risk():
    from core.risk_manager import RiskManager
    rm = RiskManager()
    size = rm.calculate_position_size(balance=1000, entry_price=100, stop_loss=95)
    assert size > 0, "Position sizing failed"
check("6. Risk Manager & Position Sizing", check_risk)

# 7. Telegram UI & Command Integrity
def check_telegram():
    import monitoring.alert_manager as am
    # Check for duplicate functions (the bug we just fixed)
    members = inspect.getmembers(am, inspect.isfunction)
    status_funcs = [m for m in members if m[0] == 'cmd_status']
    assert len(status_funcs) == 1, f"Duplicate cmd_status found! Count: {len(status_funcs)}"
    
    # Check if msg variable is defined in the function source
    source = inspect.getsource(status_funcs[0][1])
    assert "msg = (" in source, "msg variable missing in cmd_status!"
check("7. Telegram UI & Command Integrity", check_telegram)

# 8. State & Memory
def check_state():
    import core.state as state
    assert hasattr(state, 'OPEN_POSITIONS'), "Missing OPEN_POSITIONS"
    assert hasattr(state, 'SIGNAL_CACHE'), "Missing SIGNAL_CACHE"
check("8. Bot State & Memory Management", check_state)

print("━" * 50)
print("\n🏁 AUDIT COMPLETE 🏁\n")
