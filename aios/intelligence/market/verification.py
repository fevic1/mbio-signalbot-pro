from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from .models import RawEvidence, VerifiedEvidence, SourceType

logger = logging.getLogger(__name__)


class MarketVerifier:
    """
    Layer 2: Verification.
    
    Validates the integrity and quality of collected evidence.
    
    Responsibilities:
    - Deduplicate evidence based on (asset, category, source).
    - Assign freshness scores based on collection time.
    - Assign source confidence based on source type.
    - Record verified_at timestamp.
    - Preserve evidence_id through the pipeline.
    
    Constraints:
    - Never analyzes the meaning of the data (Layer 3).
    - Never makes trading decisions (Layer 5).
    """

    # Confidence mapping based on source reliability
    _SOURCE_CONFIDENCE: Dict[SourceType, float] = {
        SourceType.EXCHANGE: 0.95,
        SourceType.ONCHAIN: 0.90,
        SourceType.NEWS: 0.75,
        SourceType.MCP: 0.60,
        SourceType.INTERNAL: 0.50,
    }

    @staticmethod
    def verify(raw_evidence_list: List[RawEvidence]) -> List[VerifiedEvidence]:
        """
        Transforms RawEvidence into VerifiedEvidence with deduplication,
        freshness scoring, and source confidence.
        """
        verified_list: List[VerifiedEvidence] = []
        seen_keys: set[Tuple[str, str, str]] = set()
        now = datetime.now(timezone.utc)

        for raw in raw_evidence_list:
            # 1. Deduplication: Track unique (asset, category, source)
            dedup_key = (raw.asset, raw.category.value, raw.source)
            is_duplicate = dedup_key in seen_keys
            seen_keys.add(dedup_key)

            if is_duplicate:
                logger.debug(
                    f"Duplicate evidence detected for {raw.asset} "
                    f"from {raw.source} (ID: {raw.evidence_id[:8]}...)"
                )

            # 2. Freshness Score
            freshness = MarketVerifier._calculate_freshness(raw.collected_at, now)

            # 3. Source Confidence
            confidence = MarketVerifier._SOURCE_CONFIDENCE.get(
                raw.source_type, 0.50
            )

            # 4. Build VerifiedEvidence (preserving evidence_id)
            verified = VerifiedEvidence(
                evidence_id=raw.evidence_id,
                source=raw.source,
                source_type=raw.source_type,
                asset=raw.asset,
                category=raw.category,
                data=raw.data,
                timestamp=raw.collected_at,  # Original collection time
                verified_at=now,              # Verification time
                freshness_score=freshness,
                source_confidence=confidence,
                is_duplicate=is_duplicate,
            )
            verified_list.append(verified)

        return verified_list

    @staticmethod
    def _calculate_freshness(
        collected_at: datetime, 
        now: datetime
    ) -> float:
        """
        Calculates a 0.0 to 1.0 freshness score based on age.
        """
        # Handle naive datetimes for safety
        if collected_at.tzinfo is None:
            collected_at = collected_at.replace(tzinfo=timezone.utc)
            
        age_hours = (now - collected_at).total_seconds() / 3600.0

        if age_hours < 1.0:
            return 1.0
        elif age_hours < 24.0:
            return 0.75
        elif age_hours < 72.0:
            return 0.50
        else:
            return 0.25
