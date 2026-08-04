from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List

from .models import (
    IntelligenceEvidence, 
    IntelligenceScore, 
    IntelligenceReport, 
    Impact, 
    Priority,
    RiskLevel
)

logger = logging.getLogger(__name__)


class MarketReporter:
    """
    Layer 5: Decision Output.
    
    Synthesizes analyzed evidence and scores into a final Verified Intelligence Report.
    
    Responsibilities:
    - Generate a deterministic summary.
    - Extract "What changed" from top insights.
    - Map scores to RiskLevel.
    - Suggest research actions (NEVER trading signals).
    
    Constraints:
    - NEVER generates trading signals (Buy/Sell/Long/Short).
    - NEVER fetches data or calculates scores (Layers 1 & 4).
    - Pure synthesis and formatting.
    """

    # Mapping Priority to RiskLevel
    _PRIORITY_RISK_MAP = {
        Priority.LOW: RiskLevel.LOW,
        Priority.MEDIUM: RiskLevel.MEDIUM,
        Priority.HIGH: RiskLevel.HIGH,
        Priority.CRITICAL: RiskLevel.EXTREME,
    }

    def generate(
        self,
        asset: str,
        intelligence: List[IntelligenceEvidence],
        score: IntelligenceScore,
    ) -> IntelligenceReport:
        """
        Produces the final IntelligenceReport.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Generate Summary
        summary = self._generate_summary(asset, score, len(intelligence))
        
        # 2. Extract "What Changed"
        what_changed = self._extract_changes(intelligence)
        
        # 3. Determine Risk Level
        risk_level = self._PRIORITY_RISK_MAP.get(score.priority, RiskLevel.LOW)
        
        # 4. Suggest Actions (Research only, no trading)
        suggested_actions = self._suggest_actions(score, intelligence)
        
        return IntelligenceReport(
            asset=asset.upper(),
            summary=summary,
            what_changed=what_changed,
            evidence=intelligence,
            score=score,
            risk_level=risk_level,
            suggested_actions=suggested_actions,
            generated_at=now,
            evidence_count=len(intelligence)
        )

    def _generate_summary(self, asset: str, score: IntelligenceScore, count: int) -> str:
        """Creates a concise, non-trading summary based on score metrics."""
        impact_bias = "neutral"
        if score.technical > 55.0 or score.sentiment > 55.0:
            impact_bias = "bullish"
        elif score.technical < 45.0 or score.sentiment < 45.0:
            impact_bias = "bearish"
            
        return (
            f"Verified intelligence for {asset} indicates a {impact_bias} bias "
            f"with {score.priority.value} priority across {count} sources. "
            f"Overall score: {score.overall_score}/100 (Confidence: {score.confidence:.0%})."
        )

    def _extract_changes(self, intelligence: List[IntelligenceEvidence]) -> str:
        """Concatenates the top insights to explain what changed."""
        if not intelligence:
            return "No significant changes detected in verified data sources."
        
        # Take up to the top 3 insights
        top_insights = [ev.insight for ev in intelligence[:3]]
        return " | ".join(top_insights)

    def _suggest_actions(
        self, 
        score: IntelligenceScore, 
        intelligence: List[IntelligenceEvidence]
    ) -> List[str]:
        """Suggests research actions based on priority and impact. STRICTLY NO TRADING SIGNALS."""
        actions = []
        
        if score.priority in (Priority.HIGH, Priority.CRITICAL):
            actions.append("Conduct immediate review of market structure and liquidity depth.")
            
        if score.technical > 60.0:
            actions.append("Investigate sources of capital inflow and volume spikes.")
        elif score.technical < 40.0:
            actions.append("Review support levels and recent large wallet distributions.")
            
        if score.sentiment < 40.0:
            actions.append("Monitor community channels for negative narrative propagation.")
            
        if not actions:
            actions.append("Continue standard monitoring of on-chain and market metrics.")
            
        return actions
