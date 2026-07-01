import logging
from .base import BaseStrategy

logger = logging.getLogger(__name__)

class LLMStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("LLM")

    async def calculate_signal(self, data: dict) -> tuple:
        # 🛡️ PHASE 4: LLM DEMOTED & DEDUPLICATED
        # The actual LLM analysis is handled by analyze_batch() in main.py for Telegram UI.
        # This strategy layer is strictly a dummy voter to prevent double API calls and rate limits.
        return "HOLD", 0
