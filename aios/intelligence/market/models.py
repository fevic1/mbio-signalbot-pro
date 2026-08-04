from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class EvidenceCategory(str, Enum):
    MARKET_DATA = "market_data"
    NEWS = "news"
    ON_CHAIN = "on_chain"
    INSTITUTIONAL = "institutional"
    COMMUNITY = "community"
    MACROECONOMIC = "macroeconomic"


class Impact(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceType(str, Enum):
    MCP = "mcp"
    EXCHANGE = "exchange"
    NEWS = "news"
    ONCHAIN = "onchain"
    INTERNAL = "internal"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


# Layer 1: Data Collection Output
@dataclass(slots=True, frozen=True)
class RawEvidence:
    evidence_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    source: str
    source_type: SourceType
    asset: str
    category: EvidenceCategory
    data: Dict[str, Any]
    collected_at: datetime


# Layer 2: Verification Output
@dataclass(slots=True, frozen=True)
class VerifiedEvidence:
    evidence_id: str
    source: str
    source_type: SourceType
    asset: str
    category: EvidenceCategory
    data: Dict[str, Any]
    timestamp: datetime
    verified_at: datetime
    freshness_score: float  # 0.0 to 1.0
    source_confidence: float  # 0.0 to 1.0
    is_duplicate: bool = False


# Layer 3: Intelligence Analysis Output
@dataclass(slots=True, frozen=True)
class IntelligenceEvidence:
    asset: str
    category: EvidenceCategory
    insight: str  # The "Why"
    impact: Impact
    supporting_data: Dict[str, Any] = field(default_factory=dict)


# Layer 4: Scoring Output
@dataclass(slots=True, frozen=True)
class IntelligenceScore:
    asset: str
    fundamental: float = 0.0
    technical: float = 0.0
    on_chain: float = 0.0
    liquidity: float = 0.0
    institutional: float = 0.0
    community: float = 0.0
    developer: float = 0.0
    sentiment: float = 0.0
    narrative: float = 0.0
    risk: float = 0.0
    overall_score: float = 0.0
    confidence: float = 0.0
    priority: Priority = Priority.LOW


# Layer 5: Decision Output
@dataclass(slots=True, frozen=True)
class IntelligenceReport:
    asset: str
    summary: str
    what_changed: str
    evidence: List[IntelligenceEvidence]
    score: IntelligenceScore
    risk_level: RiskLevel
    suggested_actions: List[str]
    generated_at: datetime
    evidence_count: int = 0
