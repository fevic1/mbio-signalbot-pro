import logging
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CapabilityCandidate:
    server: str
    tool: str
    score: float


class CapabilityPlanner:

    async def plan(
        self,
        registry,
        request: str,
    ):
        request = str(request).lower()

        candidates = []

        all_tools = await registry.get_all_tools() if hasattr(registry, "get_all_tools") else {}

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
                    CapabilityCandidate(
                        server,
                        tool,
                        round(score, 3),
                    )
                )

        candidates.sort(
            key=lambda c: c.score,
            reverse=True,
        )

        return candidates

    async def select(
        self,
        registry,
        request,
        limit=5,
    ):
        planner = ParameterPlanner()
        
        planned = await self.plan(
            registry,
            request,
        )

        result = []

        for c in planned[:limit]:
            args = await planner.build_arguments(
                registry,
                c.server,
                c.tool,
                request,
            )
            
            result.append(
                {
                    "server": c.server,
                    "tool": c.tool,
                    "score": c.score,
                    "arguments": args,
                }
            )

        return result


class ParameterPlanner:

    async def build_arguments(
        self,
        registry,
        server,
        tool,
        request,
    ):
        schema = await registry.get_tool_schema_async(server, tool)
        
        if not schema:
            return {}

        properties = schema.get("inputSchema", {}).get("properties", {})
        
        if not properties:
            return {}

        request = str(request)

        args = {}

        for name in properties:

            lname = name.lower()

            if any(k in lname for k in (
                "query",
                "search",
                "keyword",
                "text",
                "prompt",
                "title",
                "topic",
                "article",
                "page",
            )):
                args[name] = request

            elif any(k in lname for k in (
                "symbol",
                "ticker",
                "token",
                "coin",
                "asset",
            )):
                words = request.split()
                if words:
                    args[name] = words[-1].upper()

        return args
