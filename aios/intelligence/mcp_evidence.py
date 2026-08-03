import asyncio


class MCPEvidenceCollector:

    async def collect(
        self,
        registry,
        capability_plan,
    ):

        evidence = []

        for item in capability_plan:

            try:

                result = await registry.call_tool(
                    item["server"],
                    item["tool"],
                    {},
                )

                evidence.append({
                    "server": item["server"],
                    "tool": item["tool"],
                    "success": True,
                    "content": result,
                })

            except Exception as exc:

                evidence.append({
                    "server": item["server"],
                    "tool": item["tool"],
                    "success": False,
                    "error": str(exc),
                })

        return evidence
