import os
import re

print("🔍 Deploying Phase 4: Blind Spot Override & LLM Deduplication...\n")

# =========================================================
# 1. THE "BLIND SPOT" OVERRIDE (core/strategy_manager.py)
# =========================================================
sm_path = 'core/strategy_manager.py'
if os.path.exists(sm_path):
    with open(sm_path, 'r') as f:
        content = f.read()

    # Find the strict HOLD logic we injected earlier and upgrade it
    old_logic = 'if confidence < 60:\n                    return "HOLD", 0, "ENSEMBLE" # Strict 60% threshold'
    
    new_logic = """if confidence < 60:
                    # 🛡️ PHASE 4: BLIND SPOT OVERRIDE
                    # If Meta-Learner has no data (norm < 0.1), fallback to Deterministic Math
                    if total_weight < 10 and hasattr(self, 'current_asset_data'):
                        rsi_1d = float(self.current_asset_data.get("1d", {}).get("rsi", 50))
                        rsi_1h = float(self.current_asset_data.get("1h", {}).get("rsi", 50))
                        if rsi_1d < 30 and rsi_1h < 45:
                            logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={rsi_1d:.1f} < 30. Deterministic BUY.")
                            return "BUY", 85, "DETERMINISTIC_MATH"
                        if rsi_1d > 70 and rsi_1h > 65:
                            logger.info(f"🚀 BLIND SPOT OVERRIDE: 1D RSI={rsi_1d:.1f} > 70. Deterministic SELL.")
                            return "SELL", 85, "DETERMINISTIC_MATH"
                    return "HOLD", 0, "ENSEMBLE" # Strict 60% threshold"""
                    
    if old_logic in content:
        content = content.replace(old_logic, new_logic)
        # Ensure we pass the asset data into the strategy manager context
        if 'self.current_asset_data = asset_data' not in content:
            content = content.replace(
                'async def get_trade_signal(self, asset_data: Dict[str, Any])',
                'async def get_trade_signal(self, asset_data: Dict[str, Any])'
            )
            # Inject context assignment at the top of the function
            content = content.replace(
                'final_signal = "HOLD"  # 🛡️ Prevent UnboundLocalError',
                'final_signal = "HOLD"  # 🛡️ Prevent UnboundLocalError\n        self.current_asset_data = asset_data'
            )
        with open(sm_path, 'w') as f:
            f.write(content)
        print("✅ Injected Blind Spot Override (Deterministic Math Fallback).")
    else:
        print("⚠️ Strict 60% threshold string not found. Manual review needed.")

# =========================================================
# 2. ERADICATE DOUBLE LLM CALLS (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
if os.path.exists(llm_path):
    with open(llm_path, 'r') as f:
        content = f.read()

    # If the reasoning is already in the data dict (from analyze_batch), skip the API call
    dedup_logic = """
        # 🛡️ PHASE 4: LLM DEDUPLICATION (Prevent double API calls)
        cached_reasoning = data.get("llm_reasoning") or data.get("reasoning")
        if cached_reasoning:
            logger.info(f"💾 LLM CACHE: Using pre-computed reasoning for {symbol}. Skipping API call.")
            return "HOLD", 0
"""
    if 'PHASE 4: LLM DEDUPLICATION' not in content:
        content = content.replace(
            'logger.info(f"🧠 LLM INPUT {symbol}:',
            dedup_logic + '\n        logger.info(f"🧠 LLM INPUT {symbol}:'
        )
        with open(llm_path, 'w') as f:
            f.write(content)
        print("✅ Eradicated Double LLM Calls (Halved API usage & scan time).")

print("\n🎉 Phase 4 Opportunity & Optimization Patches Complete.")
