import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Layer 1: Regex to catch the duplicated/mangled line and fix it
pattern = r'^(\s*)sm_signal,\s*sm_conf,\s*sm_strategy\s*=\s*await\s*sm\.\s+sm_signal,\s*sm_conf,\s*sm_strategy\s*=\s*await\s*sm\.get_trade_signal\(data\)'
replacement = r"\1if isinstance(data, dict): data['asset_name'] = str(asset_name)\n\1sm_signal, sm_conf, sm_strategy = await sm.get_trade_signal(data)"

new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

if count > 0:
    with open(path, 'w') as f:
        f.write(new_content)
    print(f"✅ Successfully repaired {count} mangled line(s) via Regex.")
else:
    # Layer 2: Brute-force literal string replacement from the exact error log
    print("⚠️ Regex missed. Attempting brute-force string replacement...")
    bad_str = "sm_signal, sm_conf, sm_strategy = await sm.                sm_signal, sm_conf, sm_strategy = await sm.get_trade_signal(data)"
    if bad_str in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if bad_str in line:
                indent = line[:len(line) - len(line.lstrip())]
                lines[i] = f"{indent}if isinstance(data, dict): data['asset_name'] = str(asset_name)\n{indent}sm_signal, sm_conf, sm_strategy = await sm.get_trade_signal(data)"
        with open(path, 'w') as f:
            f.write('\n'.join(lines))
        print("✅ Brute-force repair successful.")
    else:
        print("❌ Failed to locate the mangled string.")
