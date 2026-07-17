#!/bin/bash
echo "🔍 MBIO SignalBot Pro Health Check"
echo "-----------------------------------"
# 1. Container Status
echo "1. Container Status:"
docker compose ps mbio-signalbot
# 2. Critical Env Vars (masked)
echo -e "\n2. Critical Env Vars:"
docker compose exec mbio-bot env | grep -E "HL_ACCOUNT_ADDRESS|ENABLE_AUTO_TRADING" | sed 's/=.*/=***MASKED***/'
# 3. Python Syntax Check
echo -e "\n3. Python Syntax Check:"
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -exec python3 -m py_compile {} \; && echo "✅ All Python files have valid syntax" || echo "❌ Syntax errors found"
# 4. Repo Hygiene
echo -e "\n4. Repo Hygiene:"
if git ls-files | grep -q "\.env"; then echo "❌ .env is tracked in git!"; else echo "✅ .env is not tracked in git"; fi
if ls fix_*.py deploy_*.py god_mode_*.py 2>/dev/null; then echo "❌ Fix/deploy scripts found in root!"; else echo "✅ No forbidden scripts in root"; fi
echo "-----------------------------------"
echo "✅ Health Check Complete"
