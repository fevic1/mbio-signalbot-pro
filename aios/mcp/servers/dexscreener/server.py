from .tools import search_pairs, token_pairs, pair

class DexScreenerServer:

    name = "dexscreener"

    async def list_tools(self):
        return [
            {"name":"dex_search"},
            {"name":"dex_token_pairs"},
            {"name":"dex_pair"},
        ]

    async def call_tool(self, tool, arguments):

        if tool=="dex_search":
            return await search_pairs(arguments["query"])

        if tool=="dex_token_pairs":
            return await token_pairs(arguments["token"])

        if tool=="dex_pair":
            return await pair(arguments["pair"])

        raise ValueError(tool)
