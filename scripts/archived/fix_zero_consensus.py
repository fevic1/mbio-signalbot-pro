import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Inject Zero-Consensus Fallback
fallback_logic = """
                # 🚀 ZERO-CONSENSUS FALLBACK (Audit Fix: Trust AI when Ensemble is 0%)
                if sm_conf == 0 and signal != "HOLD" and conf >= 80:
                    sm_signal = signal
                    sm_conf = conf
                    sm_strategy = "AI_BATCH_FALLBACK"
                    logger.info(f"🚀 ZERO-CONSENSUS FALLBACK: Ensemble 0%. Trusting AI Batch ({signal} {conf}%).")
"""

target = 'sm_signal, sm_conf, sm_strategy = await sm.get_trade_signal(data)'
if target in content and 'ZERO-CONSENSUS FALLBACK' not in content:
    content = content.replace(target, target + fallback_logic)
    print("✅ Injected Zero-Consensus Fallback.")
else:
    print("ℹ️ Fallback already present or target missed.")

# 2. Update Ghost Filter Bypass to include AI_BATCH_FALLBACK
old_bypass = 'if sm_strategy == "MeanReversion" or sm_strategy == "DETERMINISTIC_MATH":'
new_bypass = 'if sm_strategy in ["MeanReversion", "DETERMINISTIC_MATH", "AI_BATCH_FALLBACK"]:'

if old_bypass in content:
    content = content.replace(old_bypass, new_bypass)
    print("✅ Updated Ghost Filter Bypass to include AI_BATCH_FALLBACK.")

# 3. Fallback Regex in case the exact string varies slightly
content = re.sub(
    r'if sm_strategy == ["\']MeanReversion["\'] or sm_strategy == ["\']DETERMINISTIC_MATH["\']:',
    'if sm_strategy in ["MeanReversion", "DETERMINISTIC_MATH", "AI_BATCH_FALLBACK"]:',
    content
)

with open(path, 'w') as f:
    f.write(content)

print("\n🎉 Zero-Consensus Fix Complete.")
