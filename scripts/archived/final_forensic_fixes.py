import re
import os
import glob

print("🔍 Deploying Final Forensic Fixes...\n")

# =========================================================
# 1. AUTO-DISCOVER & FIX "UNKNOWN" SYMBOL (main.py)
# =========================================================
main_path = 'main.py'
if os.path.exists(main_path):
    with open(main_path, 'r') as f:
        content = f.read()

    # Find the exact line calling get_trade_signal
    match = re.search(r'get_trade_signal\(([a-zA-Z_0-9]+)\)', content)
    if match:
        var_in = match.group(1)
        print(f"🔍 Found get_trade_signal called with variable: '{var_in}'")
        
        idx = match.start()
        preceding_text = content[:idx]
        
        # Find the nearest 'for' loop to identify the asset name variable
        loops = list(re.finditer(r'for\s+([a-zA-Z_0-9_]+)(?:\s*,\s*([a-zA-Z_0-9_]+))?\s+in\s+', preceding_text))
        if loops:
            last_loop = loops[-1]
            v1 = last_loop.group(1)
            v2 = last_loop.group(2)
            
            # The asset name is usually the first variable (e.g., for asset, data in ...)
            asset_name_var = v1 if v2 else v1
            print(f"🔍 Nearest loop variables: '{v1}' and '{v2}'. Using '{asset_name_var}' as asset name.")
            
            # Find indentation of the target line
            line_start = content.rfind('\n', 0, match.start()) + 1
            indent = content[line_start:match.start()]
            
            # Inject the assignment right before the call
            injection = f"{var_in}['asset_name'] = str({asset_name_var})\n{indent}"
            new_content = content[:line_start] + indent + injection + content[line_start:]
            
            with open(main_path, 'w') as f:
                f.write(new_content)
            print(f"✅ SUCCESS: Injected `{var_in}['asset_name'] = {asset_name_var}` before get_trade_signal.")
        else:
            print("⚠️ Could not find preceding for-loop.")
    else:
        print("⚠️ Could not find get_trade_signal call.")

# =========================================================
# 2. GLOBAL GROQ RATE-LIMIT SHIELD (ai/groq_client.py)
# =========================================================
paths = glob.glob('ai/*.py') + glob.glob('core/*.py') + glob.glob('*.py')
target_file = None

for p in paths:
    try:
        with open(p, 'r') as f:
            c = f.read()
        if ('chat.completions' in c or 'Groq(' in c) and 'def ' in c:
            target_file = p
            break
    except: pass

if target_file:
    print(f"\n🔍 Found root Groq client at: {target_file}")
    with open(target_file, 'r') as f:
        content = f.read()
        
    if 'Global Rate-Limit Shield' not in content:
        # Look for the main analysis/chat method
        match = re.search(r'(def\s+[a-zA-Z_0-9]+\s*\([^)]*(?:asset|prompt|messages|symbol)[^)]*\)\s*[:]\s*\n)', content)
        if match:
            indent = '        ' # Standard method body indentation
            injection = f"{indent}# 🛡️ ARCHITECTURAL FIX: Global Rate-Limit Shield\n{indent}import time\n{indent}time.sleep(1.5)\n"
            content = content.replace(match.group(1), match.group(1) + injection, 1)
            with open(target_file, 'w') as f:
                f.write(content)
            print("✅ Injected Global Rate-Limit Shield (1.5s) into root Groq client.")
        else:
            print("⚠️ Could not find analyze/chat method in Groq client.")
    else:
        print("ℹ️ Global Rate-Limit Shield already present.")
else:
    print("\n⚠️ Could not locate root Groq client file.")

print("\n🎉 Final Forensic Fixes Complete.")
