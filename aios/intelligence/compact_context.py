import re
from typing import Any

from aios.memory.context.budget import ContextBudget


class CompactContextBuilder:
    """Select a small, relevant AIOS catalog for each request."""

    BLOCKED_TOOL_TERMS = {
        "trade",
        "trading",
        "order",
        "wallet",
        "send",
        "swap",
        "grid",
        "position",
        "balance",
    }

    def __init__(self, max_items: int = 8, max_chars: int = 5000):
        self.budget = ContextBudget(max_items=max_items)
        self.max_chars = max_chars

    @staticmethod
    def _tokens(value: Any) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-z0-9_]+", str(value).lower())
            if len(token) > 1
        }

    @staticmethod
    def _value(item: Any, key: str, default: Any = "") -> Any:
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def _entry(self, kind: str, item: Any) -> dict[str, Any]:
        name = str(
            self._value(item, "name")
            or self._value(item, "server_id")
            or self._value(item, "id")
            or "unknown"
        )
        description = str(
            self._value(item, "description")
            or self._value(item, "role")
            or ""
        ).strip()
        capabilities = self._value(item, "capabilities", []) or []

        if not isinstance(capabilities, (list, tuple, set)):
            capabilities = [str(capabilities)]

        return {
            "kind": kind,
            "name": name[:160],
            "description": description[:500],
            "capabilities": [str(value)[:120] for value in capabilities[:12]],
        }

    def _tool_allowed(self, entry: dict[str, Any]) -> bool:
        text = " ".join((
            entry["name"],
            entry["description"],
        )).lower()

        return not any(
            re.search(rf"\b{re.escape(term)}\b", text)
            for term in self.BLOCKED_TOOL_TERMS
        )

    def _score(
        self,
        query_tokens: set[str],
        capability: str,
        entry: dict[str, Any],
    ) -> float:
        searchable = " ".join((
            entry["name"],
            entry["description"],
            " ".join(entry["capabilities"]),
        ))
        entry_tokens = self._tokens(searchable)
        overlap = len(query_tokens & entry_tokens)

        score = float(overlap * 10)

        if capability and capability.lower() in {
            value.lower()
            for value in entry["capabilities"]
        }:
            score += 25

        if capability and capability.lower() in entry["name"].lower():
            score += 15

        if entry["kind"] == "capability" and entry["name"].lower() == capability.lower():
            score += 40

        return score

    def build(
        self,
        query: str,
        capability: str,
        tools: list[Any] | None = None,
        skills: list[Any] | None = None,
        capabilities: list[Any] | None = None,
        agents: list[Any] | None = None,
    ) -> dict[str, Any]:
        entries = []

        for kind, collection in (
            ("tool", tools or []),
            ("skill", skills or []),
            ("capability", capabilities or []),
            ("agent", agents or []),
        ):
            for item in collection:
                entry = self._entry(kind, item)

                if kind == "tool" and not self._tool_allowed(entry):
                    continue

                entries.append(entry)

        query_tokens = self._tokens(query)

        ranked = sorted(
            entries,
            key=lambda entry: self._score(
                query_tokens,
                capability,
                entry,
            ),
            reverse=True,
        )

        relevant = [
            entry
            for entry in ranked
            if self._score(query_tokens, capability, entry) > 0
        ]

        if not relevant:
            relevant = [
                entry
                for entry in ranked
                if (
                    entry["kind"] == "capability"
                    and entry["name"].lower() == capability.lower()
                )
            ]

        selected = self.budget.apply(relevant)
        bounded = []
        used_chars = 0

        for entry in selected:
            size = len(str(entry))

            if used_chars + size > self.max_chars:
                break

            bounded.append(entry)
            used_chars += size

        return {
            "query": query[:500],
            "selected_count": len(bounded),
            "available_count": len(entries),
            "character_budget": self.max_chars,
            "characters_used": used_chars,
            "entries": bounded,
        }
