import logging
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .provider import AIProvider
from monitoring.langsmith_monitor import get_langsmith_monitor

logger = logging.getLogger(__name__)

class GroqClient(AIProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", timeout: int = 30):
        super().__init__("groq", api_key, model, timeout)
        self.client = ChatGroq(
            api_key=api_key,
            model=model,
            timeout=timeout,
            temperature=0.3,
            max_tokens=100
        )
    
    async def analyze(self, asset: str, data: dict) -> dict:
        import time; break  # 🛡️ Retries disabled  # 🛡️ Global Rate-Limit Shield
        prompt = self._build_prompt(asset, data)
        try:
            response = await self.client.ainvoke([HumanMessage(content=prompt)])
            content = response.content
            return self._parse_response(content.strip())
        except Exception as e:
            logger.error(f"Groq analysis failed: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'API Error'}
    def _parse_response(self, content: str) -> dict:
        import re
        import json
        
        # Try JSON parsing first (most reliable)
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                data = json.loads(json_match.group())
                signal = data.get('signal', 'HOLD').upper()
                confidence = int(data.get('confidence', 50))
                reasoning = data.get('reasoning', content[:100])
                if signal in ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL']:
                    return {'signal': signal, 'confidence': confidence, 'reasoning': reasoning}
        except:
            pass
        
        # Try pipe-separated format: SIGNAL|CONFIDENCE|REASONING
        if '|' in content:
            parts = content.split('|')
            if len(parts) >= 3:
                try:
                    signal = parts[0].strip().upper()
                    confidence = int(parts[1].strip())
                    reasoning = parts[2].strip()
                    if signal in ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL']:
                        return {'signal': signal, 'confidence': confidence, 'reasoning': reasoning}
                except:
                    pass
        
        # Fallback: Extract signal and confidence using regex
        signal_match = re.search(r'\b(STRONG BUY|BUY|HOLD|SELL|STRONG SELL)\b', content, re.IGNORECASE)
        conf_match = re.search(r'(\d{1,3})\s*%', content) or re.search(r'confidence[:\s]*(\d{1,3})', content, re.IGNORECASE)
        
        signal = signal_match.group(1).upper() if signal_match else 'HOLD'
        confidence = int(conf_match.group(1)) if conf_match else 50
        
        # Ensure signal is valid
        if signal not in ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL']:
            signal = 'HOLD'
        
        return {'signal': signal, 'confidence': confidence, 'reasoning': content[:100]}
