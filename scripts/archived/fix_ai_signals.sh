#!/bin/bash

echo "========================================================================"
echo "PROFESSIONAL AI SIGNAL GENERATION FIX"
echo "========================================================================"
echo ""

# Step 1: Enable debug logging in signal_generator.py
echo "[STEP 1] Enabling debug logging in signal_generator.py..."
if ! grep -q "logger.info(f\"DEBUG: AI raw response" core/signal_generator.py; then
    # Uncomment the debug logging lines
    sed -i 's/#         logger.info(f"DEBUG: AI raw response/logger.info(f"DEBUG: AI raw response/' core/signal_generator.py
    sed -i 's/#         logger.info(f"DEBUG: Parsed result/logger.info(f"DEBUG: Parsed result/' core/signal_generator.py
    echo "✅ Debug logging enabled"
else
    echo "ℹ️  Debug logging already enabled"
fi

# Step 2: Add error tracking to analyze_batch
echo ""
echo "[STEP 2] Adding error tracking to analyze_batch..."
if ! grep -q "ERROR_TRACKING" core/signal_generator.py; then
    cat >> core/signal_generator.py << 'PYEOF'

# ERROR_TRACKING: Add this to track failures
PYEOF
    
    # Find the analyze_batch function and add error tracking
    python3 << 'INNER_EOF'
with open('core/signal_generator.py', 'r') as f:
    content = f.read()

# Add error tracking before the return statement
old_return = '    return flat_results, "groq" if _groq_client else ("cerebras" if _cerebras_client else "openrouter")'
new_return = '''    # Error tracking
    if not flat_results:
        logger.error("❌ CRITICAL: analyze_batch returned empty results")
        logger.error(f"   Valid responses: {len(valid)}")
        logger.error(f"   Total responses: {len(results)}")
    
    return flat_results, "groq" if _groq_client else ("cerebras" if _cerebras_client else "openrouter")'''

if old_return in content:
    content = content.replace(old_return, new_return)
    with open('core/signal_generator.py', 'w') as f:
        f.write(content)
    print("✅ Error tracking added")
else:
    print("⚠️  Could not add error tracking")
INNER_EOF
else
    echo "ℹ️  Error tracking already present"
fi

# Step 3: Check API keys
echo ""
echo "[STEP 3] Verifying API keys..."
if [ -f .env ]; then
    groq_key=$(grep GROQ_API_KEY .env | cut -d'=' -f2 | head -c 10)
    cerebras_key=$(grep CEREBRAS_API_KEY .env | cut -d'=' -f2 | head -c 10)
    openrouter_key=$(grep OPENROUTER_API_KEY .env | cut -d'=' -f2 | head -c 10)
    
    echo "GROQ_API_KEY: ${groq_key}..."
    echo "CEREBRAS_API_KEY: ${cerebras_key}..."
    echo "OPENROUTER_API_KEY: ${openrouter_key}..."
    
    if [ -z "$groq_key" ] && [ -z "$cerebras_key" ] && [ -z "$openrouter_key" ]; then
        echo "❌ CRITICAL: No API keys found in .env"
        exit 1
    fi
else
    echo "❌ CRITICAL: .env file not found"
    exit 1
fi

# Step 4: Restart and monitor
echo ""
echo "[STEP 4] Restarting bot and monitoring logs..."
docker compose restart mbio-bot

echo "Waiting 30 seconds for first analysis cycle..."
sleep 30

echo ""
echo "[STEP 5] Checking logs for debug output..."
docker compose logs --tail=200 mbio-bot | grep -E "DEBUG:|ERROR:|Batch:|HOLD|STRONG" | tail -30

echo ""
echo "========================================================================"
echo "DIAGNOSTIC COMPLETE"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Check the logs above for 'DEBUG: AI raw response' messages"
echo "2. If you see empty responses, the AI providers are failing"
echo "3. If you see valid responses but still HOLD, check the parsing logic"
echo ""
echo "To see full debug output:"
echo "docker compose logs -f mbio-bot | grep -E 'DEBUG:|ERROR:'"
