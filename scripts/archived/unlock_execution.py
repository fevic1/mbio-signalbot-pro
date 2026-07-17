import os
import re
import yaml

print("🔍 Unlocking Execution & Injecting Diagnostics...\n")

# 1. Force min_confidence to 80 in config
cfg_path = 'config/strategy_config.yaml'
if os.path.exists(cfg_path):
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    
    updated = False
    if cfg.get('min_confidence', 100) > 80:
        cfg['min_confidence'] = 80
        updated = True
    if 'execution' in cfg and cfg['execution'].get('min_confidence', 100) > 80:
        cfg['execution']['min_confidence'] = 80
        updated = True
        
    if updated:
        with open(cfg_path, 'w') as f:
            yaml.dump(cfg, f)
        print("✅ Lowered min_confidence to 80 in strategy_config.yaml")

# 2. Inject Diagnostic Trace into main.py
main_path = 'main.py'
with open(main_path, 'r') as f:
    content = f.read()

# Find the exact line where signal is unpacked
pattern = r'([a-zA-Z_0-9]+)\s*,\s*([a-zA-Z_0-9]+)\s*,\s*([a-zA-Z_0-9]+)\s*=\s*await\s*sm\.get_trade_signal\(data\)'
match = re.search(pattern, content)

if match and '🔍 DIAGNOSTIC TRACE' not in content:
    v1, v2, v3 = match.group(1), match.group(2), match.group(3)
    indent = ' ' * 12 # Standard loop indentation
    
    trace = f"\n{indent}# 🔍 DIAGNOSTIC TRACE\n{indent}_min_conf = locals().get('effective_min_conf', locals().get('min_conf', 'N/A'))\n{indent}logger.info(f'🔍 DIAGNOSTIC: {{asset_name}} | Signal: {{{v1}}} | Conf: {{{v2}}} | Strategy: {{{v3}}} | MinConf: {{_min_conf}}')\n"
    
    content = content.replace(match.group(0), match.group(0) + trace)
    with open(main_path, 'w') as f:
        f.write(content)
    print(f"✅ Injected Diagnostic Trace (tracking variables: {v1}, {v2}, {v3})")
else:
    print("⚠️ Diagnostic trace already present or unpacking pattern not found.")

print("\n🎉 Diagnostics Ready.")
