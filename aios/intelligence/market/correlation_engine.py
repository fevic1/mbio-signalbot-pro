from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Dict, List, Tuple

from .models import Correlation, Narrative, Trend
from ..knowledge.graph import KnowledgeGraph

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Detects cross-platform and cross-entity correlations.
    
    Analyzes co-mentions, shared platforms, and narrative alignment
    to identify correlated market movements between entities.
    """
    
    __slots__ = ("_graph",)
    
    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph
    
    def detect_correlations(
        self,
        narratives: List[Narrative],
        trends: List[Trend],
        min_confidence: float = 0.5,
    ) -> List[Correlation]:
        """
        Detect correlations between entities based on narratives and trends.
        
        Args:
            narratives: List of Narrative objects
            trends: List of Trend objects
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of detected Correlation objects
        """
        correlations = []

        # Build trend lookup
        trend_map = {
            t.entity_id: t
            for t in trends
            if t.confidence >= min_confidence
        }
        
        # 1. Graph-based correlations (direct relationships)
        graph_correlations = self._detect_graph_correlations(narratives, trend_map)
        correlations.extend(graph_correlations)
        
        # 2. Narrative alignment correlations (similar sentiment trends)
        narrative_correlations = self._detect_narrative_correlations(narratives)
        correlations.extend(narrative_correlations)
        
        # Deduplicate and sort by correlation strength
        seen = set()
        unique_correlations = []
        for corr in correlations:
            # Create a canonical pair ID to avoid duplicates (A-B is same as B-A)
            pair = tuple(sorted([corr.entity_a_id, corr.entity_b_id]))
            pair_id = f"{pair[0]}_{pair[1]}_{corr.relationship_type}"
            
            if pair_id not in seen:
                seen.add(pair_id)
                unique_correlations.append(corr)
        
        unique_correlations.sort(key=lambda c: c.correlation_strength, reverse=True)
        
        logger.info(f"Detected {len(unique_correlations)} unique correlations")
        return unique_correlations
    
    def _detect_graph_correlations(
        self,
        narratives: List[Narrative],
        trend_map: Dict[str, Trend],
    ) -> List[Correlation]:
        """Detect correlations based on existing graph relationships."""
        correlations = []
        
        # Get entities with active narratives
        active_entities = {n.entity_id for n in narratives if n.confidence >= 0.5}
        
        for entity_id in active_entities:
            # Check outgoing edges
            outgoing = self._graph.get_outgoing_edges(entity_id)
            for edge in outgoing:
                if edge.target_id in active_entities and edge.weight >= 0.5:
                    # Calculate correlation strength based on edge weight and narrative confidence
                    source_narrative = next((n for n in narratives if n.entity_id == entity_id), None)
                    target_narrative = next((n for n in narratives if n.entity_id == edge.target_id), None)
                    
                    if source_narrative and target_narrative:
                        trend_bonus = 0.0

                        src_trend = trend_map.get(entity_id)
                        dst_trend = trend_map.get(edge.target_id)

                        if (
                            src_trend is not None
                            and dst_trend is not None
                            and src_trend.direction == dst_trend.direction
                        ):
                            trend_bonus = (
                                abs(src_trend.momentum)
                                + abs(dst_trend.momentum)
                            ) / 2.0

                        strength = (
                            edge.weight
                            + source_narrative.confidence
                            + target_narrative.confidence
                            + trend_bonus
                        ) / 4.0
                        
                        correlations.append(Correlation(
                            entity_a_id=entity_id,
                            entity_b_id=edge.target_id,
                            correlation_strength=round(strength, 4),
                            confidence=round(strength, 4),
                            platforms=tuple(
                                sorted(
                                    p for p in set(
                                        source_narrative.metadata.get("platforms","").split(",")
                                        + target_narrative.metadata.get("platforms","").split(",")
                                    )
                                    if p
                                )
                            ),
                            relationship_type=edge.relation_type.value,
                            detected_at=datetime.now(timezone.utc),
                            metadata={
                                "source": "graph_relationship",
                                "edge_weight": str(edge.weight),
                            }
                        ))
        
        correlations.sort(key=lambda c: c.correlation_strength, reverse=True)
        return correlations
    
    def _detect_narrative_correlations(
        self,
        narratives: List[Narrative],
    ) -> List[Correlation]:
        """Detect correlations based on narrative sentiment alignment."""
        correlations = []
        
        # Group narratives by sentiment
        sentiment_groups: Dict[str, List[Narrative]] = defaultdict(list)
        for narrative in narratives:
            if narrative.confidence >= 0.5:
                sentiment_groups[narrative.sentiment.value].append(narrative)
        
        # Find entities with aligned sentiments
        for sentiment, group in sentiment_groups.items():
            if len(group) < 2:
                continue
            
            # Compare all pairs in the same sentiment group
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    nar_a = group[i]
                    nar_b = group[j]
                    
                    # Skip if already correlated via graph
                    if self._graph.has_edge(nar_a.entity_id, nar_b.entity_id) or \
                       self._graph.has_edge(nar_b.entity_id, nar_a.entity_id):
                        continue
                    
                    # Calculate alignment strength
                    strength = (nar_a.confidence + nar_b.confidence) / 2.0
                    
                    # Only report strong alignments
                    if strength >= 0.6:
                        correlations.append(Correlation(
                            entity_a_id=nar_a.entity_id,
                            entity_b_id=nar_b.entity_id,
                            correlation_strength=round(strength, 4),
                            confidence=round(strength, 4),
                            platforms=tuple(
                                sorted(
                                    p for p in set(
                                        nar_a.metadata.get("platforms","").split(",")
                                        + nar_b.metadata.get("platforms","").split(",")
                                    )
                                    if p
                                )
                            ),
                            relationship_type=f"narrative_alignment_{sentiment}",
                            detected_at=datetime.now(timezone.utc),
                            metadata={
                                "source": "narrative_alignment",
                                "sentiment": sentiment,
                            }
                        ))
        
        return correlations
    
    def get_correlated_entities(
        self,
        entity_id: str,
        min_strength: float = 0.5,
    ) -> List[Tuple[str, float, str]]:
        """
        Get all entities correlated with a specific entity.
        
        Returns:
            List of tuples: (correlated_entity_id, correlation_strength, relationship_type)
        """
        correlations = []
        
        # Check outgoing
        outgoing = self._graph.get_outgoing_edges(entity_id)
        for edge in outgoing:
            if edge.weight >= min_strength:
                correlations.append((edge.target_id, edge.weight, edge.relation_type.value))
        
        # Check incoming
        incoming = self._graph.get_incoming_edges(entity_id)
        for edge in incoming:
            if edge.weight >= min_strength:
                correlations.append((edge.source_id, edge.weight, edge.relation_type.value))
        
        # Sort by strength descending
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        return correlations
