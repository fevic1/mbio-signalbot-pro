from __future__ import annotations

import logging
from typing import List

from .models import (
    VerifiedEvidence, 
    IntelligenceEvidence, 
    EvidenceCategory, 
    Impact
)

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """
    Layer 3: Intelligence Analysis.
    
    Converts verified facts into structured intelligence.
    
    Responsibilities:
    - Filter low-confidence or duplicate evidence.
    - Interpret data payloads based on category.
    - Generate human-readable insights.
    - Determine directional impact (Bullish, Bearish, Neutral).
    
    Constraints:
    - NEVER computes scores (Layer 4).
    - NEVER makes trading decisions (Layer 5).
    - Pure deterministic logic; no external LLM calls in this foundational layer.
    """

    # Confidence threshold for analysis
    MIN_CONFIDENCE = 0.50

    # Keyword mappings for News/Sentiment analysis
    _BULLISH_KEYWORDS = {
        "partnership", "adoption", "upgrade", "listing", "integration", 
        "growth", "surge", "breakout", "approval", "etf"
    }
    _BEARISH_KEYWORDS = {
        "hack", "exploit", "lawsuit", "ban", "crash", "plunge", 
        "investigation", "outage", "vulnerability", "drain"
    }

    def analyze(
        self, 
        verified_evidence: List[VerifiedEvidence]
    ) -> List[IntelligenceEvidence]:
        """
        Transforms VerifiedEvidence into IntelligenceEvidence.
        """
        intelligence_list: List[IntelligenceEvidence] = []

        for evidence in verified_evidence:
            # 1. Filter out duplicates and low-confidence sources
            if evidence.is_duplicate:
                continue
            if evidence.source_confidence < self.MIN_CONFIDENCE:
                continue

            # 2. Dispatch to category-specific analyzer
            insight, impact = self._interpret(evidence)

            # 3. Build IntelligenceEvidence
            intelligence = IntelligenceEvidence(
                asset=evidence.asset,
                category=evidence.category,
                insight=insight,
                impact=impact,
                supporting_data={
                    "source": evidence.source,
                    "freshness": evidence.freshness_score,
                    "raw_data_summary": str(evidence.data)[:200] # Truncate for safety
                }
            )
            intelligence_list.append(intelligence)

        return intelligence_list

    def _interpret(
        self, 
        evidence: VerifiedEvidence
    ) -> tuple[str, Impact]:
        """
        Routes evidence to the correct interpretation logic.
        """
        if evidence.category == EvidenceCategory.MARKET_DATA:
            return self._analyze_market_data(evidence.data)
        elif evidence.category == EvidenceCategory.NEWS:
            return self._analyze_news(evidence.data)
        elif evidence.category == EvidenceCategory.ON_CHAIN:
            return self._analyze_on_chain(evidence.data)
        
        # Fallback for other categories
        return self._analyze_generic(evidence.data)

    def _analyze_market_data(self, data: dict) -> tuple[str, Impact]:
        """Interprets price, volume, and technical metrics."""
        price_change = data.get("price_change_24h", data.get("price_change", 0.0))
        volume_spike = data.get("volume_change_24h", data.get("volume_spike", 0.0))

        if isinstance(price_change, (int, float)) and price_change > 5.0:
            return f"Significant price surge of {price_change:.2f}% detected.", Impact.BULLISH
        if isinstance(price_change, (int, float)) and price_change < -5.0:
            return f"Significant price drop of {price_change:.2f}% detected.", Impact.BEARISH
        if isinstance(volume_spike, (int, float)) and volume_spike > 50.0:
            return f"Unusual volume spike of {volume_spike:.2f}% indicates high market interest.", Impact.BULLISH
        
        return "Market data shows standard fluctuations within normal parameters.", Impact.NEUTRAL

    def _analyze_news(self, data: dict) -> tuple[str, Impact]:
        """Interprets news headlines and text for sentiment."""
        text = str(data.get("headline", data.get("title", data.get("content", "")))).lower()
        
        bullish_hits = len([w for w in self._BULLISH_KEYWORDS if w in text])
        bearish_hits = len([w for w in self._BEARISH_KEYWORDS if w in text])

        if bullish_hits > bearish_hits and bullish_hits > 0:
            return f"Positive market narrative detected: '{text[:50]}...'", Impact.BULLISH
        if bearish_hits > bullish_hits and bearish_hits > 0:
            return f"Negative market narrative detected: '{text[:50]}...'", Impact.BEARISH
            
        return f"News item processed with neutral sentiment: '{text[:50]}...'", Impact.NEUTRAL

    def _analyze_on_chain(self, data: dict) -> tuple[str, Impact]:
        """Interprets on-chain metrics like TVL or whale movements."""
        tvl_change = data.get("tvl_change_24h", 0.0)
        whale_activity = data.get("whale_transactions", 0)

        if isinstance(tvl_change, (int, float)) and tvl_change > 2.0:
            return f"Capital inflow detected: TVL increased by {tvl_change:.2f}%.", Impact.BULLISH
        if isinstance(whale_activity, (int, float)) and whale_activity > 10:
            return f"High whale activity detected: {int(whale_activity)} large transactions.", Impact.BULLISH # Usually accumulation
            
        return "On-chain metrics indicate stable network activity.", Impact.NEUTRAL

    def _analyze_generic(self, data: dict) -> tuple[str, Impact]:
        """Fallback for unstructured or unknown categories."""
        return f"New intelligence received from source. Data payload size: {len(str(data))} chars.", Impact.NEUTRAL
