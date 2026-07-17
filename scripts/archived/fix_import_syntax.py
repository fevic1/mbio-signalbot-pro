path = 'main.py'
with open(path, 'r') as f:
    content = f.read()

# Fix the mangled import line
bad_import = 'from monitoring.alert_manager import cmd_signal_source, (cmd_ratchet,'
good_import = 'from monitoring.alert_manager import cmd_signal_source, cmd_ratchet,'

if bad_import in content:
    content = content.replace(bad_import, good_import)
    with open(path, 'w') as f:
        f.write(content)
    print("✅ Fixed mangled import syntax in main.py")
else:
    # Fallback: find any variation with parentheses
    import re
    pattern = r'from monitoring\.alert_manager import cmd_signal_source,\s*\(cmd_ratchet,'
    match = re.search(pattern, content)
    if match:
        content = content[:match.start()] + 'from monitoring.alert_manager import cmd_signal_source, cmd_ratchet,' + content[match.end():]
        with open(path, 'w') as f:
            f.write(content)
        print("✅ Fixed mangled import via regex fallback")
    else:
        print("⚠️ Mangled import not found. Printing line 34 for inspection:")
        lines = content.split('\n')
        if len(lines) >= 34:
            print(f"Line 34: {lines[33]}")
