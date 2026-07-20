class MemoryError(Exception):
    """Base AIOS memory exception."""


class MemoryConfigError(MemoryError):
    """Invalid memory configuration."""


class MemoryValidationError(MemoryError):
    """Memory validation failure."""


class MemoryLockError(MemoryError):
    """Memory lock failure."""
