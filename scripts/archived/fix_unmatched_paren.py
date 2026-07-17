path = 'main.py'
with open(path, 'r') as f:
    lines = f.readlines()

# Print lines 30-50 for diagnosis
print("=== Lines 30-50 of main.py ===")
for i in range(29, min(50, len(lines))):
    print(f"{i+1:3d}: {lines[i]}", end='')
print("=" * 40)

# Fix: Find the unmatched ) and remove it
fixed = False
for i in range(len(lines)):
    stripped = lines[i].strip()
    # If this line is just a closing paren with nothing before it
    # and the previous non-empty line doesn't have an unmatched open paren
    if stripped == ')':
        # Check if there's a matching ( in recent lines
        context = ''.join(lines[max(0,i-10):i])
        open_count = context.count('(')
        close_count = context.count(')')
        if close_count >= open_count:
            print(f"⚠️ Removing unmatched ')' at line {i+1}")
            lines[i] = ''  # Remove the line
            fixed = True

if fixed:
    with open(path, 'w') as f:
        f.writelines(lines)
    print("✅ Removed unmatched parenthesis.")
else:
    print("ℹ️ No standalone unmatched ')' found. Manual review needed.")
