"""
core/signal_generator.py — Elite AI Signal Generation
Exposes init_ai_clients() and analyze_batch() for the functional main.py.
"""
from core.regime import detect_regime
import asyncio
import json
import logging
import os
import re
from typing import Dict, Tuple

from aios.providers.router import chat
from aios.providers.types import ProviderRequest

logger = logging.getLogger(__name__)

init_ai_clients()

def init_ai_clients() -> int:
    from aios.providers.registry import registry

    active = sum(
        provider.available()
        for provider in registry.all().values()
    )

    logger.info(f"🧠 AI Providers: {active} active")
    return active

def _get_system_prompt(cfg: dict) -> str:
    s = cfg.get("signals", {})
    return f"""You are a senior quantitative trading analyst at a top-tier hedge fund. Analyze the crypto market data and output strict JSON. Your reasoning must be professional, concise, and use institutional trading terminology (e.g., "momentum shift", "liquidity sweep", "mean reversion", "support test").

TRADING LOGIC:
1. STRONG BUY: 1D RSI < {s.get('strong_buy_1d_rsi_max', 40)} AND 1H RSI < {s.get('strong_buy_1h_rsi_max', 55)}
2. BUY: 1D RSI < {s.get('buy_1d_rsi_max', 45)} AND Price near lower Bollinger Band.
3. STRONG SELL: 1D RSI > {s.get('strong_sell_1d_rsi_min', 68)} AND 1H RSI > {s.get('strong_sell_1h_rsi_min', 58)}
4. SELL: 1D RSI > {s.get('sell_1d_rsi_min', 62)} AND Price near upper Bollinger Band.
5. HOLD: If RSI is near 50 (neutral) or timeframes conflict.

OUTPUT FORMAT:
{{"results": [{{"asset": "NAME", "signal": "STRONG BUY|BUY|STRONG SELL|SELL|HOLD", "confidence": 0-100, "reasoning": "Professional 1-sentence institutional analysis"}}]}}"""

def _build_user_prompt(asset_batch: dict, regimes: dict = None) -> str:
    if regimes is None:
        regimes = {}
    lines = []
    for asset_name, data in asset_batch.items():
        d1h, d4h, d1d = data.get("1h", {}), data.get("4h", {}), data.get("1d", {})
        regime = regimes.get(asset_name, "UNKNOWN")
        lines.append(
            f"ASSET: {asset_name} (Current Market Regime: {regime})\n"
            f"1H: Price={d1h.get('price', 0)}, RSI={d1h.get('rsi', 50)}, MACD={d1h.get('macd', 0)}, BB=[{d1h.get('bb_lower', 0)}, {d1h.get('bb_upper', 0)}]\n"
            f"4H: RSI={d4h.get('rsi', 50)}, MACD={d4h.get('macd', 0)}\n"
            f"1D: RSI={d1d.get('rsi', 50)}, MACD={d1d.get('macd', 0)}\n"
        )
    return "Analyze the following market data:\n\n" + "\n".join(lines)

def _parse_json_response(text: str) -> Dict:
    if not text: return {}
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try: return json.loads(text[start:end+1])
        except: pass
    return {}

async def _call_provider(name: str, client, sys_prompt: str, user_prompt: str, json_mode: bool, model: str) -> Dict:
    try:
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt + ("\n\nREMINDER: Output ONLY raw JSON." if not json_mode else "")}
        ]
        
        # FIX: Pass model parameter explicitly
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500
        }
        if json_mode: 
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        parsed = json.loads(content) if json_mode else _parse_json_response(content)
        # logger.info(f"DEBUG: AI raw response: {content[:200]}")
        # logger.info(f"DEBUG: Parsed result: {parsed}")
        return parsed
    except Exception as e:
        logger.warning(f"Provider {name} failed: {e}")
        return {}

async def analyze_batch(asset_batch: dict, cfg: dict) -> Tuple[Dict, str]:
    """Returns (results_dict, provider_name)"""
    if not asset_batch: return {}, "none"
    
    # 🌊 --- ADD THIS BLOCK: DETECT & LOG REGIME ---
    regimes = {}
    for asset, data in asset_batch.items():
        try:
            # detect_regime requires the 4H OHLCV data
            regime = detect_regime(data.get("4h", {}))
            regimes[asset] = regime
            logger.info(f"🌊 {asset} Market Regime: {regime}")
        except Exception as e:
            logger.warning(f"⚠️ Regime detection failed for {asset}: {e}")
            regimes[asset] = "RANGING"
    # -----------------------------------------------

    sys_prompt = _get_system_prompt(cfg)
    user_prompt = _build_user_prompt(asset_batch, regimes) 
    
    # ... (leave the rest of your function exactly as it is) ...
    
    request = ProviderRequest(
    messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0.2,
    max_tokens=500,
)

try:
    response = await asyncio.to_thread(chat, request)
    best = _parse_json_response(response.content)
except Exception as e:
    logger.error(f"AI provider failed: {e}")
    return {}, "failed"

if "results" not in best:
    logger.error("❌ Invalid AI response")
    return {}, "failed"
    
    # Pick best result (highest total confidence)
    best = max(valid, key=lambda r: sum(item.get('confidence', 0) for item in r.get('results', [])))
    
    # Flatten to {asset_name: result_dict}
    flat_results = {}
    for item in best.get("results", []):
        asset = item.get("asset")
        if asset:
            flat_results[asset] = {
                "signal": item.get("signal", "HOLD").upper(),
                "confidence": max(50, int(item.get("confidence", 50))) if item.get("confidence") not in [None, "", 0] else 50,
                "reasoning": item.get("reasoning", "")
            }
            
    # Error tracking
    if not flat_results:
        logger.error("❌ CRITICAL: analyze_batch returned empty results")
        logger.error(f"   Valid responses: {len(valid)}")
        logger.error(f"   Total responses: {len(results)}")
    
return flat_results, response.provider
# ERROR_TRACKING: Add this to track failures
