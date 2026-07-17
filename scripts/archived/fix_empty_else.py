import re

path = 'core/strategy_manager.py'
with open(path, 'r') as f:
    lines = f.readlines()

fixed_lines = []
patched = 0

for i, line in enumerate(lines):
    fixed_lines.append(line)
    
    # Check if line is a block starter ending with a colon (if, else, try, etc.)
    if re.search(r'^(\s*)(if|elif|else|try|except|finally|for|while|def|class|with)\b.*:\s*$', line):
        indent1 = len(line) - len(line.lstrip())
        
        j = i + 1
        # Skip empty lines to find the next actual line of code
        while j < len(lines) and lines[j].strip() == '':
            j += 1
            
        if j < len(lines):
            next_line = lines[j]
            indent2 = len(next_line) - len(next_line.lstrip())
            
            # If the next line is dedented or at the same level, the block is empty!
            if indent2 <= indent1:
                fixed_lines.append(' ' * (indent1 + 4) + 'pass  # 🛡️ Auto-fixed empty block\n')
                patched += 1

with open(path, 'w') as f:
    f.writelines(fixed_lines)

print(f"✅ Auto-fixed {patched} empty block(s) in strategy_manager.py.")
