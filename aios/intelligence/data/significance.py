from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List

from .models import (
    AnalyticalInsight, 
    AnalysisScore, 
    AnalysisType, 
    SignificanceLevel
)

logger = logging.getLogger(__name__)


class DataSignificance:
    """
    Layer 4: Significance.
    
    Computes standardized scores based on analytical insights.
    
    Responsibilities:
    - Calculate trend_strength (0.0 to 1.0).
    - Calculate statistical_significance (0.0 to 1.0).
    - Calculate anomaly_score (0.0 to 1.0).
    - Assign SignificanceLevel based on composite metrics.
    
    Constraints:
    - NEVER generates explanations or insights (Layer 3).
    - NEVER recommends actions or generates reports (Layer 5).
    - Pure mathematical computation; no side effects.
    """

    @staticmethod
    def score(insights: List[AnalyticalInsight], payload_id: str) -> AnalysisScore:
        """
        Transforms a list of AnalyticalInsights into a single AnalysisScore.
        """
        if not insights:
            return AnalysisScore(
                payload_id=payload_id,
                trend_strength=0.0,
                statistical_significance=0.0,
                anomaly_score=0.0,
                significance_level=SignificanceLevel.NONE,
                scored_at=datetime.now(timezone.utc)
            )

        trend_strengths = []
        correlation_confidences = []
        anomaly_detected = False

        for insight in insights:
            metrics = insight.supporting_metrics
            
            # 1. Extract Trend Strength
            if insight.analysis_type == AnalysisType.TREND:
                volatility = metrics.get("volatility", 0.0)
                change_pct = abs(metrics.get("change_pct", 0.0))
                # Strength is the max of volatility or relative change, capped at 1.0
                strength = min(1.0, max(volatility, change_pct))
                trend_strengths.append(strength)
                
            # 2. Extract Statistical Significance (from Correlation)
            elif insight.analysis_type == AnalysisType.CORRELATION:
                corr = abs(metrics.get("correlation_coefficient", 0.0))
                correlation_confidences.append(corr)
                
            # 3. Detect Anomalies
            elif insight.analysis_type == AnalysisType.ANOMALY:
                anomaly_detected = True

        # Aggregate Scores
        avg_trend_strength = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0.0
        avg_correlation = sum(correlation_confidences) / len(correlation_confidences) if correlation_confidences else 0.5
        
        # Anomaly score is binary in this deterministic model: 1.0 if any outliers found, else 0.0
        # (Can be enhanced later to scale by count, but binary is safest for baseline)
        final_anomaly_score = 1.0 if anomaly_detected else 0.0

        # Determine Overall Significance Level
        level = DataSignificance._determine_level(
            avg_trend_strength, 
            avg_correlation, 
            final_anomaly_score
        )

        return AnalysisScore(
            payload_id=payload_id,
            trend_strength=round(avg_trend_strength, 4),
            statistical_significance=round(avg_correlation, 4),
            anomaly_score=round(final_anomaly_score, 4),
            significance_level=level,
            scored_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _determine_level(
        trend_strength: float, 
        correlation: float, 
        anomaly_score: float
    ) -> SignificanceLevel:
        """
        Maps composite scores to a deterministic SignificanceLevel.
        """
        # Critical/High triggers: Strong trends, high correlation, or any anomalies
        if anomaly_score == 1.0 or trend_strength > 0.7 or correlation > 0.8:
            return SignificanceLevel.HIGH
            
        # Medium triggers: Moderate trends or moderate correlation
        if trend_strength > 0.4 or correlation > 0.5:
            return SignificanceLevel.MEDIUM
            
        # Low triggers: Weak signals
        if trend_strength > 0.1 or correlation > 0.2:
            return SignificanceLevel.LOW
            
        return SignificanceLevel.NONE
