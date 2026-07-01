import logging
from openai import AsyncOpenAI
from .provider import AIProvider

logger = logging.getLogger(__name__)

class OpenRouterClient(AIProvider):
    def __init__(self, api_key: str, model: str = "meta-llama/llama-3.3-70b-instruct", timeout: int = 60):
        super().__init__("openrouter", api_key, model, timeout)
        self.client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    
    async def analyze(self, asset: str, data: dict) -> dict:
        prompt = self._build_prompt(asset, data)
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=100
            )
            return self._parse_response(response.choices[0].message.content.strip())
        except Exception as e:
            logger.error(f"OpenRouter analysis failed: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'API Error'}

    def _parse_response(self, content: str) -> dict:
        import re
        if '|' in content:
            parts = content.split('|')
            if len(parts) >= 3:
                try: return {'signal': parts[0].strip().upper(), 'confidence': int(parts[1].strip()), 'reasoning': parts[2].strip()}
                except: pass
        signal_match = re.search(r'(STRONG BUY|BUY|HOLD|SELL|STRONG SELL)', content, re.IGNORECASE)
        conf_match = re.search(r'(\d{1,3})%', content) or re.search(r'confidence[:\s]*(\d{1,3})', content, re.IGNORECASE)
        return {'signal': signal_match.group(1).upper() if signal_match else 'HOLD', 
                'confidence': int(conf_match.group(1)) if conf_match else 50, 'reasoning': content[:100]}
