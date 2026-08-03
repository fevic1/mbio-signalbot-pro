
from .tools import TOOLS

class HyperliquidServer:

    name="hyperliquid"

    async def list_tools(self):

        return [

            {"name":"hl_market_info","category":"market","read_only":True},
            {"name":"hl_all_mids","category":"market","read_only":True},
            {"name":"hl_orderbook","category":"market","read_only":True},
            {"name":"hl_candles","category":"market","read_only":True},
            {"name":"hl_funding","category":"market","read_only":True},
            {"name":"hl_open_orders","category":"account"},
            {"name":"hl_positions","category":"account"},
            {"name":"hl_balances","category":"account"},
            {"name":"hl_place_order","category":"execution"},
            {"name":"hl_cancel_order","category":"execution"},

        ]

    async def call_tool(
        self,
        tool,
        arguments,
    ):

        if tool not in TOOLS:
            raise ValueError(tool)

        return await TOOLS[tool](arguments)
