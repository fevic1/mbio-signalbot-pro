import os

print("🔍 Deploying Master Fixes: Blind Spot Override & LLM Deduplication...\n")

# =========================================================
# 1. BULLETPROOF BLIND SPOT OVERRIDE (core/strategy_manager.py)
# =========================================================
sm_path = 'core/strategy_manager.py'
if os.path.exists(sm_path):
    with open(sm_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    injected = False
    for line in lines:
        # Find the exact line where it forces HOLD
        if 'Forcing HOLD to protect capital' in line and not injected:
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Inject the RSI check right before the warning
            override = [
                f"{indent_str}# 🚀 PHASE 4: BLIND SPOT OVERRIDE (Deterministic Math Fallback)\n",
                f"{indent_str}_rsi_1d = float(asset_data.get('1d', {{}}).get('rsi', 50))\n",
                f"{indent_str}_rsi_1h = float(asset_data.get('1h', {{}}).get('rsi', 50))\n",
                f"{indent_str}if _rsi_1d < 30 and _rsi_1h < 45:\n",
                f"{indent_str}    logger.info(f'🚀 BLIND SPOT OVERRIDE: 1D RSI={{_rsi_1d:.1f}} < 30 & 1H RSI={{_rsi_1h:.1f}} < 45. Deterministic BUY.')\n",
                f"{indent_str}    return 'BUY', 85, 'DETERMINISTIC_MATH'\n",
                f"{indent_str}elif _rsi_1d > 70 and _rsi_1h > 65:\n",
                f"{indent_str}    logger.info(f'🚀 BLIND SPOT OVERRIDE: 1D RSI={{_rsi_1d:.1f}} > 70 & 1H RSI={{_rsi_1h:.1f}} > 65. Deterministic SELL.')\n",
                f"{indent_str}    return 'SELL', 85, 'DETERMINISTIC_MATH'\n"
            ]
            new_lines.extend(override)
            injected = True
        new_lines.append(line)
        
    if injected:
        with open(sm_path, 'w') as f:
            f.writelines(new_lines)
        print("✅ Bulletproof Blind Spot Override injected.")
    else:
        print("⚠️ Target line for Blind Spot not found.")

# =========================================================
# 2. ERADICATE DOUBLE LLM CALLS (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
dummy_code = '''import logging
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class LLMStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("LLM")

    async def calculate_signal(self, data: dict) -> tuple:
        # 🛡️ PHASE 4: LLM DEMOTED & DEDUPLICATED
        # The actual LLM analysis is handled by analyze_batch() in main.py for Telegram UI.
        # This strategy layer is strictly a dummy voter to prevent double API calls and rate limits.
        return "HOLD", 0
'''
with open(llm_path, 'w') as f:
    f.write(dummy_code)
print("✅ Eradicated Double LLM Calls (LLMStrategy is now a dummy voter).")

print("\n🎉 Master Fixes Complete.")
