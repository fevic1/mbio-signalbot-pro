from .pool import provider_pool
from .types import ProviderRequest


async def chat(request: ProviderRequest):

    last_error = None

    for provider in provider_pool.ranked():

        if not provider.available():
            continue

        try:
            return await provider.chat(request)

        except Exception as e:
            last_error = e
            continue

    if last_error:
        raise last_error

    raise RuntimeError("No provider available")
