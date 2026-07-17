import os

path = 'core/strategy_manager.py'
if not os.path.exists(path):
    print(f"❌ {path} not found.")
    exit(1)

with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
injected = False

for line in lines:
    # Find the exact log line where the final vote is printed
    if 'Ensemble Vote:' in line and 'logger.info' in line and not injected:
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        override = [
            f"{indent_str}# 🚀 PHASE 4: BLIND SPOT OVERRIDE (Deterministic Dip-Buyer)\n",
            f"{indent_str}if final_signal == 'HOLD' or conf < 60:\n",
            f"{indent_str}    try:\n",
            f"{indent_str}        _rsi_1d = float(asset_data.get('1d', {{}}).get('rsi', 50))\n",
            f"{indent_str}        _rsi_1h = float(asset_data.get('1h', {{}}).get('rsi', 50))\n",
            f"{indent_str}        if _rsi_1d < 35 and _rsi_1h < 55:\n",
            f"{indent_str}            logger.info(f'🚀 BLIND SPOT OVERRIDE: 1D RSI={{_rsi_1d:.1f}} < 35 & 1H RSI={{_rsi_1h:.1f}} < 55. Deterministic BUY.')\n",
            f"{indent_str}            final_signal, conf, winner = 'BUY', 85, 'DETERMINISTIC_MATH'\n",
            f"{indent_str}        elif _rsi_1d > 70 and _rsi_1h > 65:\n",
            f"{indent_str}            logger.info(f'🚀 BLIND SPOT OVERRIDE: 1D RSI={{_rsi_1d:.1f}} > 70 & 1H RSI={{_rsi_1h:.1f}} > 65. Deterministic SELL.')\n",
            f"{indent_str}            final_signal, conf, winner = 'SELL', 85, 'DETERMINISTIC_MATH'\n",
            f"{indent_str}    except Exception:\n",
            f"{indent_str}        pass\n"
        ]
        new_lines.extend(override)
        injected = True
        
    new_lines.append(line)

if injected:
    with open(path, 'w') as f:
        f.writelines(new_lines)
    print("✅ Successfully injected Blind Spot Override via Line-by-Line Parser.")
else:
    print("❌ Failed to find 'Ensemble Vote:' log line. The file structure may have changed.")
