from .parser import Parser
from .chunker import Chunker

parser=Parser()
chunker=Chunker()

async def read_document(path):

    text=parser.parse(path)

    chunks=chunker.split(text)

    return {
        "chunks":chunks,
        "count":len(chunks),
    }
