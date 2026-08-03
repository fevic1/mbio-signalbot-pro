
from .tools import TOOLS

class CoinGeckoServer:

    name="coingecko"

    async def list_tools(self):

        return [

{"name":"cg_ping","category":"market","read_only":True},
{"name":"cg_trending","category":"market","read_only":True},
{"name":"cg_search","category":"market","read_only":True},
{"name":"cg_coin","category":"market","read_only":True},
{"name":"cg_markets","category":"market","read_only":True},
{"name":"cg_global","category":"market","read_only":True},

]

    async def call_tool(
        self,
        tool,
        arguments,
    ):

        if tool not in TOOLS:
            raise ValueError(tool)

        return TOOLS[tool](arguments)
