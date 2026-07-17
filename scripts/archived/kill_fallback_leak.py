import re

path = 'core/strategy_manager.py'
with open(path, 'r') as f:
    content = f.read()

# Find the exact logger warning for the fallback and inject an immediate return
pattern = r'(logger\.[a-z]+\([^)]*using best strategy[^)]*\))'
replacement = r'\1\n            return "HOLD", 0, "ENSEMBLE"  # 🛡️ KILLED FALLBACK: Force HOLD on weak consensus'

new_content, count = re.subn(pattern, replacement, content)

if count > 0:
    with open(path, 'w') as f:
        f.write(new_content)
    print(f"✅ Successfully neutered {count} weak fallback leak(s).")
else:
    print("⚠️ Could not find the exact fallback string. Manual review required.")
