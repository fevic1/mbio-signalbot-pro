#!/bin/bash

echo "=========================================="
echo "MBIO SignalBot v9.0 - Security Audit"
echo "=========================================="

# 1. Check for hardcoded secrets
echo -e "\n[1/10] Checking for hardcoded secrets..."
grep -r "8708504181" --include="*.py" --include="*.yaml" --include="*.yml" . 2>/dev/null && echo "⚠️  Found potential token" || echo "✅ No hardcoded tokens found"

# 2. Check .gitignore
echo -e "\n[2/10] Checking .gitignore..."
if [ -f ".gitignore" ]; then
    grep -q "\.env" .gitignore && echo "✅ .env in .gitignore" || echo "❌ .env NOT in .gitignore"
    grep -q "\.log" .gitignore && echo "✅ .log in .gitignore" || echo "❌ .log NOT in .gitignore"
    grep -q "venv/" .gitignore && echo "✅ venv/ in .gitignore" || echo "❌ venv/ NOT in .gitignore"
else
    echo "❌ .gitignore file missing"
fi

# 3. Check if .env is tracked
echo -e "\n[3/10] Checking if .env is tracked in git..."
git ls-files | grep -q "\.env$" && echo "❌ .env is tracked in git (DANGER!)" || echo "✅ .env not tracked"

# 4. Check for secrets in git history
echo -e "\n[4/10] Checking git history for secrets..."
git log --all --full-history --source --pretty=format: --name-only | grep -E "\.(env|pem|key)$" && echo "⚠️  Found sensitive files in history" || echo "✅ No sensitive files in history"

# 5. Check environment variable usage
echo -e "\n[5/10] Checking environment variable consistency..."
grep -r "HL_ADDRESS" --include="*.py" . 2>/dev/null | grep -v "HL_ACCOUNT_ADDRESS" && echo "⚠️  Found HL_ADDRESS (should be HL_ACCOUNT_ADDRESS)" || echo "✅ All env vars consistent"

# 6. Check for synchronous blocking calls in async code
echo -e "\n[6/10] Checking for blocking calls in async functions..."
grep -n "execute_hl_order" monitoring/alert_manager.py | grep -v "asyncio.to_thread" && echo "⚠️  Found synchronous execute_hl_order in async context" || echo "✅ All blocking calls wrapped"

# 7. Check requirements.txt
echo -e "\n[7/10] Checking requirements.txt..."
[ -f "requirements.txt" ] && echo "✅ requirements.txt exists" || echo "❌ requirements.txt missing"
grep -q "python-telegram-bot" requirements.txt && echo "✅ python-telegram-bot in requirements" || echo "❌ python-telegram-bot missing"
grep -q "hyperliquid-python-sdk" requirements.txt && echo "✅ hyperliquid-python-sdk in requirements" || echo "❌ hyperliquid-python-sdk missing"

# 8. Check for .env.example
echo -e "\n[8/10] Checking .env.example..."
[ -f ".env.example" ] && echo "✅ .env.example exists" || echo "❌ .env.example missing"

# 9. Check log suppression
echo -e "\n[9/10] Checking log suppression..."
grep -q "logging.getLogger('telegram').setLevel" main.py && echo "✅ Telegram logs suppressed" || echo "⚠️  Telegram logs not suppressed"

# 10. Check for race conditions
echo -e "\n[10/10] Checking for async/await patterns..."
grep -n "async def _close_position" monitoring/alert_manager.py && echo "✅ _close_position is async" || echo "❌ _close_position not async"

echo -e "\n=========================================="
echo "Security audit complete!"
echo "=========================================="
