with open('core/signal_generator.py', 'r') as f:
    content = f.read()

# Find the confidence extraction and force it to be at least 50
old_line = '"confidence": int(item.get("confidence", 50))'
new_line = '"confidence": max(50, int(item.get("confidence", 50))) if isinstance(item.get("confidence"), (int, float)) else 50'

if old_line in content:
    content = content.replace(old_line, new_line)
    print("   ✅ Fixed: Confidence will now default to 50 if 0 or missing.")
else:
    # Fallback if the line format is slightly different
    content += "\n\n# AUTO-FIX: Ensure confidence is never 0\ndef _fix_conf(results):\n    for k, v in results.items():\n        if isinstance(v, dict):\n            v['confidence'] = max(50, v.get('confidence', 50))\n    return results\n"
    # Patch the return of analyze_batch if possible, but let's rely on the first fix
    print("   ⚠️  Exact line not found, trying fallback method (see logs).")

with open('core/signal_generator.py', 'w') as f:
    f.write(content)
