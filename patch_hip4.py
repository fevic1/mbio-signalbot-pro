import re
import sys

FILE_PATH = 'execution/hl_executor.py'

try:
    with open(FILE_PATH, 'r') as f:
        content = f.read()
except FileNotFoundError:
    print(f"❌ CRITICAL: {FILE_PATH} not found.")
    sys.exit(1)

# --- STEP 1: INJECT IMPORT ---
if 'from core.hip4_metadata import HIP4MetadataManager' not in content:
    # Insert after the last 'import' or 'from' statement at the top of the file
    import_pattern = re.compile(r'^(import .*|from .*)$', re.MULTILINE)
    matches = list(import_pattern.finditer(content))
    if matches:
        insert_pos = matches[-1].end()
        content = content[:insert_pos] + '\nfrom core.hip4_metadata import HIP4MetadataManager\n' + content[insert_pos:]
        print("✅ Injected HIP4MetadataManager import.")
    else:
        print("❌ Could not find import location.")

# --- STEP 2: INITIALIZE MANAGER IN __init__ ---
# Look for where the Info client is assigned (e.g., self.info = Info(...))
# We need to hook into that variable to pass it to the manager.
info_match = re.search(r'self\.(\w+)\s*=\s*Info\(', content)
if info_match:
    info_var = info_match.group(1)
    init_injection = f"""
        # --- HIP-4 INSTITUTIONAL INTEGRATION ---
        self.hip4_manager = HIP4MetadataManager.get_instance()
        self.hip4_manager.initialize(self.{info_var})
        # ---------------------------------------
"""
    # Find the end of the __init__ method signature to inject safely
    # We look for the first line of code inside __init__ that isn't a docstring
    init_start = content.find('def __init__')
    if init_start != -1:
        # Simple heuristic: inject after the first 'self.' assignment or at the end of the block
        # Let's inject immediately after the Info client assignment
        inject_pos = info_match.end()
        # Find the end of that line
        eol = content.find('\n', inject_pos)
        content = content[:eol+1] + init_injection + content[eol+1:]
        print(f"✅ Initialized HIP4Manager using client 'self.{info_var}' in __init__.")
else:
    print("⚠️ WARNING: Could not find 'self.xyz = Info(' assignment. Manual init required.")

# --- STEP 3: REPLACE STATIC ROUNDING WITH LIVE FORMATTING ---
# Target: sz = round(sz, _prec.get(coin, 4))  (or similar static rounding)
# Replace with: sz = self.hip4_manager.format_size(coin, sz)

# Regex to catch variations of static rounding
static_round_pattern = re.compile(r'sz\s*=\s*round\(sz,\s*_prec\.get\([^)]+\)\)')
if static_round_pattern.search(content):
    content = static_round_pattern.sub('sz = self.hip4_manager.format_size(coin, sz)', content)
    print("✅ Replaced static rounding with live HIP-4 format_size().")
else:
    # Fallback: try to find generic rounding if the exact pattern differs
    generic_round = re.compile(r'sz\s*=\s*round\(sz,\s*\d+\)')
    if generic_round.search(content):
         content = generic_round.sub('sz = self.hip4_manager.format_size(coin, sz)', content)
         print("✅ Replaced generic rounding with live HIP-4 format_size().")
    else:
         print("⚠️ WARNING: Could not auto-locate rounding logic. Manual patch may be needed.")

# --- STEP 4: WRITE BACK ---
with open(FILE_PATH, 'w') as f:
    f.write(content)

print("\n🎯 PATCH COMPLETE. hl_executor.py is now HIP-4 compliant.")
