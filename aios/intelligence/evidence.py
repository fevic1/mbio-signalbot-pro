from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Evidence:

    source: str
    category: str
    claim: str

    confidence: float = 1.0
    verified: bool = False

    url: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class EvidenceCollection:

    def __init__(self):

        self._items: list[Evidence] = []

    def add(self, evidence: Evidence):

        self._items.append(evidence)

    def extend(self, items):

        for item in items:
            self.add(item)

    def all(self):

        return list(self._items)

    def verified(self):

        return [
            e for e in self._items
            if e.verified
        ]

    def by_category(self, category):

        return [
            e for e in self._items
            if e.category == category
        ]

    def confidence(self):

        if not self._items:
            return 0.0

        return (
            sum(e.confidence for e in self._items)
            / len(self._items)
        )

    def as_prompt(self):

        return [
            {
                "source": e.source,
                "category": e.category,
                "claim": e.claim,
                "confidence": e.confidence,
                "verified": e.verified,
                "url": e.url,
                "timestamp": e.timestamp,
                "metadata": e.metadata,
            }
            for e in self._items
        ]


    def normalize(self):

        unique = {}

        for item in self._items:

            key = (
                item.category,
                item.claim.strip().lower(),
            )

            current = unique.get(key)

            if (
                current is None
                or item.confidence > current.confidence
            ):
                unique[key] = item

        self._items = sorted(
            unique.values(),
            key=lambda e: (
                e.verified,
                e.confidence,
                e.timestamp,
            ),
            reverse=True,
        )

        return self


    def conflicts(self):

        conflicts = {}

        for item in self._items:

            key = (
                item.category,
                item.source,
            )

            conflicts.setdefault(
                key,
                set(),
            ).add(
                item.claim.strip()
            )

        return {
            str(k): sorted(v)
            for k, v in conflicts.items()
            if len(v) > 1
        }


    def summary(self):

        self.normalize()

        return {
            "count": len(self._items),
            "verified": len(
                self.verified()
            ),
            "confidence": self.confidence(),
            "conflicts": self.conflicts(),
            "categories": sorted(
                {
                    e.category
                    for e in self._items
                }
            ),
        }


    def ranked(self):

        self.normalize()

        return sorted(
            self._items,
            key=lambda e: (
                e.verified,
                e.confidence,
                e.freshness,
            ),
            reverse=True,
        )


    def top(
        self,
        limit=10,
    ):

        return self.ranked()[:limit]
