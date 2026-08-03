from .tools import search, summary, article

class WikipediaServer:

    name = "wikipedia"

    async def list_tools(self):
        return [
            {"name":"wiki_search","category":"knowledge"},
            {"name":"wiki_summary","category":"knowledge"},
            {"name":"wiki_article","category":"knowledge"},
        ]

    async def call_tool(self, tool, arguments):

        if tool=="wiki_search":
            return await search(arguments["query"])

        if tool=="wiki_summary":
            return await summary(arguments["title"])

        if tool=="wiki_article":
            return await article(arguments["title"])

        raise ValueError(tool)
