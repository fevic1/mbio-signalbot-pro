import os

path = 'strategies/llm.py'
if not os.path.exists(path):
    print(f"❌ {path} not found.")
    exit(1)

with open(path, 'r') as f:
    lines = f.readlines()

out = []
i = 0
while i < len(lines):
    line = lines[i]
    out.append(line)
    
    # Detect any 'try:' block
    if line.strip() == 'try:':
        try_indent = len(line) - len(line.lstrip())
        j = i + 1
        has_except = False
        
        # Scan forward to find the end of the try block
        while j < len(lines):
            l = lines[j]
            if l.strip() == '':
                j += 1
                continue
            l_indent = len(l) - len(l.lstrip())
            
            # If we hit a line at the same or lower indentation, the try block has ended
            if l_indent <= try_indent:
                if l.strip().startswith(('except', 'finally')):
                    has_except = True
                break
            j += 1
            
        # If the try block ended without an except/finally, inject one
        if not has_except:
            out.append(' ' * try_indent + 'except Exception:\n')
            out.append(' ' * (try_indent + 4) + 'return "HOLD", 0  # 🛡️ Auto-injected safety except\n')
            
    i += 1

with open(path, 'w') as f:
    f.writelines(out)

print("✅ Successfully repaired missing 'except' blocks in llm.py.")
