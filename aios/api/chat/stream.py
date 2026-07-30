from typing import AsyncGenerator


async def stream_response(
    text: str,
) -> AsyncGenerator[str, None]:

    for chunk in text.split():

        yield chunk + " "
