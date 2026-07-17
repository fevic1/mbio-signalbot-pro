import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Add import at module level (no indentation issues)
if 'from core.strategy_registry import' not in content:
    content = content.replace(
        'from core.strategy_manager import StrategyManager',
        'from core.strategy_manager import StrategyManager\nfrom core.strategy_registry import get_strategy_class'
    )

# Find the analyze_batch call and detect its EXACT indentation
match = re.search(r'^(\s+)DEBUG: analyze_batch returned:', content, re.MULTILINE)
if match and 'STRATEGY REGISTRY ACTIVE' not in content:
    indent = match.group(1)
    
    registry_block = f'''
{indent}# 🔄 STRATEGY REGISTRY ACTIVE
{indent}import config_loader as _cfg_loader
{indent}_active_strat_id = _cfg_loader.get_config().get("execution", {{}}).get("active_strategy", "internal")
{indent}_native_strategy = None
{indent}if _active_strat_id != "internal":
{indent}    _strat_cls = get_strategy_class(_active_strat_id)
{indent}    if _strat_cls:
{indent}        _native_strategy = _strat_cls()
{indent}        logger.info(f"📐 Using native strategy: {{_active_strat_id}} for {{asset_name}}")
{indent}if _native_strategy:
{indent}    try:
{indent}        _ns_signal, _ns_conf = _native_strategy.calculate_signal(data)
{indent}        if _ns_signal != "HOLD" and _ns_conf >= 70:
{indent}            sm_signal, sm_conf, sm_strategy = _ns_signal, _ns_conf, _active_strat_id
{indent}            logger.info(f"📐 NATIVE SIGNAL: {{asset_name}} | {{_ns_signal}} ({{_ns_conf}}%) via {{_active_strat_id}}")
{indent}        else:
{indent}            sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
{indent}    except Exception as _ns_err:
{indent}        logger.error(f"❌ Native strategy error on {{asset_name}}: {{_ns_err}}")
{indent}        sm_signal, sm_conf, sm_strategy = "HOLD", 0, _active_strat_id
{indent}else:
{indent}    # Fallback: AI Batch analysis (internal mode)
'''
    # Insert BEFORE the analyze_batch debug line
    insert_point = match.start()
    content = content[:insert_point] + registry_block + '\n' + content[insert_point:]
    
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Wired Strategy Registry with detected indent ({len(indent)} spaces).")
else:
    print("⚠️ Could not find analyze_batch marker or already wired.")
