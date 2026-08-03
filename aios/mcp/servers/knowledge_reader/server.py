from .tools import read_document

class KnowledgeReaderServer:

    name="knowledge_reader"

    async def list_tools(self):

        return [
            {
                "name":"read_document",
                "category":"knowledge",
                "read_only":True,
            }
        ]

    async def call_tool(
        self,
        tool,
        arguments,
    ):

        if tool=="read_document":
            return await read_document(
                arguments["path"]
            )

        raise ValueError(tool)
