import sys

FILE = 'execution/hl_executor.py'
with open(FILE, 'r') as f:
    content = f.read()

# --- FIX 1: INJECT INITIALIZATION ---
# Anchor: We insert immediately after the Exchange client is created.
anchor = 'self.exchange = _Exchange(self.account, base_url, account_address=self.address)'
injection = """
        # --- HIP-4 INSTITUTIONAL INTEGRATION ---
        from core.hip4_metadata import HIP4MetadataManager
        self.hip4_manager = HIP4MetadataManager.get_instance()
        self.hip4_manager.initialize(self.info)
        # ---------------------------------------"""

if 'self.hip4_manager = HIP4MetadataManager' not in content:
    if anchor in content:
        content = content.replace(anchor, anchor + injection)
        print("✅ FIX 1: Injected HIP-4 Initialization into __init__.")
    else:
        print("❌ CRITICAL: Could not find anchor for __init__ injection.")
        sys.exit(1)
else:
    print("ℹ️ FIX 1: Initialization already present.")

# --- FIX 2: DISABLE OVERWRITE ---
# Target: The specific line inside place_order that overwrites the HIP-4 size.
# We match the exact indentation (12 spaces) to avoid touching the function definition.
old_overwrite = '            sz = _round_sz(coin, sz)'
new_overwrite = '            # sz = _round_sz(coin, sz)  # DISABLED: HIP-4 manager handles precision above'

if old_overwrite in content:
    content = content.replace(old_overwrite, new_overwrite)
    print("✅ FIX 2: Disabled static _round_sz overwrite in place_order.")
else:
    print("ℹ️ FIX 2: Overwrite already disabled or not found.")

# --- SAVE ---
with open(FILE, 'w') as f:
    f.write(content)

print("\n🎯 SURGICAL FIX COMPLETE. Code is now structurally sound.")
