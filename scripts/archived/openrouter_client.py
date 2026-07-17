"""
Groq AI Client
"""
import logging
from groq import AsyncGroq
from typing import Dict
from .provider import AIProvider

logger = logging.getLogger(__name__)

class GroqClient(AIProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", timeout: int = 30):
        super().__init__("groq", api_key, model, timeout)
        self.client = AsyncGroq(api_key=api_key)
    
    async def analyze(self, asset: str, data: Dict) -> Dict:
        prompt = self._build_prompt(asset, data)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        
        content = response.choices[0].message.content.strip()
        return self._parse_response(content)
    
    def _parse_response(self, content: str) -> Dict:
        try:
            parts = content.split('|')
            if len(parts) >= 3:
                signal = parts[0].strip()
                confidence = int(parts[1].strip())
                reasoning = parts[2].strip()
                return {'signal': signal, 'confidence': confidence, 'reasoning': reasoning}
        except Exception as e:
            logger.error(f"Groq parse failed: {e}")
        return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'Parse failed'}
