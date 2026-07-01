"""
LLM-Based Trade Reasoning Engine.
Provides human-readable explanations and risk assessments for trade signals.
Stateless and multi-user safe.
"""
import json
import logging
import re
from typing import Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Default fallback if LLM fails or returns garbage
FALLBACK_REASONING = {
    "reasoning": "LLM analysis unavailable. Relying on raw strategy signal.",
    "risk_factors": "Unknown due to LLM error.",
    "timeframe_alignment": "Unknown"
}

class LLMReasoningEngine:
    """
    Analyzes trade setups using an LLM.
    Stateless: No shared state between calls, making it 100% multi-user safe.
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.2):
        self.client = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=250
        )

    async def analyze_trade(
        self, 
        asset: str, 
        signal: str, 
        confidence: int, 
        market_data: Dict
    ) -> Dict:
        """
        Get LLM reasoning for a specific trade setup.
        
        Args:
            asset: e.g., 'BTC'
            signal: 'BUY' or 'SELL'
            confidence: 0-100
            market_data: Dict containing RSI, ADX, volume, etc.
            
        Returns:
            Dict with 'reasoning', 'risk_factors', and 'timeframe_alignment'
        """
        if signal == "HOLD" or confidence < 50:
            return FALLBACK_REASONING

        prompt = self._build_prompt(asset, signal, confidence, market_data)
        
        try:
            response = await self.client.ainvoke([HumanMessage(content=prompt)])
            raw_content = response.content.strip()
            
            # Parse the JSON response
            parsed_data = self._parse_json_response(raw_content)
            
            if parsed_data:
                return parsed_data
            else:
                logger.warning(f"LLM returned unparseable JSON for {asset}: {raw_content[:50]}")
                return FALLBACK_REASONING
                
        except Exception as e:
            logger.error(f"LLM Reasoning failed for {asset}: {e}")
            return FALLBACK_REASONING

    def _build_prompt(self, asset: str, signal: str, confidence: int, data: Dict) -> str:
        """Construct the prompt for the LLM."""
        rsi = data.get('rsi', 'N/A')
        adx = data.get('adx', 'N/A')
        volume_ratio = data.get('volume_ratio', 'N/A')
        
        return f"""You are a senior crypto trading analyst at an institutional desk. Provide professional, concise analysis using institutional terminology. 
Analyze this {asset} trade setup and return ONLY valid JSON. Do not include markdown formatting like ```json.

Setup:
- Signal: {signal}
- Strategy Confidence: {confidence}%
- 1H RSI: {rsi}
- ADX (Trend Strength): {adx}
- Volume Ratio: {volume_ratio}

Return a JSON object with exactly these three keys:
1. "reasoning": A 1-sentence explanation of why this is a good trade.
2. "risk_factors": A 1-sentence warning about what could go wrong.
3. "timeframe_alignment": 'Bullish', 'Bearish', or 'Mixed' based on the data.

Example Output:
{{"reasoning": "RSI divergence supports the breakout.", "risk_factors": "Low volume might cause a fakeout.", "timeframe_alignment": "Bullish"}}
"""

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """
        Safely extract and parse JSON from LLM text.
        Handles cases where LLM adds conversational filler.
        """
        # 1. Try direct parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Try to extract JSON block using regex (handles ```json ... ```)
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None
