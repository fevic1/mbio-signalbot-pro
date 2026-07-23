import asyncio


async def retry(
    operation,
    retries=3,
    delay=1.0,
):

    last_error = None

    for attempt in range(retries):

        try:
            return await operation()

        except Exception as exc:

            last_error = exc

            if attempt < retries - 1:
                await asyncio.sleep(delay)

    raise last_error
