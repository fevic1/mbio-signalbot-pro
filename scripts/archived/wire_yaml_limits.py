import yaml
import os

print("🔍 Wiring Hardcoded Limits to strategy_config.yaml...\n")

# 1. Update the YAML Configuration
yaml_path = 'config/strategy_config.yaml'
with open(yaml_path, 'r') as f:
    cfg = yaml.safe_load(f) or {}

if 'execution' not in cfg:
    cfg['execution'] = {}

# Set default institutional limits if they don't exist
if 'max_positions' not in cfg['execution']:
    cfg['execution']['max_positions'] = 3
if 'min_confidence' not in cfg['execution']:
    cfg['execution']['min_confidence'] = 70

with open(yaml_path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
print("✅ Updated strategy_config.yaml with execution.max_positions and min_confidence.")

# 2. Rewrite main.py to strictly obey the YAML
main_path = 'main.py'
with open(main_path, 'r') as f:
    content = f.read()

yaml_lookup = '__import__("config_loader").get_config().get("execution", {}).get("max_positions", 3)'

# Replace all hardcoded 3s and 2s related to OPEN_POSITIONS
content = content.replace('len(state.OPEN_POSITIONS) < 3', f'len(state.OPEN_POSITIONS) < {yaml_lookup}')
content = content.replace('len(_state.OPEN_POSITIONS) >= 3', f'len(_state.OPEN_POSITIONS) >= {yaml_lookup}')
content = content.replace('len(state.OPEN_POSITIONS) < 2', f'len(state.OPEN_POSITIONS) < {yaml_lookup}')
content = content.replace('len(_state.OPEN_POSITIONS) >= 2', f'len(_state.OPEN_POSITIONS) >= {yaml_lookup}')

with open(main_path, 'w') as f:
    f.write(content)
print("✅ Rewired main.py to dynamically read max_positions from YAML.")

print("\n🎉 YAML-Driven Capacity Restored.")
