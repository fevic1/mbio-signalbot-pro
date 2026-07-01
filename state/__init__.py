# state/__init__.py — Package initialization
# Fixed: Only import what actually exists in state_manager.py

try:
    from .state_manager import state  # If 'state' object exists
except ImportError:
    # Fallback: import the module, not the object
    from . import state_manager as state  # type: ignore

# Expose user_manager for multi-user support (additive)
from . import user_manager  # type: ignore

__all__ = ["state", "user_manager"]
