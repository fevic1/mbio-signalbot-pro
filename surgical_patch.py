import sys

FILE = 'execution/hl_executor.py'
with open(FILE, 'r') as f:
    content = f.read()

modified = False

# --- FIX 1: INJECT INITIALIZATION INTO __init__ ---
# Target: self.info = _Info(base_url, skip_ws=True)
target_init = "self.info = _Info(base_url, skip_ws=True)"
if target_init in content and "self.hip4_manager = HIP4MetadataManager" not in content:
    injection = """self.info = _Info(base_url, skip_ws=True)
        
        # --- HIP-4 INSTITUTIONAL INTEGRATION ---
        from core.hip4_metadata import HIP4MetadataManager
        self.hip4_manager = HIP4MetadataManager.get_instance()
        self.hip4_manager.initialize(self.info)
        logger.info("✅ HIP-4 Metadata Manager initialized.")
        # ---------------------------------------"""
    content = content.replace(target_init, injection)
    print("✅ FIX 1: Injected HIP-4 initialization into __init__.")
    modified = True
else:
    print("ℹ️ FIX 1: Initialization already present or target not found.")

# --- FIX 2: REMOVE STATIC _prec DICTIONARY ---
# Target: _prec = {"BTC":5,"ETH":4,"SOL":2,"XRP":0,"DOGE":0,"HYPE":2,"BNB":3,"AVAX":2,"LINK":2}
target_prec = '_prec = {"BTC":5,"ETH":4,"SOL":2,"XRP":0,"DOGE":0,"HYPE":2,"BNB":3,"AVAX":2,"LINK":2}'
if target_prec in content:
    content = content.replace(target_prec, "# _prec removed: Using HIP-4 live metadata")
    print("✅ FIX 2: Removed static _prec dictionary.")
    modified = True

# --- FIX 3: REMOVE REDUNDANT STATIC ROUNDING ---
# Target: sz = _round_sz(coin, sz)  (This overwrites the HIP-4 formatting)
# We must be careful to only remove the one inside place_order, not the function definition.
# We look for the specific context: it happens after px = _round_px(coin, px)
target_round = """            px = _round_px(coin, px)
            sz = _round_sz(coin, sz)"""
replacement_round = """            px = _round_px(coin, px)
            # sz = _round_sz(coin, sz)  <-- REMOVED: HIP-4 format_size already applied"""

if target_round in content:
    content = content.replace(target_round, replacement_round)
    print("✅ FIX 3: Disabled static _round_sz override.")
    modified = True

# --- WRITE BACK ---
if modified:
    with open(FILE, 'w') as f:
        f.write(content)
    print("\n🎯 SURGICAL PATCH COMPLETE. File updated.")
else:
    print("\nℹ️ No changes needed.")
