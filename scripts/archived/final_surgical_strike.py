import os
import re

print("🔍 Deploying Final Surgical Strike...\n")

# =========================================================
# 1. FIX "UNKNOWN" SYMBOL IN ALL MAIN.PY LOOPS
# =========================================================
main_path = 'main.py'
if os.path.exists(main_path):
    with open(main_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    patched = 0
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Match ANY loop unpacking two variables: for X, Y in ...
        match = re.search(r'for\s+([a-zA-Z_0-9]+)\s*,\s*([a-zA-Z_0-9]+)\s+in\s+', line)
        if match:
            asset_var = match.group(1)
            data_var = match.group(2)
            indent = len(line) - len(line.lstrip()) + 4
            injection = ' ' * indent + f"if isinstance({data_var}, dict): {data_var}['asset_name'] = str({asset_var})\n"
            
            # Prevent double injection
            recent_text = ''.join(new_lines[-5:])
            if "['asset_name']" not in recent_text:
                new_lines.append(injection)
                patched += 1

    with open(main_path, 'w') as f:
        f.writelines(new_lines)
    print(f"✅ Injected asset_name mapping into {patched} loop(s) in main.py.")

# =========================================================
# 2. GLOBAL RATE-LIMIT SHIELD IN GROQ CLIENT
# =========================================================
groq_path = 'ai/groq_client.py'
if os.path.exists(groq_path):
    with open(groq_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    injected = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Target the first async method in the class (the main API caller)
        if not injected and re.match(r'\s*async\s+def\s+\w+\(self', line):
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                new_lines.append(lines[j])
                j += 1
            if j < len(lines):
                indent = len(lines[j]) - len(lines[j].lstrip())
                new_lines.append(' ' * indent + "import time; time.sleep(1.5)  # 🛡️ Global Rate-Limit Shield\n")
                injected = True
                
    with open(groq_path, 'w') as f:
        f.writelines(new_lines)
    if injected:
        print("✅ Injected 1.5s Rate-Limit Shield into ai/groq_client.py.")
    else:
        print("⚠️ Could not find async method in groq_client.py.")
else:
    print(f"❌ {groq_path} not found.")

print("\n🎉 Final Surgical Strike Complete.")
