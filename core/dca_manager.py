"""Compatibility facade for callers still importing ``DCAManager``.

The implementation lives exclusively in DCAExecutionEngine. This module contains
no exchange logic and exists only to keep older monitoring integrations wired to
the current engine while they migrate to the canonical import.
"""
from core.dca_execution_engine import DCAExecutionEngine


class DCAManager(DCAExecutionEngine):
    """Compatibility alias for the canonical DCA execution engine."""

    def __init__(self, executor=None):
        super().__init__()
        self._legacy_executor = executor

    @property
    def execution(self):
        # Canonical engine resolves the live executor through AppContext.
        return super().execution
