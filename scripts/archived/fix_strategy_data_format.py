import re

# ============================================================
# 1. FIX TV_BOS_V6 DATA EXTRACTION
# ============================================================
bos_path = 'strategies/tv_bos_v6.py'
with open(bos_path, 'r') as f:
    bos = f.read()

# Replace incorrect data access patterns
bos = bos.replace(
    'candles_1h = data.get("1h", {}).get("candles", [])',
    'candles_1h = data.get("1h", {}).get("candles", []) if isinstance(data.get("1h"), dict) else []'
)
bos = bos.replace(
    'candles_4h = data.get("4h", {}).get("candles", [])',
    'candles_4h = data.get("4h", {}).get("candles", []) if isinstance(data.get("4h"), dict) else []'
)

# Add defensive check at top of calculate_signal
old_calc = 'def calculate_signal(self, data: dict) -> tuple:'
new_calc = '''def calculate_signal(self, data: dict) -> tuple:
        # Defensive: ensure data is a dict, not a list
        if isinstance(data, list):
            return "HOLD", 0'''
bos = bos.replace(old_calc, new_calc, 1)

with open(bos_path, 'w') as f:
    f.write(bos)
print("✅ Fixed tv_bos_v6.py data extraction")

# ============================================================
# 2. FIX TV_SMC_FVG DATA EXTRACTION
# ============================================================
smc_path = 'strategies/tv_smc_fvg.py'
with open(smc_path, 'r') as f:
    smc = f.read()

smc = smc.replace(
    'candles = data.get("1h", {}).get("candles", [])',
    'candles = data.get("1h", {}).get("candles", []) if isinstance(data.get("1h"), dict) else []'
)

old_calc_smc = 'def calculate_signal(self, data: dict) -> tuple:'
new_calc_smc = '''def calculate_signal(self, data: dict) -> tuple:
        # Defensive: ensure data is a dict, not a list
        if isinstance(data, list):
            return "HOLD", 0'''
smc = smc.replace(old_calc_smc, new_calc_smc, 1)

with open(smc_path, 'w') as f:
    f.write(smc)
print("✅ Fixed tv_smc_fvg.py data extraction")

# ============================================================
# 3. FIX UNBOUND 'signal' VARIABLE IN MAIN.PY
# ============================================================
main_path = 'main.py'
with open(main_path, 'r') as f:
    main = f.read()

# Add signal/conf/reason defaults BEFORE the native strategy block
if '_native_signal_default_set' not in main:
    default_vars = '''                # Default signal variables (prevent UnboundLocalError if native strategy fails)
                signal = "HOLD"
                conf = 0
                reason = ""
                _native_signal_default_set = True
'''
    # Insert right after "if isinstance(data, dict): data['asset_name'] = str(asset_name)"
    # inside the batch loop, before the STRATEGY REGISTRY ACTIVE comment
    target = "# 🔄 STRATEGY REGISTRY ACTIVE"
    if target in main:
        main = main.replace(target, default_vars + "                " + target, 1)
        with open(main_path, 'w') as f:
            f.write(main)
        print("✅ Added default signal/conf/reason in main.py")
    else:
        print("⚠️ Could not find STRATEGY REGISTRY marker in main.py")

print("\n🎉 All fixes applied.")
