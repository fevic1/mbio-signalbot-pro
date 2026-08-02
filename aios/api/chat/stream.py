from typing import AsyncGenerator


async def stream_response(
    text: str,
) -> AsyncGenerator[str, None]:
    # Stream exact text slices. Splitting on whitespace destroyed Markdown
    # newlines and collapsed headings, lists, and paragraphs into one wall.
    chunk_size = 64
    for offset in range(0, len(text), chunk_size):
        yield text[offset:offset + chunk_size]
