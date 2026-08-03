from .client import WikipediaClient

client = WikipediaClient()

async def search(query):
    return client.search(query)

async def summary(title):
    return client.summary(title)

async def article(title):
    page = client.page(title)
    return {
        "title": page.title,
        "summary": page.summary,
        "url": page.url,
    }
