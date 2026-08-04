from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from .models import RawEvidence, EvidenceCategory, SourceType

logger = logging.getLogger(__name__)


class MarketCollector:
    """
    Layer 1: Data Collection.
    
    Transforms raw tool execution results from the main AIOS pipeline
    into standardized, immutable RawEvidence objects.
    
    Responsibilities:
    - Filter successful tool results.
    - Map categories to source types.
    - Timestamp collection.
    
    Constraints:
    - Never scores or makes decisions.
    - Never fetches data directly (relies on foundation ToolExecutor).
    """

    @staticmethod
    def collect(
        asset: str,
        category: EvidenceCategory,
        tool_results: List[Dict[str, Any]],
    ) -> List[RawEvidence]:
        """
        Converts a list of tool execution results into RawEvidence.
        """
        evidence_list: List[RawEvidence] = []
        now = datetime.now(timezone.utc)
        source_type = MarketCollector._resolve_source_type(category)

        for result in tool_results:
            if not result.get("success"):
                logger.debug(
                    f"Skipping failed tool result for {asset}: {result.get('error')}"
                )
                continue

            evidence = RawEvidence(
                source=result.get("server", "unknown"),
                source_type=source_type,
                asset=asset.upper(),
                category=category,
                data=result.get("content", {}),
                collected_at=now,
            )
            evidence_list.append(evidence)

        return evidence_list

    @staticmethod
    def _resolve_source_type(category: EvidenceCategory) -> SourceType:
        """Maps evidence categories to their primary source types."""
        mapping = {
            EvidenceCategory.MARKET_DATA: SourceType.EXCHANGE,
            EvidenceCategory.NEWS: SourceType.NEWS,
            EvidenceCategory.ON_CHAIN: SourceType.ONCHAIN,
            EvidenceCategory.INSTITUTIONAL: SourceType.MCP,
            EvidenceCategory.COMMUNITY: SourceType.MCP,
            EvidenceCategory.MACROECONOMIC: SourceType.NEWS,
        }
        return mapping.get(category, SourceType.INTERNAL)
