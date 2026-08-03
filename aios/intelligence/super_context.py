from aios.intelligence.evidence import EvidenceCollection
import asyncio
import os
import re
from time import perf_counter
from typing import Any, Dict, List

from aios.memory.search.retriever import MemoryRetriever


class SuperContextBuilder:
    """Bounded, read-only first-turn context retrieval."""

    _SECRET_PATTERNS = (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password|authorization)"
            r"\b\s*[:=]\s*[^\s,;]+"
        ),
        re.compile(r"\b(?:sk|gsk|sk-or-v1)-[A-Za-z0-9._-]{12,}\b"),
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{12,}\b"),
    )

    def __init__(
        self,
        max_items: int = 5,
        max_chars: int = 6000,
        item_max_chars: int = 1600,
        timeout_seconds: float = 0.35,
    ):
        self.enabled = (
            os.getenv("AIOS_SUPER_CONTEXT_ENABLED", "true")
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
        )
        self.max_items = max(
            1,
            int(os.getenv("AIOS_SUPER_CONTEXT_MAX_ITEMS", max_items)),
        )
        self.max_chars = max(
            500,
            int(os.getenv("AIOS_SUPER_CONTEXT_MAX_CHARS", max_chars)),
        )
        self.item_max_chars = max(
            200,
            int(
                os.getenv(
                    "AIOS_SUPER_CONTEXT_ITEM_MAX_CHARS",
                    item_max_chars,
                )
            ),
        )
        self.timeout_seconds = max(
            0.05,
            float(
                os.getenv(
                    "AIOS_SUPER_CONTEXT_TIMEOUT_SECONDS",
                    timeout_seconds,
                )
            ),
        )

    def _redact(self, value: Any) -> str:
        text = str(value or "").strip()

        for pattern in self._SECRET_PATTERNS:
            text = pattern.sub("[REDACTED]", text)

        return text

    @staticmethod
    def _enum_value(value: Any) -> str:
        return str(getattr(value, "value", value or ""))

    def _retrieve(
        self,
        query: str,
        memory_router: Any,
    ) -> List[Dict[str, Any]]:
        retriever = MemoryRetriever(memory_router)
        ranked = retriever.search_memory(query) or []

        entries = []
        characters_used = 0

        for result in ranked:
            if len(entries) >= self.max_items:
                break

            if not isinstance(result, dict):
                continue

            record = result.get("record")
            if record is None:
                continue

            content = self._redact(
                getattr(record, "content", "")
            )

            if not content:
                continue

            remaining = self.max_chars - characters_used
            if remaining <= 0:
                break

            content = content[
                : min(self.item_max_chars, remaining)
            ]

            try:
                relevance = round(
                    float(result.get("score", 0.0)),
                    4,
                )
            except (TypeError, ValueError):
                relevance = 0.0

            entry = {
                "kind": "memory",
                "memory_type": self._enum_value(
                    getattr(record, "memory_type", "")
                ),
                "importance": self._enum_value(
                    getattr(record, "importance", "")
                ),
                "relevance": relevance,
                "content": content,
            }

            entries.append(entry)
            characters_used += len(content)

        return entries

    async def build(
        self,
        query: str,
        services: Dict[str, Any],
    ) -> Dict[str, Any]:
        started = perf_counter()

        if not self.enabled:
            return {
                "status": "disabled",
                "entries": [],
                "characters_used": 0,
                "latency_ms": 0.0,
            }

        memory_router = services.get("memory_router")

        if memory_router is None:
            return {
                "status": "unavailable",
                "entries": [],
                "characters_used": 0,
                "latency_ms": round(
                    (perf_counter() - started) * 1000,
                    2,
                ),
            }

        try:
            # PersistentMemoryRouter owns a SQLite connection created on
            # the application thread. Keep retrieval on that same thread;
            # moving it through asyncio.to_thread violates SQLite affinity.
            entries = self._retrieve(
                query,
                memory_router,
            )

            elapsed_seconds = perf_counter() - started
            status = (
                "ready"
                if elapsed_seconds <= self.timeout_seconds
                else "ready_over_budget"
            )

            return {
                "status": status,
                "source": "persistent_memory",
                "read_only": True,
                "entries": entries,
                "selected_count": len(entries),
                "characters_used": sum(
                    len(item["content"])
                    for item in entries
                ),
                "latency_ms": round(
                    (perf_counter() - started) * 1000,
                    2,
                ),
            }

        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "entries": [],
                "characters_used": 0,
                "latency_ms": round(
                    (perf_counter() - started) * 1000,
                    2,
                ),
            }

        except Exception as error:
            return {
                "status": "failed",
                "entries": [],
                "characters_used": 0,
                "error_type": type(error).__name__,
                "latency_ms": round(
                    (perf_counter() - started) * 1000,
                    2,
                ),
            }
