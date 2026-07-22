"""
Vibe-Trading AI Client Connector - Live Smoke Test
Simulates an external AI agent interacting with the MBIO MCP Gateway.
"""
import os
import sys
import requests
import json
from typing import Dict, Any

MBIO_BASE_URL = os.getenv("MBIO_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("MCP_API_KEY", "dev_key_change_in_env")

def mcp_call(tool_name: str, arguments: Dict[str, Any], server_id: str = "vibe-trading") -> Dict[str, Any]:
    url = f"{MBIO_BASE_URL}/mcp/{server_id}/invoke"
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def parse_result(res, tool_name):
    if "error" in res:
        print(f"❌ {tool_name} failed: {res['error']}")
        return None
    if "result" in res and not res["result"].get("isError"):
        try:
            return json.loads(res["result"]["content"][0]["text"])
        except Exception:
            return res["result"]["content"][0]["text"]
    else:
        print(f"❌ {tool_name} failed: {res}")
        return None

if __name__ == "__main__":
    print("🤖 Vibe-Trading AI Client Connector - Live Smoke Test")
    print(f"   Target: {MBIO_BASE_URL}")
    print("-" * 60)

    asset = input("1️⃣ Enter asset symbol (e.g., BTC, ETH, SOL): ").strip().upper()
    if not asset:
        print("❌ Asset required.")
        sys.exit(1)

    print(f"\n🔍 Step 1: Fetching market regime for {asset}...")
    regime_res = mcp_call("get_market_regime", {"asset": asset}, server_id="vibe-trading")
    regime_data = parse_result(regime_res, "get_market_regime")
    
    if regime_data and regime_data.get("success"):
        data = regime_data.get("data", {})
        print(f"   ✅ Regime: {data.get('regime', 'UNKNOWN')}")
        print(f"   ✅ Confidence: {data.get('confidence', 0):.2%}")
    else:
        print("   ⚠️ Could not fetch regime, proceeding anyway...")

    print(f"\n🛡️ Step 2: Running pre-trade risk checks...")
    test_investment = 10.0 
    # ROUTE TO RISK-ANALYZER SERVER
    risk_res = mcp_call("validate_portfolio_exposure", {"asset": asset, "proposed_investment": test_investment}, server_id="risk-analyzer")
    risk_data = parse_result(risk_res, "validate_portfolio_exposure")
    
    if risk_data and risk_data.get("approved"):
        print(f"   ✅ Risk check passed: {risk_data.get('message', 'OK')}")
    else:
        print(f"   ❌ Risk check failed: {risk_data.get('reason') if risk_data else 'Unknown'}")
        sys.exit(1)

    print(f"\n🚀 Step 3: Preparing live grid deployment...")
    print("   ⚠️  THIS WILL PLACE A REAL ORDER ON HYPERLIQUID.")
    lower = float(input(f"   Enter lower price for {asset}: "))
    upper = float(input(f"   Enter upper price for {asset}: "))
    nodes = int(input("   Enter number of grid nodes (e.g., 5): "))
    otp = input("   Enter 6-digit OTP from Telegram (for fixed@mbio.com): ").strip()

    print(f"\n⏳ Executing place_grid for {asset}...")
    # ROUTE TO VIBE-TRADING SERVER
    exec_res = mcp_call("place_grid", {
        "asset": asset,
        "lower_price": lower,
        "upper_price": upper,
        "investment": test_investment,
        "nodes": nodes,
        "otp": otp
    }, server_id="vibe-trading")
    
    exec_data = parse_result(exec_res, "place_grid")
    if exec_data and exec_data.get("success"):
        print(f"\n🎉 SUCCESS! Grid deployed.")
        print(f"   Response: {exec_data.get('data')}")
    else:
        print(f"\n❌ Deployment failed: {exec_data}")
