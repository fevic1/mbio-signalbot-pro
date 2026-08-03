import asyncio

class ToolExecutor:

    def __init__(self,client):
        self.client=client

    async def execute(self,plan):

        async def run(call):
            result = await self.client.call_tool(
                f"{call.server}__{call.name}",
                call.arguments,
            )

            return {
                "tool":call.name,
                "result":result,
            }

        return await asyncio.gather(
            *[run(c) for c in plan]
        )
