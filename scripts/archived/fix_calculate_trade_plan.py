with open('main.py', 'r') as f:
    content = f.read()

# Fix line 264 - add signal parameter
old_call_264 = '_tp_s = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"])'
new_call_264 = '_tp_s = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"], signal)'

if old_call_264 in content:
    content = content.replace(old_call_264, new_call_264)
    print("✅ Fixed line 264 - added signal parameter")

# Also fix line 234 if it has the same issue
old_call_234 = '_tp_c = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"])'
new_call_234 = '_tp_c = calculate_trade_plan(get_account_balance(), data["1h"]["price"], data["1h"]["atr"], signal)'

if old_call_234 in content:
    content = content.replace(old_call_234, new_call_234)
    print("✅ Fixed line 234 - added signal parameter")

with open('main.py', 'w') as f:
    f.write(content)

print("✅ All calculate_trade_plan calls fixed")
