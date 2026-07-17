import os

print("🔍 Deploying Final Variable & Key Repairs...\n")

# =========================================================
# 1. FIX UnboundLocalError (core/strategy_manager.py)
# =========================================================
sm_path = 'core/strategy_manager.py'
if os.path.exists(sm_path):
    with open(sm_path, 'r') as f:
        content = f.read()

    target = 'async def get_trade_signal(self, asset_data: Dict[str, Any]) -> Tuple[str, int, str]:'
    if target in content and 'Prevent UnboundLocalError' not in content:
        content = content.replace(
            target,
            target + '\n        final_signal = "HOLD"  # 🛡️ Prevent UnboundLocalError\n        final_confidence = 0\n        used_strategy = "ENSEMBLE"'
        )
        with open(sm_path, 'w') as f:
            f.write(content)
        print("✅ Initialized final_signal to prevent UnboundLocalError.")
    else:
        # Fallback if it's not an async def
        target_sync = 'def get_trade_signal(self, asset_data: Dict[str, Any]) -> Tuple[str, int, str]:'
        if target_sync in content and 'Prevent UnboundLocalError' not in content:
            content = content.replace(
                target_sync,
                target_sync + '\n        final_signal = "HOLD"  # 🛡️ Prevent UnboundLocalError\n        final_confidence = 0\n        used_strategy = "ENSEMBLE"'
            )
            with open(sm_path, 'w') as f:
                f.write(content)
            print("✅ Initialized final_signal (sync) to prevent UnboundLocalError.")
        else:
            print("ℹ️ Target function not found or already patched.")

# =========================================================
# 2. EXPOSE LLM DATA KEYS (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
if os.path.exists(llm_path):
    with open(llm_path, 'r') as f:
        content = f.read()

    if 'LLM DATA KEYS' not in content:
        content = content.replace(
            'symbol = data.get("asset_name"',
            'logger.info(f"🧠 LLM DATA KEYS: {list(data.keys())}")\n        symbol = data.get("asset_name"'
        )
        with open(llm_path, 'w') as f:
            f.write(content)
        print("✅ Injected LLM data keys diagnostic logger.")
else:
    print(f"❌ {llm_path} not found.")

print("\n🎉 Final Repairs Complete.")
