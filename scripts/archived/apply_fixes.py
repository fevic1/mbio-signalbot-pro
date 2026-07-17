import re

# ============================================================================
# FIX 1: Add precision handling to execution/hl_executor.py
# ============================================================================
with open('execution/hl_executor.py', 'r') as f:
    lines = f.readlines()

# Find where to insert precision constants (after imports, before first class)
insert_idx = 0
for i, line in enumerate(lines):
    if 'class HLExecutor' in line or 'def execute_hl_order' in line:
        insert_idx = i
        break

# Insert precision constants
precision_lines = [
    "\n",
    "# Hyperliquid precision rules\n",
    "ASSET_PRECISION = {\n",
    "    'BTC': {'sz_decimals': 4, 'tick_size': 1.0},\n",
    "    'ETH': {'sz_decimals': 3, 'tick_size': 0.1},\n",
    "    'SOL': {'sz_decimals': 2, 'tick_size': 0.01},\n",
    "    'XRP': {'sz_decimals': 1, 'tick_size': 0.0001},\n",
    "    'DOGE': {'sz_decimals': 0, 'tick_size': 0.00001},\n",
    "}\n",
    "\n",
    "def round_price(asset, price):\n",
    "    if asset not in ASSET_PRECISION:\n",
    "        return price\n",
    "    tick = ASSET_PRECISION[asset]['tick_size']\n",
    "    return round(price / tick) * tick\n",
    "\n",
    "def round_size(asset, size):\n",
    "    if asset not in ASSET_PRECISION:\n",
    "        return size\n",
    "    decimals = ASSET_PRECISION[asset]['sz_decimals']\n",
    "    return round(size, decimals)\n",
    "\n"
]

lines = lines[:insert_idx] + precision_lines + lines[insert_idx:]

# Find and update the place_order function to use rounding
content = ''.join(lines)

# Add rounding before exchange.order call
old_pattern = r'(result = self\.exchange\.order\(coin, is_buy, sz, px,)'
new_code = '''# Apply precision rounding
            px = round_price(coin, px)
            sz = round_size(coin, sz)
            logger.info(f"🎯 Rounded: {coin} price={px} size={sz}")
            
            result = self.exchange.order(coin, is_buy, sz, px,'''

content = re.sub(old_pattern, new_code, content)

with open('execution/hl_executor.py', 'w') as f:
    f.write(content)

print("✅ Fixed precision handling")

# ============================================================================
# FIX 2: Reduce sleep time in config
# ============================================================================
with open('config/strategy_config.yaml', 'r') as f:
    config = f.read()

config = config.replace('full_analysis_hours: 2', 'full_analysis_hours: 0.5')

with open('config/strategy_config.yaml', 'w') as f:
    f.write(config)

print("✅ Reduced analysis cycle to 30 minutes")

print("\n✅ All fixes applied!")
