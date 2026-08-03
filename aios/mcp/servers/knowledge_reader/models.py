from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class DocumentChunk:
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ReaderResponse:
    success: bool
    document_id: str
    metadata: dict
    content: dict
    citations: list
    processing_time_ms: float
