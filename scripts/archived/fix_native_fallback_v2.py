path = 'main.py'
with open(path, 'r') as f:
    lines = f.readlines()

# Find the native strategy gating block and replace it
new_lines = []
skip_until_else = False
injected = False

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Detect start of native strategy gating block
    if 'if _native_strategy:' in stripped and not injected:
        # Look ahead to confirm this is the gating block (not Slot Hunter)
        lookahead = ''.join(lines[i:i+5])
        if '_ns_signal, _ns_conf = _native_strategy.calculate_signal' in lookahead:
            # Inject AI-first supplementary logic
            indent = len(line) - len(line.lstrip())
            sp = ' ' * indent
            sp1 = ' ' * (indent + 4)
            sp2 = ' ' * (indent + 8)
            
            new_lines.append(f'{sp}# Get AI Batch signal FIRST (always available as baseline)\n')
            new_lines.append(f'{sp}result = results.get(asset_name) or {{}}\n')
            new_lines.append(f'{sp}signal = result.get("signal", "HOLD")\n')
            new_lines.append(f'{sp}conf = result.get("confidence", 50)\n')
            new_lines.append(f'{sp}reason = result.get("reasoning", "")\n')
            new_lines.append(f'\n')
            new_lines.append(f'{sp}# Native strategy SUPPLEMENTS AI — overrides when active, falls through when HOLD\n')
            new_lines.append(f'{sp}if _native_strategy:\n')
            new_lines.append(f'{sp1}try:\n')
            new_lines.append(f'{sp2}_ns_signal, _ns_conf = _native_strategy.calculate_signal(data)\n')
            new_lines.append(f'{sp2}if _ns_signal != "HOLD" and _ns_conf >= 70:\n')
            new_lines.append(f'{sp2}    signal = _ns_signal\n')
            new_lines.append(f'{sp2}    conf = _ns_conf\n')
            new_lines.append(f'{sp2}    reason = f"Native: {{_active_strat_id}}"\n')
            new_lines.append(f'{sp2}    logger.info(f"📐 NATIVE SIGNAL: {{asset_name}} | {{_ns_signal}} ({{_ns_conf}}%) via {{_active_strat_id}}")\n')
            new_lines.append(f'{sp2}else:\n')
            new_lines.append(f'{sp2}    logger.info(f"📐 NATIVE HOLD: {{asset_name}} via {{_active_strat_id}} → falling through to AI ({{signal}} {{conf}}%)")\n')
            new_lines.append(f'{sp1}except Exception as _ns_err:\n')
            new_lines.append(f'{sp2}logger.error(f"❌ Native strategy error on {{asset_name}}: {{_ns_err}} → falling through to AI")\n')
            new_lines.append(f'{sp}# If no native strategy configured, AI signal already set above\n')
            
            # Skip old block until we hit the else: or next major block
            skip_until_else = True
            injected = True
            continue
    
    if skip_until_else:
        # Skip lines until we find the closing else: of the old if/else block
        # or the "# Fallback: AI Batch" comment
        if '# Fallback: AI Batch analysis' in stripped:
            skip_until_else = False
            continue  # Skip this line too since we already handle AI above
        elif stripped.startswith('else:') and 'Fallback' in ''.join(lines[i:i+3]):
            skip_until_else = False
            continue
        else:
            continue  # Skip old block lines
    
    new_lines.append(line)

with open(path, 'w') as f:
    f.writelines(new_lines)

if injected:
    print("✅ Fixed: Native strategy now supplements AI instead of gating it")
else:
    print("⚠️ Could not find native strategy gating block")
