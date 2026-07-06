import re

FILE = 'execution/hl_executor.py'
with open(FILE, 'r') as f:
    lines = f.readlines()

# Check if already patched
if any('HIP4MetadataManager' in line for line in lines):
    print("✅ HIP-4 already patched. Skipping.")
else:
    # Find the __init__ method
    init_idx = -1
    for i, line in enumerate(lines):
        if 'def __init__' in line:
            init_idx = i
            break
            
    if init_idx == -1:
        print("❌ FATAL: Could not find __init__ method.")
        exit(1)
        
    # Find the end of __init__ (next method definition at same or lower indentation)
    end_idx = -1
    init_indent = len(lines[init_idx]) - len(lines[init_idx].lstrip())
    
    for i in range(init_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (init_indent + 1)) and not line.strip().startswith('#'):
            # Found next method or class end
            end_idx = i
            break
            
    if end_idx == -1:
        end_idx = len(lines) # End of file
        
    # Construct the injection code
    injection = [
        "\n",
        "        # --- HIP-4 INSTITUTIONAL INTEGRATION (FORCE INJECTED) ---\n",
        "        try:\n",
        "            from core.hip4_metadata import HIP4MetadataManager\n",
        "            self.hip4_manager = HIP4MetadataManager.get_instance()\n",
        "            # Pass the Info client (usually self.info or self.exchange.info)\n",
        "            info_client = getattr(self, 'info', None) or getattr(self, 'exchange', None)\n",
        "            if info_client and hasattr(info_client, 'info'):\n",
        "                info_client = info_client.info\n",
        "            if info_client:\n",
        "                self.hip4_manager.initialize(info_client)\n",
        "            else:\n",
        "                print('⚠️ HIP-4: Could not locate Info client for initialization.')\n",
        "        except Exception as e:\n",
        "            print(f'❌ HIP-4 Init Error: {e}')\n",
        "        # ----------------------------------------------------------\n"
    ]
    
    # Insert the code
    lines = lines[:end_idx] + injection + lines[end_idx:]
    
    # Also ensure import is at top if not using inline import
    # (We used inline import above for safety, so no top import needed)
    
    with open(FILE, 'w') as f:
        f.writelines(lines)
        
    print("✅ SUCCESS: HIP-4 Force-Injected into __init__.")
