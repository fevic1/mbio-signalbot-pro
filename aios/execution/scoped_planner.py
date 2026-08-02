import re
from uuid import uuid4
from typing import Any


class ScopedWorkflowPlanner:
    """Create small, deterministic, read-only AIOS workflow plans."""

    BLOCKED_ACTIONS = {
        "buy",
        "sell",
        "trade",
        "place order",
        "execute order",
        "send funds",
        "transfer funds",
        "swap",
        "deploy grid",
        "open position",
        "close position",
    }

    COMPLEX_TERMS = {
        "research",
        "compare",
        "analyze",
        "investigate",
        "verify",
        "evaluate",
        "look into",
        "find out",
        "summarize",
        "latest",
        "sources",
    }

    def __init__(self, execution_planner=None, max_steps: int = 6):
        self.execution_planner = execution_planner
        self.max_steps = max_steps

    @staticmethod
    def _contains(text: str, terms: set[str]) -> bool:
        return any(
            re.search(rf"\b{re.escape(term)}\b", text)
            for term in terms
        )

    def should_plan(self, query: str, category: str) -> bool:
        lowered = query.lower()

        return (
            category == "research"
            or self._contains(lowered, self.COMPLEX_TERMS)
            or len(query.split()) >= 18
            or " and " in lowered
            or " then " in lowered
        )

    @staticmethod
    def _catalog_tools(catalog: list[dict[str, Any]]) -> list[str]:
        return [
            str(entry.get("name"))
            for entry in catalog
            if entry.get("kind") == "tool"
        ]

    def _pipeline(self, category: str) -> list[str]:
        if (
            self.execution_planner
            and hasattr(self.execution_planner, "get_pipeline")
        ):
            pipeline = self.execution_planner.get_pipeline(category)

            if pipeline:
                return list(pipeline)

        if category == "research":
            return ["research", "reasoning", "verification"]

        return [category or "reasoning", "verification"]

    def plan(
        self,
        query: str,
        category: str,
        catalog: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        if not self.should_plan(query, category):
            return None

        lowered = query.lower()
        blocked = self._contains(lowered, self.BLOCKED_ACTIONS)
        tools = self._catalog_tools(catalog or [])
        pipeline = self._pipeline(category)[:self.max_steps]

        steps = []
        previous = None

        for index, capability in enumerate(pipeline, 1):
            selected_tools = []

            if capability == "research":
                selected_tools = [
                    name
                    for name in tools
                    if "search" in name or "fetch" in name
                ][:2]

            step = {
                "id": f"step_{index}",
                "name": capability,
                "capability": capability,
                "mode": "read_only",
                "depends_on": [previous] if previous else [],
                "tools": selected_tools,
                "status": "blocked" if blocked else "planned",
            }
            steps.append(step)
            previous = step["id"]

        requires_council = any(
            term in lowered
            for term in (
                "conflicting evidence",
                "high stakes",
                "change aios",
                "improve aios",
                "modify policy",
                "provider conflict",
            )
        )

        return {
            "plan_id": str(uuid4()),
            "objective": query[:1000],
            "category": category,
            "mode": "read_only",
            "status": "blocked" if blocked else "planned",
            "blocked_reason": (
                "State-changing or trading execution is disabled."
                if blocked
                else None
            ),
            "steps": steps,
            "council_gate": {
                "required": requires_council,
                "reason": (
                    "Uncertainty, conflict, or AIOS change requires review."
                    if requires_council
                    else None
                ),
            },
        }
