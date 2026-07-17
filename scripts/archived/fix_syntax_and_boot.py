import re

path = 'main.py'
with open(path, 'r') as f:
    lines = f.readlines()

# 1. Eradicate all broken diagnostic traces
clean_lines = []
for line in lines:
    if '# 🔍 DIAGNOSTIC TRACE' in line: continue
    if '_min_conf = locals()' in line: continue
    if '🔍 DIAGNOSTIC:' in line and 'logger.info' in line: continue
    clean_lines.append(line)

# 2. Mathematically repair any orphaned/empty try blocks
fixed_lines = []
for i, line in enumerate(clean_lines):
    fixed_lines.append(line)
    if line.strip() == 'try:':
        indent = len(line) - len(line.lstrip())
        j = i + 1
        # Skip empty lines to find the actual next line of code
        while j < len(clean_lines) and clean_lines[j].strip() == '':
            j += 1
            
        if j < len(clean_lines):
            next_indent = len(clean_lines[j]) - len(clean_lines[j].lstrip())
            # If the next line is dedented, the try block is empty or broken
            if next_indent <= indent:
                fixed_lines.append(' ' * (indent + 4) + 'pass  # 🛡️ Auto-fixed empty try block\n')

with open(path, 'w') as f:
    f.writelines(fixed_lines)

print("✅ Eradicated broken diagnostics and repaired try/except syntax.")
