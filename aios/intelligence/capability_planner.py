from __future__ import annotations

import logging
from dataclasses import dataclass
from difflib import SequenceMatcher

from .parameter_planner import ParameterPlanner

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CapabilityCandidate:
    server: str
    tool: str
    score: float


class CapabilityPlanner:

    async def plan(self, registry, request: str):
        request = str(request).lower()
        candidates = []

        all_tools = (
            await registry.get_all_tools()
            if hasattr(registry, "get_all_tools") else {}
        )

        for server, tools in all_tools.items():
            for tool in tools.keys():
                score = max(
                    SequenceMatcher(None, request, tool.lower()).ratio(),
                    SequenceMatcher(None, request, server.lower()).ratio(),
                )
                keywords = (tool + " " + server).lower()
                for token in request.split():
                    if token in keywords:
                        score += 0.15
                candidates.append(
                    CapabilityCandidate(server, tool, round(score, 3))
                )

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    async def select(self, registry, request, limit=5):
        planner = ParameterPlanner()
        planned = await self.plan(registry, request)
        result = []

        for c in planned[:limit]:
            validation = await planner.validate_and_build(
                registry, c.server, c.tool, request
            )

            step = {
                "server": c.server,
                "tool": c.tool,
                "score": c.score,
                "arguments": validation.arguments,
            }

            if not validation.success:
                step["validation_error"] = validation.error

            result.append(step)

        return result
