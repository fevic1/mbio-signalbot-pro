
from .tools import TOOLS

class DefiLlamaServer:

    name="defillama"

    async def list_tools(self):

        return [

{"name":"dl_protocols","category":"defi","read_only":True},
{"name":"dl_protocol","category":"defi","read_only":True},
{"name":"dl_chains","category":"defi","read_only":True},
{"name":"dl_tvl","category":"defi","read_only":True},
{"name":"dl_yields","category":"defi","read_only":True},
{"name":"dl_stablecoins","category":"defi","read_only":True},

]

    async def call_tool(
        self,
        tool,
        arguments,
    ):

        if tool not in TOOLS:
            raise ValueError(tool)

        return TOOLS[tool](arguments)
