"""
Cerebras AI Client with Retry Logic
"""
import logging
import asyncio
from cerebras.cloud.sdk import AsyncCerebras
from .provider import AIProvider

logger = logging.getLogger(__name__)

class CerebrasClient(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-oss-120b", timeout: int = 30):
        super().__init__("cerebras", api_key, model, timeout)
        self.client = AsyncCerebras(api_key=api_key)
        self.max_retries = 2
    
    async def analyze(self, asset: str, data: dict) -> dict:
        prompt = self._build_prompt(asset, data)
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=100
                )
                
                content = response.choices[0].message.content if response.choices else None
                if not content:
                    logger.warning(f"Cerebras returned empty response for {asset}")
                    return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'Empty response'}
                
                self.retry_count = 0  # Reset on success
                return self._parse_response(content.strip())
                
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg and attempt < self.max_retries:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"⏳ Cerebras rate limited, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Cerebras analysis failed: {e}")
                    return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'API Error'}
        
        return {'signal': 'HOLD', 'confidence': 0, 'reasoning': 'Max retries exceeded'}

    def _parse_response(self, content: str) -> dict:
        import re
        if '|' in content:
            parts = content.split('|')
            if len(parts) >= 3:
                try:
                    return {'signal': parts[0].strip().upper(), 'confidence': int(parts[1].strip()), 'reasoning': parts[2].strip()}
                except:
                    pass
        
        signal_match = re.search(r'(STRONG BUY|BUY|HOLD|SELL|STRONG SELL)', content, re.IGNORECASE)
        conf_match = re.search(r'(\d{1,3})%', content) or re.search(r'confidence[:\s]*(\d{1,3})', content, re.IGNORECASE)
        
        return {
            'signal': signal_match.group(1).upper() if signal_match else 'HOLD',
            'confidence': int(conf_match.group(1)) if conf_match else 50,
            'reasoning': content[:100]
        }
