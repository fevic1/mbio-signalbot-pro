import logging
from aios.intelligence.parameter_planner import ParameterPlanner
from aios.intelligence.evidence_fusion import EvidenceFusion

logger = logging.getLogger(__name__)


class ToolExecutor:

    async def execute(
        self,
        registry,
        capability_plan,
    ):

        tool_results = []

        for step in capability_plan:

            server = step["server"]
            tool = step["tool"]

            try:

                result = await registry.call_tool(
                    server,
                    tool,
                    step.get(
                        "arguments",
                        {},
                    ),
                )

                tool_results.append(
                    {
                        "server": server,
                        "tool": tool,
                        "arguments": step.get(
                            "arguments",
                            {},
                        ),
                        "success": True,
                        "content": result,
                    }
                )

            except Exception as exc:

                logger.warning(
                    "Tool execution failed: %s/%s - %s",
                    server,
                    tool,
                    exc,
                )

                tool_results.append(
                    {
                        "server": server,
                        "tool": tool,
                        "arguments": step.get(
                            "arguments",
                            {},
                        ),
                        "success": False,
                        "error": str(exc),
                    }
                )

        fused = EvidenceFusion().fuse(
            tool_results
        )

        return {
            "tool_results": tool_results,
            "tool_evidence": fused,
            "verified_sources": fused.get(
                "sources",
                {},
            ),
            "verified_count": fused.get(
                "verified_count",
                0,
            ),
        }
