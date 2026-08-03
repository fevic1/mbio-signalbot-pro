from .client import DexClient

client = DexClient()

async def search_pairs(query):
    return client.get(f"/dex/search?q={query}")

async def token_pairs(token):
    return client.get(f"/dex/tokens/{token}")

async def pair(address):
    return client.get(f"/dex/pairs/{address}")
