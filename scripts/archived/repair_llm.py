import re

path = 'strategies/llm.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Strip out the broken cache_save injection completely
broken_blocks = [
    """
        # 🛡️ Save to LLM Cache
        if hasattr(self, '_llm_cache'):
            self._llm_cache[_cache_key] = {'ts': time.time(), 'data': (signal, confidence, reasoning) if 'reasoning' in locals() else (signal, confidence, "")}
""",
    """
        # 🛡️ Save to LLM Cache
        if hasattr(self, '_llm_cache'):
            self._llm_cache[_cache_key] = {'ts': time.time(), 'data': (signal, confidence, reasoning) if 'reasoning' in locals() else (signal, confidence, "")}"""
]
for block in broken_blocks:
    content = content.replace(block, "\n")

lines = content.split('\n')
fixed_lines = []

# 2. Auto-fix any empty blocks (IndentationError)
for i in range(len(lines)):
    line = lines[i]
    fixed_lines.append(line)
    
    # Check if line is a block starter ending with a colon
    if re.search(r'^(\s*)(if|elif|else|try|except|finally|for|while|def|class|with)\b.*:\s*$', line):
        indent1 = len(line) - len(line.lstrip())
        
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
            
        if j < len(lines):
            next_line = lines[j]
            indent2 = len(next_line) - len(next_line.lstrip())
            
            # If the next line is dedented, the block is empty!
            if indent2 <= indent1:
                fixed_lines.append(' ' * (indent1 + 4) + 'pass  # 🛡️ Auto-fixed empty block')

with open(path, 'w') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Stripped broken cache injection and auto-fixed IndentationErrors.")
