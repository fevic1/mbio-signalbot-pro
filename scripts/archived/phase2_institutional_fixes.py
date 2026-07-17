import os
import re

print("🔍 Starting Phase 2: Institutional Core Rectification...\n")

# =========================================================
# 1. FIX ENSEMBLE & META-LEARNER COLLAPSE (core/strategy_manager.py)
# =========================================================
strat_path = 'core/strategy_manager.py'
if os.path.exists(strat_path):
    with open(strat_path, 'r') as f:
        content = f.read()

    # A. Intercept Meta-Learner Weight Collapse
    # If weights sum to < 0.5, force a uniform distribution so the committee actually votes
    weight_intercept = """
        # 🛡️ ARCHITECTURAL FIX: Prevent Meta-Learner Weight Collapse
        if not weights or sum(weights.values()) < 0.5:
            weights = {name: 1.0 for name in self.strategies.keys()}
            logger.warning("⚠️ Meta-Learner weights collapsed. Forcing uniform committee distribution.")
"""
    if 'ARCHITECTURAL FIX: Prevent Meta-Learner' not in content:
        content = content.replace(
            'weights = self.meta.get_weights(self.current_regime)',
            'weights = self.meta.get_weights(self.current_regime)\n' + weight_intercept
        )

    # B. Inject Strict Majority Voting Logic (Audit Exact Fix)
    # Replace the weak fallback logic with strict 60% consensus requirement
    strict_voting = """
            # 🛡️ ARCHITECTURAL FIX: Strict Ensemble Majority Vote
            votes = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
            for res in results:
                if isinstance(res, tuple) and len(res) >= 2:
                    sig, conf = res[0], res[1]
                    if sig in votes: votes[sig] += conf
            
            total_weight = sum(votes.values())
            if total_weight > 0:
                winner = max(votes, key=votes.get)
                confidence = int((votes[winner] / total_weight) * 100)
                if confidence < 60:
                    return "HOLD", 0, "ENSEMBLE" # Strict 60% threshold
                return winner, confidence, "ENSEMBLE"
            return "HOLD", 0, "ENSEMBLE"
"""
    # Find the end of the strategy gathering loop and inject the voting logic
    if 'Strict Ensemble Majority Vote' not in content:
        # We look for the sniper override or the return statement at the end of the function
        content = re.sub(
            r'(if sniper_signal:.*?return sniper_signal\n)',
            r'\1' + strict_voting,
            content,
            flags=re.DOTALL
        )
        # Fallback injection if regex misses
        if 'Strict Ensemble Majority Vote' not in content:
             content = content.replace(
                 'return best_signal, best_confidence, used_strategy',
                 strict_voting + '\n        # return best_signal, best_confidence, used_strategy'
             )

    with open(strat_path, 'w') as f:
        f.write(content)
    print("✅ Fixed Ensemble Logic & Meta-Learner Collapse.")
else:
    print(f"❌ {strat_path} not found.")

# =========================================================
# 2. DEMOTE LLM & LOG INPUTS (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
if os.path.exists(llm_path):
    with open(llm_path, 'r') as f:
        content = f.read()

    # Inject Prompt Logging and Demote Voting
    llm_patch = """
        # 🛡️ ARCHITECTURAL FIX: Log LLM Inputs & Demote to Analyst
        logger.info(f"🧠 LLM INPUT {data.get('symbol', 'UNKNOWN')}: 1H RSI={data.get('1h', {}).get('rsi', 'N/A')}, 4H RSI={data.get('4h', {}).get('rsi', 'N/A')}, 1D RSI={data.get('1d', {}).get('rsi', 'N/A')}")
        
        # Execute LLM call for reasoning only...
"""
    if 'ARCHITECTURAL FIX: Log LLM Inputs' not in content:
        # Inject right before the LLM API call
        content = content.replace(
            'response =', 
            llm_patch + '\n        response ='
        )
        
        # Force the LLM to return HOLD for voting, but keep the reasoning
        content = content.replace(
            'return signal, confidence',
            'return "HOLD", 0  # 🛡️ LLM DEMOTED: Analyst only, no voting'
        )
        
        with open(llm_path, 'w') as f:
            f.write(content)
        print("✅ Demoted LLM to Analyst-Only & Enabled Prompt Logging.")
else:
    print(f"❌ {llm_path} not found.")

# =========================================================
# 3. INSTITUTIONAL POSITION TELEMETRY (monitoring/position_tracker.py)
# =========================================================
tracker_path = 'monitoring/position_tracker.py'
if os.path.exists(tracker_path):
    with open(tracker_path, 'r') as f:
        content = f.read()

    telemetry_block = """
            # 🛡️ ARCHITECTURAL FIX: Institutional Position Telemetry
            from datetime import datetime
            for asset, pos in state.OPEN_POSITIONS.items():
                entry = float(pos.get("entry", 0))
                size = float(pos.get("size", 0))
                side = pos.get("side", "BUY")
                sl = float(pos.get("sl", 0))
                created = pos.get("created_at", datetime.now().timestamp())
                age_hrs = (datetime.now().timestamp() - created) / 3600
                
                try:
                    current = get_current_price(f"{asset}-USD")
                    pnl_pct = ((current - entry) / entry * 100) if side == "BUY" else ((entry - current) / entry * 100)
                    r_multiple = pnl_pct / 2.0 if side == "BUY" else pnl_pct / 2.0 # Approximate R
                    logger.info(f"📊 TELEMETRY: {asset} {side} | Entry: ${entry:.4f} | Current: ${current:.4f} | PnL: {pnl_pct:+.2f}% | R: {r_multiple:+.2f} | SL: ${sl:.4f} | Age: {age_hrs:.1f}h")
                except Exception as e:
                    logger.info(f"📊 TELEMETRY: {asset} {side} | Entry: ${entry:.4f} | SL: ${sl:.4f} | Age: {age_hrs:.1f}h (Price fetch failed)")
"""
    if 'ARCHITECTURAL FIX: Institutional Position Telemetry' not in content:
        content = content.replace(
            'logger.info(f"🔍 Checking {len(positions)} open positions...")',
            'logger.info(f"🔍 Checking {len(positions)} open positions...")\n' + telemetry_block
        )
        with open(tracker_path, 'w') as f:
            f.write(content)
        print("✅ Upgraded Position Monitor to Institutional Telemetry.")
else:
    print(f"❌ {tracker_path} not found.")

print("\n🎉 Phase 2 Core Rectification Complete.")
