import httpx


class AsyncHTTPClient:

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=60,
            follow_redirects=True,
        )

    async def post(
        self,
        url,
        *,
        headers=None,
        json=None,
    ):
        return await self.client.post(
            url,
            headers=headers,
            json=json,
        )

    async def close(self):
        await self.client.aclose()


http = AsyncHTTPClient()
