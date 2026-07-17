import os

path = 'strategies/llm.py'
with open(path, 'r') as f:
    lines = f.readlines()

out = []
i = 0
fixed = False

while i < len(lines):
    line = lines[i]
    out.append(line)
    
    # Detect any 'try:' block
    if line.strip() == 'try:':
        indent = len(line) - len(line.lstrip())
        
        # Look ahead to see if the try block is empty
        j = i + 1
        is_empty = True
        while j < len(lines):
            next_line = lines[j]
            if next_line.strip() == '':
                j += 1
                continue
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent <= indent:
                # The block ended without any indented code inside
                is_empty = True
                break
            else:
                # There is valid code inside the try block
                is_empty = False
                break
        
        if is_empty:
            out.append(' ' * (indent + 4) + 'pass  # 🛡️ Auto-fixed empty try block\n')
            fixed = True
    i += 1

with open(path, 'w') as f:
    f.writelines(out)

if fixed:
    print("✅ Successfully injected 'pass' into empty try block.")
else:
    print("⚠️ No empty try blocks found. Printing lines 35-45 for manual inspection:")
    for idx in range(34, min(45, len(lines))):
        print(f"{idx+1:3d}: {lines[idx]}", end='')
