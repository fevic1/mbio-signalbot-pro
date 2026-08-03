import asyncio


class ToolExecutor:

    async def execute(
        self,
        registry,
        capability_plan,
    ):

        results = []

        async def _call(item):

            try:

                output = await registry.invoke_tool(
                    item["server"],
                    item["tool"],
                    {},
                )

                return {
                    "server": item["server"],
                    "tool": item["tool"],
                    "success": True,
                    "result": output,
                }

            except Exception as exc:

                return {
                    "server": item["server"],
                    "tool": item["tool"],
                    "success": False,
                    "error": str(exc),
                }

        tasks = [
            _call(item)
            for item in capability_plan
        ]

        if tasks:
            results = await asyncio.gather(*tasks)

        return results
