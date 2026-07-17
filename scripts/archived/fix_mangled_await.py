import re

path = 'main.py'
with open(path, 'r') as f:
    lines = f.readlines()

out = []
fixed = False

for line in lines:
    # Detect the exact mangled signature
    if "['asset_name'] = str(" in line and "= await" in line:
        m = re.search(r'^(\s*)(.*?)\s*=\s*await\s+(.*?)\.([a-zA-Z_0-9_]+)\[\'asset_name\'\]\s*=\s*str\((.*?)\)', line)
        if m:
            indent = m.group(1)
            lhs = m.group(2)       # e.g., sm_signal, sm_conf, sm_strategy
            obj = m.group(3)       # e.g., sm
            dict_var = m.group(4)  # e.g., data
            asset_var = m.group(5) # e.g., asset_name
            
            # Reconstruct the correct injection and original line
            injection = f"{indent}if isinstance({dict_var}, dict): {dict_var}['asset_name'] = str({asset_var})\n"
            original = f"{indent}{lhs} = await {obj}.get_trade_signal({dict_var})\n"
            
            out.append(injection)
            out.append(original)
            fixed = True
            continue
            
    out.append(line)

if fixed:
    with open(path, 'w') as f:
        f.writelines(out)
    print("✅ Successfully repaired mangled await assignment in main.py.")
else:
    print("⚠️ Mangled line not found. Manual inspection required.")
