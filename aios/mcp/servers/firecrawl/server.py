from .tools import TOOLS

class FirecrawlServer:

    name = "firecrawl"

    async def list_tools(self):

        return [

            {
                "name": name,
                **{
                    k:v
                    for k,v in meta.items()
                    if k != "handler"
                }

            }

            for name,meta in TOOLS.items()

        ]

    async def call_tool(
        self,
        tool,
        arguments,
    ):

        return TOOLS[tool]["handler"](
            arguments
        )
