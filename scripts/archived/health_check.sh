#!/bin/bash

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
fail() { echo -e "  ${RED}❌ $1${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
info() { echo -e "  ${CYAN}ℹ️  $1${NC}"; }
hdr()  { echo -e "\n${BOLD}${BLUE}━━━ $1 ━━━${NC}"; }

cd /root/hyperliquid-agent-scout
source venv/bin/activate 2>/dev/null
export $(grep -v '^#' .env | grep '=' | xargs) 2>/dev/null

echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════╗"
echo -e "║   MBIO SignalBot — System Health Check   ║"
echo -e "╚══════════════════════════════════════════╝${NC}"
echo -e "  ${CYAN}$(date '+%Y-%m-%d %H:%M:%S UTC')${NC}\n"

hdr "1. Docker Containers"
BOT_STATUS=$(docker inspect mbio-signalbot --format='{{.State.Status}}' 2>/dev/null)
REDIS_STATUS=$(docker inspect mbio-redis --format='{{.State.Status}}' 2>/dev/null)
[ "$BOT_STATUS" = "running" ] && ok "mbio-signalbot: RUNNING" || fail "mbio-signalbot: ${BOT_STATUS:-NOT FOUND}"
[ "$REDIS_STATUS" = "running" ] && ok "mbio-redis: RUNNING" || fail "mbio-redis: ${REDIS_STATUS:-NOT FOUND}"
BOT_UPTIME=$(docker inspect mbio-signalbot --format='{{.State.StartedAt}}' 2>/dev/null | cut -c1-19)
[ -n "$BOT_UPTIME" ] && info "Bot started: $BOT_UPTIME"

hdr "2. Network Connectivity"
# Accept ANY response (even redirects/404s) as "reachable" — only real failures are timeouts/connection errors
check_url() {
    local name=$1 url=$2
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    if [ -n "$CODE" ] && [ "$CODE" != "000" ]; then
        ok "$name: REACHABLE (HTTP $CODE)"
    else
        fail "$name: UNREACHABLE (timeout/no response)"
    fi
}
check_url "Telegram API"    "https://api.telegram.org"
check_url "Hyperliquid API" "https://api.hyperliquid.xyz"
check_url "Groq API"        "https://api.groq.com"
check_url "Cerebras API"    "https://api.cerebras.ai"
check_url "OpenRouter API"  "https://openrouter.ai"
check_url "yFinance"        "https://finance.yahoo.com"

hdr "3. Environment Variables"
check_env() {
    local name=$1 val="${!1}"
    if [ -z "$val" ] || echo "$val" | grep -q "YOUR_\|your_\|PLACEHOLDER"; then
        fail "$name: NOT SET or placeholder"
    else
        ok "$name: SET (${val:0:8}...)"
    fi
}
check_env "TELEGRAM_BOT_TOKEN"; check_env "TELEGRAM_CHAT_ID"
check_env "GROQ_API_KEY"; check_env "CEREBRAS_API_KEY"; check_env "OPENROUTER_API_KEY"
check_env "HL_ACCOUNT_ADDRESS"; check_env "HL_PRIVATE_KEY"
[ "${HL_NETWORK:-MAINNET}" = "MAINNET" ] && ok "HL_NETWORK: MAINNET" || warn "HL_NETWORK: ${HL_NETWORK}"

hdr "4. AI Providers"
[ -n "$GROQ_API_KEY" ] && { R=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $GROQ_API_KEY" "https://api.groq.com/openai/v1/models"); [ "$R" = "200" ] && ok "Groq: ACTIVE" || warn "Groq: HTTP $R"; } || fail "Groq: NO KEY"
[ -n "$CEREBRAS_API_KEY" ] && { R=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CEREBRAS_API_KEY" "https://api.cerebras.ai/v1/models"); [ "$R" = "200" ] && ok "Cerebras: ACTIVE" || warn "Cerebras: HTTP $R"; } || fail "Cerebras: NO KEY"
[ -n "$OPENROUTER_API_KEY" ] && { R=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $OPENROUTER_API_KEY" "https://openrouter.ai/api/v1/models"); [ "$R" = "200" ] && ok "OpenRouter: ACTIVE" || warn "OpenRouter: HTTP $R"; } || fail "OpenRouter: NO KEY"

hdr "5. Hyperliquid Account"
if [ -n "$HL_ACCOUNT_ADDRESS" ]; then
    HL_DATA=$(curl -s --max-time 8 -X POST "https://api.hyperliquid.xyz/info" -H "Content-Type: application/json" -d "{\"type\":\"clearinghouseState\",\"user\":\"$HL_ACCOUNT_ADDRESS\"}" 2>/dev/null)
    BALANCE=$(echo "$HL_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'\${float(d[\"marginSummary\"][\"accountValue\"]):.2f}')" 2>/dev/null)
    POSITIONS=$(echo "$HL_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); p=[x for x in d.get('assetPositions',[]) if float(x['position'].get('szi',0))!=0]; print(len(p))" 2>/dev/null)
    MARGIN=$(echo "$HL_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'\${float(d[\"marginSummary\"][\"totalMarginUsed\"]):.2f}')" 2>/dev/null)
    [ -n "$BALANCE" ] && ok "Connected: Balance=$BALANCE | Margin=$MARGIN | Positions=$POSITIONS" || fail "Account query failed"
else fail "HL_ACCOUNT_ADDRESS not set"; fi

hdr "6. Core Python Modules"
for f in main.py config_loader.py core/signal_generator.py core/data_fetcher.py core/risk_manager.py core/state.py execution/hl_executor.py monitoring/position_tracker.py monitoring/alert_manager.py db.py; do
    [ -f "$f" ] && { python3 -m py_compile "$f" 2>/dev/null && ok "$f: OK" || fail "$f: SYNTAX ERROR"; } || fail "$f: NOT FOUND"
done

hdr "7. Strategy Config"
if [ -f "config/strategy_config.yaml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('config/strategy_config.yaml'))" 2>/dev/null && ok "strategy_config.yaml: VALID" || fail "strategy_config.yaml: INVALID"
    MAX_POS=$(python3 -c "import yaml; c=yaml.safe_load(open('config/strategy_config.yaml')); print(c.get('trading',{}).get('max_open_positions','?'))" 2>/dev/null)
    MIN_CONF=$(python3 -c "import yaml; c=yaml.safe_load(open('config/strategy_config.yaml')); print(c.get('trading',{}).get('entry_min_confidence','?'))" 2>/dev/null)
    info "Max positions: $MAX_POS | Min confidence: $MIN_CONF%"
else fail "strategy_config.yaml: NOT FOUND"; fi

hdr "8. Database"
DB_PATH="data/signals.db"
[ -f "$DB_PATH" ] && ok "Database: $DB_PATH ($(du -h "$DB_PATH" | cut -f1))" || warn "Database not found"

hdr "9. Redis State"
REDIS_PING=$(docker exec mbio-redis redis-cli ping 2>/dev/null)
[ "$REDIS_PING" = "PONG" ] && ok "Redis: RESPONDING ($(docker exec mbio-redis redis-cli DBSIZE 2>/dev/null) keys)" || fail "Redis: NOT RESPONDING"

hdr "10. Live Bot Activity (last 5min)"
LOGS=$(docker logs mbio-signalbot --since 5m 2>&1)
ERR_COUNT=$(echo "$LOGS" | grep -c "ERROR" || echo 0)
WARN_COUNT=$(echo "$LOGS" | grep -c "WARNING" || echo 0)
TRADE_COUNT=$(echo "$LOGS" | grep -c "Executing" || echo 0)
CHECK_COUNT=$(echo "$LOGS" | grep -c "Checking.*positions" || echo 0)
[ "$ERR_COUNT" -eq 0 ] 2>/dev/null && ok "Errors: $ERR_COUNT" || warn "Errors: $ERR_COUNT"
[ "$WARN_COUNT" -lt 10 ] 2>/dev/null && ok "Warnings: $WARN_COUNT (likely Groq rate limits — normal)" || warn "Warnings: $WARN_COUNT"
info "Trade executions: $TRADE_COUNT | Position checks: $CHECK_COUNT"
info "Last log: $(docker logs mbio-signalbot --tail 1 2>&1)"

hdr "11. System Resources"
DISK_PCT=$(df / | awk 'NR==2{gsub(/%/,""); print $5}')
[ "$DISK_PCT" -lt 85 ] && ok "Disk: ${DISK_PCT}% used" || warn "Disk: ${DISK_PCT}% used (getting full!)"
info "RAM: $(free -h | awk 'NR==2{print $3"/"$2}')"
info "Bot: $(docker stats mbio-signalbot --no-stream --format '{{.CPUPerc}} CPU, {{.MemUsage}}' 2>/dev/null)"

echo -e "\n${BOLD}${BLUE}━━━ SUMMARY ━━━${NC}"
if [ "$BOT_STATUS" = "running" ] && [ "$REDIS_STATUS" = "running" ] && [ -n "$BALANCE" ]; then
    echo -e "  ${GREEN}${BOLD}🟢 SYSTEM OPERATIONAL${NC}\n"
else
    echo -e "  ${RED}${BOLD}🔴 ISSUES DETECTED — check ❌ above${NC}\n"
fi
