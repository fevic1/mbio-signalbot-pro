class ProviderError(Exception):
    pass


class AuthenticationError(ProviderError):
    pass


class ProviderUnavailable(ProviderError):
    pass


class RateLimitError(ProviderError):
    pass


class TimeoutError(ProviderError):
    pass
