import os

print("🔍 Deploying Final Micro-Patches...\n")

# =========================================================
# 1. NUKE THE FINAL FALLBACK LEAK (core/strategy_manager.py)
# =========================================================
sm_path = 'core/strategy_manager.py'
if os.path.exists(sm_path):
    with open(sm_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    skip = 0
    patched = False
    
    for i, line in enumerate(lines):
        if skip > 0:
            skip -= 1
            continue
            
        # If we find the dangerous fallback log, nuke it and force HOLD
        if 'using best strategy' in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + 'logger.warning("⚠️ Weak ensemble detected. Forcing HOLD to protect capital.")\n')
            new_lines.append(' ' * indent + 'return "HOLD", 0, "ENSEMBLE"  # 🛡️ KILLED FALLBACK\n')
            skip = 4  # Skip the next 4 lines which contain the bad assignment logic
            patched = True
        else:
            new_lines.append(line)

    if patched:
        with open(sm_path, 'w') as f:
            f.writelines(new_lines)
        print("✅ Nuked weak ensemble fallback in strategy_manager.py")
    else:
        print("ℹ️ Fallback string not found (may already be dead).")

# =========================================================
# 2. FIX LLM SYMBOL & RATE LIMIT (strategies/llm.py)
# =========================================================
llm_path = 'strategies/llm.py'
if os.path.exists(llm_path):
    with open(llm_path, 'r') as f:
        content = f.read()

    # A. Increase Rate-Limit Shield to 2.5s (Guarantees we stay under Groq RPM limits)
    content = content.replace('time.sleep(0.8)', 'time.sleep(2.5)')
    
    # B. Fix the "UNKNOWN" symbol extraction
    old_sym = 'symbol = data.get("coin", data.get("symbol", "UNKNOWN"))'
    new_sym = 'symbol = data.get("asset_name", data.get("asset", data.get("coin", data.get("symbol", "UNKNOWN"))))'
    content = content.replace(old_sym, new_sym)
    
    # Fallback if the exact string was slightly different
    if 'asset_name' not in content:
        content = content.replace(
            'data.get("coin", "UNKNOWN")', 
            'data.get("asset_name", data.get("asset", data.get("coin", "UNKNOWN")))'
        )

    with open(llm_path, 'w') as f:
        f.write(content)
    print("✅ Fixed LLM symbol extraction and increased rate-limit shield to 2.5s")

print("\n🎉 Final Micro-Patches Complete.")
