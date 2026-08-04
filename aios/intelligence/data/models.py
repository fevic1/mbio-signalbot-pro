from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DataType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    SQL = "sql"
    JSON = "json"
    PDF = "pdf"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    PERFORMANCE = "performance"


class AnalysisType(str, Enum):
    STATISTICAL = "statistical"
    TIME_SERIES = "time_series"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"
    TREND = "trend"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"
    VOLATILE = "volatile"


class SignificanceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


# Layer 1: Ingestion Output
@dataclass(slots=True, frozen=True)
class DataPayload:
    source_type: DataType
    data: Any  # Will hold pandas DataFrame, list of dicts, or raw text
    metadata: Dict[str, Any] = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=datetime.utcnow)
    # Moved to the end to satisfy dataclass default-argument rules
    payload_id: str = field(default_factory=lambda: uuid.uuid4().hex)


# Layer 2: Profiling Output
@dataclass(slots=True, frozen=True)
class DataProfile:
    payload_id: str
    row_count: int
    column_count: int
    null_counts: Dict[str, int]
    data_types: Dict[str, str]
    basic_stats: Dict[str, Any]  # Mean, median, std, min, max for numeric cols
    profiled_at: datetime = field(default_factory=datetime.utcnow)


# Layer 3: Analysis Output
@dataclass(slots=True, frozen=True)
class AnalyticalInsight:
    payload_id: str
    analysis_type: AnalysisType
    finding: str  # The "What happened"
    trend_direction: Optional[TrendDirection] = None
    supporting_metrics: Dict[str, float] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


# Layer 4: Significance Output
@dataclass(slots=True, frozen=True)
class AnalysisScore:
    payload_id: str
    trend_strength: float  # 0.0 to 1.0
    statistical_significance: float  # p-value or confidence score
    anomaly_score: float  # 0.0 to 1.0
    significance_level: SignificanceLevel
    scored_at: datetime = field(default_factory=datetime.utcnow)


# Layer 5: Reporting Output
@dataclass(slots=True, frozen=True)
class AnalysisReport:
    payload_id: str
    summary: str
    key_findings: List[AnalyticalInsight]
    score: AnalysisScore
    chart_data: List[Dict[str, Any]]  # Structured data for frontend visualization
    suggested_actions: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)
