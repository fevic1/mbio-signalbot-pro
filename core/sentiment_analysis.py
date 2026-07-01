"""
Sentiment Analysis Engine.
Analyzes text (news/social) to determine market sentiment.
Stateless and multi-user safe.
"""
import logging
import json
from typing import List, Dict, Optional
from core.llm_reasoning import LLMReasoningEngine

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Analyzes text snippets for market sentiment.
    """
    
    def __init__(self, api_key: str):
        self.engine = LLMReasoningEngine(api_key=api_key)

    async def analyze(
        self, 
        asset: str, 
        headlines: List[str]
    ) -> Dict:
        """
        Analyze a list of headlines for sentiment.
        
        Args:
            asset: The crypto asset (e.g., 'BTC').
            headlines: A list of news headlines or social posts.
            
        Returns:
            Dict with 'score' (-1.0 to 1.0) and 'summary'.
        """
        if not headlines:
            return {"score": 0.0, "summary": "No data available"}

        prompt = f"""You are a crypto market sentiment analyst.
Analyze the sentiment of these headlines regarding {asset}.

Headlines:
{chr(10).join(headlines)}

Return ONLY a valid JSON object with these keys:
1. "score": A float between -1.0 (Extremely Bearish) and 1.0 (Extremely Bullish). 0.0 is neutral.
2. "summary": A one-sentence explanation of the overall sentiment.

Example Output:
{{"score": 0.8, "summary": "Strong bullish momentum following regulatory clarity."}}
"""

        try:
            # We reuse the LLM reasoning engine for the API call to save dependencies
            # Since the engine uses ainvoke, we mock the prompt passing via direct invocation if needed
            # But for now, let's use the engine's invoke method directly with the prompt
            from langchain_core.messages import HumanMessage
            response = await self.engine.client.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Parse JSON
            import re
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return {
                        "score": float(data.get("score", 0)),
                        "summary": data.get("summary", "Analysis complete.")
                    }
                except json.JSONDecodeError:
                    logger.error(f"Sentiment JSON parse error: {content[:50]}")
                    return {"score": 0.0, "summary": "Parse error"}
            else:
                return {"score": 0.0, "summary": "No JSON found in LLM response"}

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"score": 0.0, "summary": "Analysis failed"}
