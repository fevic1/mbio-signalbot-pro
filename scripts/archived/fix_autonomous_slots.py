import re

path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Upgrade Portfolio Limit from 2 to 3 Slots
content = content.replace('len(_state.OPEN_POSITIONS) >= 2', 'len(_state.OPEN_POSITIONS) >= 3')
content = content.replace('len(state.OPEN_POSITIONS) < 2', 'len(state.OPEN_POSITIONS) < 3')
print("✅ Upgraded Portfolio Limit to 3 Slots.")

# 2. Inject Dynamic Sleep Cycle (Autonomous Slot Hunting)
old_sleep = 'logger.info("💤 Sleeping 0.5h...")'
new_sleep = '''import core.state as _state
            _free_slots = 3 - len(_state.OPEN_POSITIONS)
            if _free_slots > 0:
                _sleep_time = 300 # 5 minutes
                logger.info(f"🤖 DYNAMIC SLEEP: {_free_slots} free slot(s). Waking up in 5 minutes to hunt.")
            else:
                _sleep_time = 1800 # 30 minutes
                logger.info("💤 Portfolio full (3/3). Sleeping 0.5h...")'''

if 'DYNAMIC SLEEP' not in content:
    content = content.replace(old_sleep, new_sleep)
    
    # Replace the static asyncio.sleep(1800) with our dynamic variable
    content = re.sub(
        r'(Portfolio full.*?Sleeping 0\.5h\.\.\."\n\s*)await asyncio\.sleep\([^)]+\)',
        r'\1await asyncio.sleep(_sleep_time)',
        content,
        flags=re.DOTALL
    )
    # Fallback for standard sleep calls
    content = content.replace('await asyncio.sleep(1800)', 'await asyncio.sleep(_sleep_time)')
    content = content.replace('await asyncio.sleep(30 * 60)', 'await asyncio.sleep(_sleep_time)')
    print("✅ Injected Dynamic Sleep Cycle (Autonomous Slot Hunting).")

with open(path, 'w') as f:
    f.write(content)
