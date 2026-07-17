import yaml
import os
import re

print("🔍 Wiring Risk & Sizing Logic to strategy_config.yaml...\n")

# 1. Update the YAML Configuration
yaml_path = 'config/strategy_config.yaml'
with open(yaml_path, 'r') as f:
    cfg = yaml.safe_load(f) or {}

if 'execution' not in cfg:
    cfg['execution'] = {}

# Set dynamic risk parameters optimized for small accounts
if 'risk_per_trade_pct' not in cfg['execution']:
    cfg['execution']['risk_per_trade_pct'] = 0.05  # 5% risk per trade (Better for $100 account)
if 'default_notional' not in cfg['execution']:
    cfg['execution']['default_notional'] = 20.0    # $20 fallback notional size

with open(yaml_path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
print("✅ Updated strategy_config.yaml with risk_per_trade_pct and default_notional.")

# 2. Rewrite main.py Brute Force Sizing to read from YAML
main_path = 'main.py'
with open(main_path, 'r') as f:
    content = f.read()

# Replace the hardcoded 0.02 (2%) and 10.0 ($10) logic
content = re.sub(
    r'_risk_amt\s*=\s*_bal\s*\*\s*0\.02',
    '_risk_pct = __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)\n                                    _risk_amt = _bal * _risk_pct',
    content
)

content = re.sub(
    r'_size\s*=\s*10\.0\s*/\s*_entry',
    '_default_notional = __import__("config_loader").get_config().get("execution", {}).get("default_notional", 20.0)\n                                    _size = _default_notional / _entry',
    content
)

# Catch any other standard execution paths using 0.02
content = re.sub(
    r'(\w+)\s*\*\s*0\.02',
    r'\1 * __import__("config_loader").get_config().get("execution", {}).get("risk_per_trade_pct", 0.05)',
    content
)

with open(main_path, 'w') as f:
    f.write(content)
print("✅ Replaced hardcoded 2% risk and $10 fallback with dynamic YAML lookups.")

print("\n🎉 YAML-Driven Risk & Sizing Restored.")
