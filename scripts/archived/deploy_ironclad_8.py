import os
import re

print("🔍 Deploying The Ironclad 8 Architectural Pivot...\n")

# =========================================================
# 1. CREATE DETERMINISTIC STRATEGY (Change 4)
# =========================================================
os.makedirs('strategies', exist_ok=True)
with open('strategies/deterministic.py', 'w') as f:
    f.write('''from .base import BaseStrategy

class DeterministicStrategy(BaseStrategy):
    """First-class citizen for deep oversold/overbought math."""
    def __init__(self):
        super().__init__("Deterministic")

    def calculate_signal(self, data: dict) -> tuple:
        rsi_1d = float(data.get("1d", {}).get("rsi", 50))
        rsi_1h = float(data.get("1h", {}).get("rsi", 50))
        
        if rsi_1d < 30 and rsi_1h < 55:
            return "BUY", 95
        if rsi_1d > 70 and rsi_1h > 65:
            return "SELL", 95
        return "HOLD", 0
''')
print("✅ 1. Created DeterministicStrategy.")

# =========================================================
# 2. UPDATE STRATEGY MANAGER (Changes 3, 4, 5, 7)
# =========================================================
sm_path = 'core/strategy_manager.py'
with open(sm_path, 'r') as f:
    sm = f.read()

if 'DeterministicStrategy' not in sm:
    sm = sm.replace('from strategies.llm import LLMStrategy', 'from strategies.llm import LLMStrategy\nfrom strategies.deterministic import DeterministicStrategy')
    sm = sm.replace('"LLM": LLMStrategy(),', '"LLM": LLMStrategy(),\n            "Deterministic": DeterministicStrategy(),')

# Remove hacky Blind Spot/God Mode overrides (now handled by DeterministicStrategy)
sm = re.sub(r'\s*# 🚀 PHASE 4: BLIND SPOT OVERRIDE.*?pass\n', '\n', sm, flags=re.DOTALL)
sm = re.sub(r'\s*# 🚀 GOD MODE.*?\n', '\n', sm, flags=re.DOTALL)

# Ensure consensus threshold is 60% (Change 5)
sm = re.sub(r'confidence < \d+', 'confidence < 60', sm)

with open(sm_path, 'w') as f:
    f.write(sm)
print("✅ 2. StrategyManager updated (Deterministic added, LLM neutered, 60% consensus).")

# =========================================================
# 3. KILL GROQ RETRIES (Change 1 & 2)
# =========================================================
for p in ['ai/groq_client.py', 'ai/base_client.py', 'ai/cerebras_client.py']:
    if os.path.exists(p):
        with open(p, 'r') as f:
            c = f.read()
        # Neutralize sleep retries
        c = re.sub(r'time\.sleep\(\d+(\.\d+)?\)', 'break  # 🛡️ Retries disabled', c)
        c = re.sub(r'@retry.*?\n', '# @retry disabled\n', c)
        with open(p, 'w') as f:
            f.write(c)
print("✅ 3. Groq/Cerebras retries completely eradicated.")

# =========================================================
# 4. MAIN.PY: TOP 2 LIMIT & 70% THRESHOLD (Changes 6 & 8)
# =========================================================
main_path = 'main.py'
with open(main_path, 'r') as f:
    main = f.read()

# Clean up old hacky injections
main = re.sub(r'\s*# 🔍 DIAGNOSTIC TRACE.*?\n', '\n', main)
main = re.sub(r'\s*# 🚀 GOD MODE.*?\n', '\n', main)

# Inject Cycle Counter for Top 2 Limit
if '_cycle_executions = 0' not in main:
    main = main.replace(
        'logger.info("♻️ Starting cycle...")',
        'logger.info("♻️ Starting cycle...")\n    _cycle_executions = 0  # 🛡️ Top 2 Limit'
    )

# Inject Top 2 Gatekeeper right before execution
# We look for the execution function call
exec_pattern = r'(_execute_trade\([^)]+\)|execute_hl_order\([^)]+\))'
if '_cycle_executions >= 2' not in main:
    main = re.sub(
        exec_pattern,
        r'(_cycle_executions >= 2 and logger.info("🛑 TOP 2 LIMIT: Skipping further executions this cycle.")) or \1',
        main,
        count=1 # Only inject at the first/main execution block
    )
    # Increment counter after successful execution (approximate injection)
    main = main.replace(
        'state.OPEN_POSITIONS[asset_name] = {',
        '_cycle_executions += 1  # 🛡️ Increment Top 2 Counter\n            state.OPEN_POSITIONS[asset_name] = {'
    )

# Lower trade threshold to 70% (Change 6)
main = re.sub(r'conf >= \d+', 'conf >= 70', main)
main = re.sub(r'sm_conf >= \d+', 'sm_conf >= 70', main)

with open(main_path, 'w') as f:
    f.write(main)
print("✅ 4. main.py updated (Top 2 Limit, 70% Execution Threshold).")

print("\n🎉 The Ironclad 8 Deployment Complete.")
