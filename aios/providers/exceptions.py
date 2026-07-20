class ProviderError(Exception):
    """Base provider exception."""


class AuthenticationError(ProviderError):
    """Invalid or missing API key."""


class ProviderUnavailable(ProviderError):
    """Provider is unavailable."""


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""


class TimeoutError(ProviderError):
    """Provider request timed out."""
