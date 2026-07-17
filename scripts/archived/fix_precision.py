with open('execution/hl_executor.py', 'r') as f:
    content = f.read()

# Add precision constants after imports
precision_code = '''
# Hyperliquid precision rules
ASSET_PRECISION = {
    'BTC': {'sz_decimals': 4, 'tick_size': 1.0},
    'ETH': {'sz_decimals': 3, 'tick_size': 0.1},
    'SOL': {'sz_decimals': 2, 'tick_size': 0.01},
    'XRP': {'sz_decimals': 1, 'tick_size': 0.0001},
    'DOGE': {'sz_decimals': 0, 'tick_size': 0.00001},
}

def round_price(asset, price):
    """Round price to valid tick size."""
    if asset not in ASSET_PRECISION:
        return price
    tick = ASSET_PRECISION[asset]['tick_size']
    return round(price / tick) * tick

def round_size(asset, size):
    """Round size to valid decimals."""
    if asset not in ASSET_PRECISION:
        return size
    decimals = ASSET_PRECISION[asset]['sz_decimals']
    return round(size, decimals)
'''

if 'ASSET_PRECISION' not in content:
    # Insert after imports, before first class/function
    import_end = content.find('class HLExecutor')
    if import_end == -1:
        import_end = content.find('def ')
    
    if import_end != -1:
        content = content[:import_end] + precision_code + '\n' + content[import_end:]
        print("✅ Added precision constants")

# Add rounding before order placement
if 'round_price(coin, px)' not in content:
    # Find the order placement and add rounding
    old_order = 'result = self.exchange.order(coin, is_buy, sz, px,'
    new_order = '''# Apply precision rounding
        px = round_price(coin, px)
        sz = round_size(coin, sz)
        logger.info(f"🎯 Rounded: {coin} price={px} size={sz}")
        
        result = self.exchange.order(coin, is_buy, sz, px,'''
    
    if old_order in content:
        content = content.replace(old_order, new_order)
        print("✅ Added precision rounding to order placement")

with open('execution/hl_executor.py', 'w') as f:
    f.write(content)
