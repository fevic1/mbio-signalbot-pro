from __future__ import annotations

import logging
from typing import Dict, List

from .models import (
    IntelligenceEvidence, 
    IntelligenceScore, 
    Impact, 
    EvidenceCategory,
    Priority
)

logger = logging.getLogger(__name__)


class MarketScorer:
    """
    Layer 4: Scoring.
    
    Computes the multi-dimensional intelligence score based on analyzed evidence.
    
    Responsibilities:
    - Calculate the 10 scoring dimensions.
    - Compute overall_score (0.0 to 100.0).
    - Compute confidence (0.0 to 1.0).
    - Assign Priority based on score deviation from neutral.
    
    Constraints:
    - NEVER generates explanations or insights (Layer 3).
    - NEVER recommends trades or actions (Layer 5).
    - NEVER fetches data (Layer 1).
    - NEVER verifies evidence (Layer 2).
    - Pure mathematical computation; no side effects.
    """

    # Neutral baseline for all dimensions
    _NEUTRAL_BASELINE = 50.0
    
    # Impact delta applied to dimensions
    _IMPACT_DELTA = 10.0

    # Category to primary dimension mapping
    _CATEGORY_DIMENSION_MAP: Dict[EvidenceCategory, str] = {
        EvidenceCategory.MARKET_DATA: "technical",
        EvidenceCategory.NEWS: "sentiment",
        EvidenceCategory.ON_CHAIN: "on_chain",
        EvidenceCategory.INSTITUTIONAL: "institutional",
        EvidenceCategory.COMMUNITY: "community",
        EvidenceCategory.MACROECONOMIC: "fundamental",
    }

    def score(self, intelligence: List[IntelligenceEvidence]) -> IntelligenceScore:
        """
        Transforms a list of IntelligenceEvidence into a single IntelligenceScore.
        """
        if not intelligence:
            return IntelligenceScore(asset="UNKNOWN", priority=Priority.LOW)

        asset = intelligence[0].asset
        
        # Initialize dimensions to neutral baseline
        dimensions = {
            "fundamental": self._NEUTRAL_BASELINE,
            "technical": self._NEUTRAL_BASELINE,
            "on_chain": self._NEUTRAL_BASELINE,
            "liquidity": self._NEUTRAL_BASELINE,
            "institutional": self._NEUTRAL_BASELINE,
            "community": self._NEUTRAL_BASELINE,
            "developer": self._NEUTRAL_BASELINE,
            "sentiment": self._NEUTRAL_BASELINE,
            "narrative": self._NEUTRAL_BASELINE,
            "risk": self._NEUTRAL_BASELINE,
        }
        
        total_freshness = 0.0
        
        for ev in intelligence:
            # 1. Map category to primary dimension and apply impact delta
            primary_dim = self._CATEGORY_DIMENSION_MAP.get(ev.category)
            if primary_dim and primary_dim in dimensions:
                dimensions[primary_dim] = self._apply_delta(
                    dimensions[primary_dim], ev.impact
                )
                
            # 2. Secondary mappings (e.g., News also affects Narrative)
            if ev.category == EvidenceCategory.NEWS:
                dimensions["narrative"] = self._apply_delta(
                    dimensions["narrative"], ev.impact, multiplier=0.5
                )
                
            # 3. Accumulate freshness for confidence calculation
            freshness = ev.supporting_data.get("freshness", 0.5)
            total_freshness += freshness
            
        # 4. Calculate Risk based on overall volatility/deviation
        # Higher deviation from neutral = higher risk
        avg_dimension_score = sum(dimensions.values()) / len(dimensions)
        deviation = abs(avg_dimension_score - self._NEUTRAL_BASELINE)
        dimensions["risk"] = min(100.0, self._NEUTRAL_BASELINE + deviation)
            
        # 5. Compute overall_score
        overall_score = sum(dimensions.values()) / len(dimensions)
        
        # 6. Compute confidence (0.0 to 1.0)
        # Based on evidence volume and average freshness
        evidence_count = len(intelligence)
        avg_freshness = total_freshness / evidence_count if evidence_count > 0 else 0.0
        confidence = min(1.0, (evidence_count / 10.0) * avg_freshness)
        
        # 7. Determine Priority based on deviation from neutral (50.0)
        priority = self._assign_priority(deviation)
                
        return IntelligenceScore(
            asset=asset,
            fundamental=round(dimensions["fundamental"], 2),
            technical=round(dimensions["technical"], 2),
            on_chain=round(dimensions["on_chain"], 2),
            liquidity=round(dimensions["liquidity"], 2),
            institutional=round(dimensions["institutional"], 2),
            community=round(dimensions["community"], 2),
            developer=round(dimensions["developer"], 2),
            sentiment=round(dimensions["sentiment"], 2),
            narrative=round(dimensions["narrative"], 2),
            risk=round(dimensions["risk"], 2),
            overall_score=round(overall_score, 2),
            confidence=round(confidence, 2),
            priority=priority
        )

    def _apply_delta(self, current_score: float, impact: Impact, multiplier: float = 1.0) -> float:
        """Applies an impact delta to a score, clamped between 0.0 and 100.0."""
        delta = self._IMPACT_DELTA * multiplier
        if impact == Impact.BULLISH:
            return min(100.0, current_score + delta)
        elif impact == Impact.BEARISH:
            return max(0.0, current_score - delta)
        return current_score

    def _assign_priority(self, deviation: float) -> Priority:
        """Assigns priority based on how far the score deviates from neutral."""
        if deviation >= 30.0:
            return Priority.CRITICAL
        elif deviation >= 20.0:
            return Priority.HIGH
        elif deviation >= 10.0:
            return Priority.MEDIUM
        return Priority.LOW
