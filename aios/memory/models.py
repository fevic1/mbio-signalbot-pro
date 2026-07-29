from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any
import uuid


class MemoryType(str, Enum):

    PROJECT = "project"

    AGENT = "agent"

    DECISION = "decision"

    KNOWLEDGE = "knowledge"

    OPERATIONAL = "operational"

    FEEDBACK = "feedback"



class MemoryImportance(str, Enum):

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"



@dataclass
class MemoryMetadata:

    source: str = "aios"

    tags: list[str] = field(
        default_factory=list
    )

    confidence: float = 1.0

    access_count: int = 0



@dataclass
class MemoryRecord:

    content: dict[str, Any]

    memory_type: MemoryType

    importance: MemoryImportance = (
        MemoryImportance.NORMAL
    )

    metadata: MemoryMetadata = field(
        default_factory=MemoryMetadata
    )

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def access(self):

        self.metadata.access_count += 1


    def describe(self):

        return {
            "id": self.id,
            "type": self.memory_type.value,
            "importance":
                self.importance.value,
            "content":
                self.content,
            "metadata":
                {
                    "source":
                        self.metadata.source,
                    "tags":
                        self.metadata.tags,
                    "confidence":
                        self.metadata.confidence,
                    "access_count":
                        self.metadata.access_count,
                },
            "created_at":
                self.created_at,
        }


@dataclass
class MemoryEntry:

    content: dict[str, Any] = field(
        default_factory=dict
    )

    category: str = "general"

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    def describe(self):
        return {
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
        }
