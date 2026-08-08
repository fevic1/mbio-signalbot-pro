from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from .models import Narrative, NarrativeSentiment
from ..knowledge.models import AggregatedSignal, SignalType
from ..knowledge.graph import KnowledgeGraph
from ..knowledge.temporal_graph import TemporalGraph

logger = logging.getLogger(__name__)


class NarrativeDetector:
    """
    Detects market narratives from aggregated signals.
    
    Analyzes signal patterns, sentiment, and entity relationships
    to identify bullish, bearish, or neutral narratives.
    """
    
    __slots__ = ("_graph", "_temporal", "_sentiment_thresholds")
    
    def __init__(
        self,
        graph: KnowledgeGraph,
        temporal: TemporalGraph,
        sentiment_thresholds: Optional[Dict[str, float]] = None,
    ):
        self._graph = graph
        self._temporal = temporal
        
        # Default sentiment thresholds
        self._sentiment_thresholds = sentiment_thresholds or {
            "strongly_bullish": 0.8,
            "bullish": 0.6,
            "neutral": 0.4,
            "bearish": 0.2,
            "strongly_bearish": 0.0,
        }
    
    def detect_narratives(
        self,
        signals: List[AggregatedSignal],
        min_confidence: float = 0.5,
    ) -> List[Narrative]:
        """
        Detect narratives from aggregated signals.
        
        Args:
            signals: List of AggregatedSignal objects
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of detected Narrative objects
        """
        narratives = []
        
        # Group signals by entity
        entity_signals: Dict[str, List[AggregatedSignal]] = {}
        for signal in signals:
            if signal.confidence >= min_confidence:
                if signal.target_entity_id not in entity_signals:
                    entity_signals[signal.target_entity_id] = []
                entity_signals[signal.target_entity_id].append(signal)
        
        # Analyze each entity's signals
        for entity_id, entity_signal_list in entity_signals.items():
            narrative = self._analyze_entity_narrative(entity_id, entity_signal_list)
            if narrative:
                narratives.append(narrative)
        
        # Sort by strength descending
        narratives.sort(key=lambda n: n.strength, reverse=True)
        
        logger.info(f"Detected {len(narratives)} narratives from {len(signals)} signals")
        return narratives
    
    def _analyze_entity_narrative(
        self,
        entity_id: str,
        signals: List[AggregatedSignal],
    ) -> Optional[Narrative]:
        """Analyze signals for a single entity to detect narrative."""
        if not signals:
            return None
        
        # Calculate weighted sentiment score
        sentiment_scores = []
        signal_ids = []
        
        for signal in signals:
            # Map signal type to sentiment
            sentiment = self._signal_type_to_sentiment(signal.signal_type)
            weighted_score = sentiment * signal.aggregated_score * signal.confidence
            sentiment_scores.append(weighted_score)
            signal_ids.append(signal.signal_id)
        
        if not sentiment_scores:
            return None
        
        # Average sentiment (weighted by confidence)
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Normalize to 0.0 - 1.0 range
        normalized_sentiment = (avg_sentiment + 1.0) / 2.0
        
        # Classify narrative sentiment
        narrative_sentiment = self._classify_sentiment(normalized_sentiment)
        
        # Calculate narrative strength (based on signal count and confidence)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        signal_factor = min(1.0, len(signals) / 5.0)
        confidence_factor = avg_confidence
        strength = round((signal_factor * 0.6) + (confidence_factor * 0.4), 4)
        
        # Generate narrative text
        entity = self._graph.get_entity(entity_id)
        entity_name = (
            entity.name
            if entity is not None
            else entity_id.removeprefix("ENT_").replace("_", " ").title()
        )
        narrative_text = self._generate_narrative_text(entity_name, narrative_sentiment, strength)
        
        # Calculate expiration (24 hours from now)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        return Narrative(
            entity_id=entity_id,
            sentiment=narrative_sentiment,
            strength=round(strength, 4),
            confidence=round(avg_confidence, 4),
            narrative_text=narrative_text,
            supporting_signals=tuple(signal_ids),
            expires_at=expires_at,
            metadata={"signal_count": str(len(signals))},
        )
    
    def _signal_type_to_sentiment(self, signal_type: SignalType) -> float:
        """Map signal type to sentiment score (-1.0 to 1.0)."""
        sentiment_map = {
            SignalType.PARTNERSHIP: 0.8,
            SignalType.INVESTMENT: 0.9,
            SignalType.LAUNCH: 0.6,
            SignalType.UPGRADE: 0.5,
            SignalType.EXPANSION: 0.7,
            SignalType.HIRES: 0.3,
            SignalType.DEPARTURE: -0.4,
            SignalType.REGULATORY: -0.6,
            SignalType.COMPLIANCE: 0.2,
            SignalType.VULNERABILITY: -0.8,
            SignalType.AUDIT: 0.3,
            SignalType.SENTIMENT: 0.0,
            SignalType.MENTION: 0.0,
        }
        return sentiment_map.get(signal_type, 0.0)
    
    def _classify_sentiment(self, score: float) -> NarrativeSentiment:
        """Classify sentiment score into NarrativeSentiment enum."""
        if score >= self._sentiment_thresholds["strongly_bullish"]:
            return NarrativeSentiment.STRONGLY_BULLISH
        elif score >= self._sentiment_thresholds["bullish"]:
            return NarrativeSentiment.BULLISH
        elif score >= self._sentiment_thresholds["neutral"]:
            return NarrativeSentiment.NEUTRAL
        elif score >= self._sentiment_thresholds["bearish"]:
            return NarrativeSentiment.BEARISH
        else:
            return NarrativeSentiment.STRONGLY_BEARISH
    
    def _generate_narrative_text(
        self,
        entity_name: str,
        sentiment: NarrativeSentiment,
        strength: float,
    ) -> str:
        """Generate human-readable narrative text."""
        sentiment_descriptions = {
            NarrativeSentiment.STRONGLY_BULLISH: "strong positive momentum",
            NarrativeSentiment.BULLISH: "positive sentiment",
            NarrativeSentiment.NEUTRAL: "neutral market positioning",
            NarrativeSentiment.BEARISH: "negative sentiment",
            NarrativeSentiment.STRONGLY_BEARISH: "strong negative pressure",
        }
        
        description = sentiment_descriptions.get(sentiment, "unclear sentiment")
        strength_adj = "significant" if strength > 0.7 else "moderate" if strength > 0.4 else "weak"
        
        return f"{entity_name} showing {strength_adj} {description} across multiple platforms"
