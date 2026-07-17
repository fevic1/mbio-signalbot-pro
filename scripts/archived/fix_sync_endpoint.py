with open('main.py', 'r') as f:
    content = f.read()

# Find the _sync_exchange_positions function and replace the API call
old_api_call = 'resp = requests.post(\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "userState", "user": address},\n                timeout=15\n            )'

new_api_call = 'resp = requests.post(\n                "https://api.hyperliquid.xyz/info",\n                json={"type": "clearinghouseState", "user": address},\n                timeout=15\n            )'

if 'userState' in content and '_sync_exchange_positions' in content:
    content = content.replace('userState', 'clearinghouseState')
    print("✅ Updated sync to use clearinghouseState endpoint")
else:
    print("⚠️ Could not find userState to replace")

with open('main.py', 'w') as f:
    f.write(content)
