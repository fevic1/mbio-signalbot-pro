with open('main.py', 'r') as f:
    content = f.read()

# Fix the exact syntax error caused by the previous regex script
content = content.replace('import (, cmd_ratchet', 'import (cmd_ratchet,')
content = content.replace('import (,cmd_ratchet', 'import (cmd_ratchet,')

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed main.py import syntax.")
