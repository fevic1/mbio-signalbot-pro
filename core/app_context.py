"""
core/app_context.py — Application Lifecycle & Dependency Injection
Owns the lifecycle of all shared resources (HLExecutor, HIP-4, etc.).
Created once at startup, passed explicitly to consumers.
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

class AppContext:
    """
    Explicit lifecycle manager. No globals, no magic singletons.
    """
    
    def __init__(self):
        self._executor = None
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Called once during app startup. Thread-safe."""
        async with self._lock:
            if self._initialized:
                logger.warning("AppContext already initialized, skipping")
                return
            
            from execution.hl_executor import HLExecutor
            # Create the ONE true instance
            # Use singleton factory to ensure single initialization
            from execution.hl_executor import get_hl_executor
            self._executor = get_hl_executor()
            
            self._initialized = True
            logger.info("✅ AppContext initialized. HLExecutor singleton locked.")
    
    @property
    def executor(self):
        """Access the executor. Raises if not initialized."""
        if not self._initialized or self._executor is None:
            raise RuntimeError("AppContext not initialized. Call initialize() first.")
        return self._executor
    
    async def shutdown(self):
        """Graceful shutdown. Clears references."""
        async with self._lock:
            self._executor = None
            self._initialized = False
            logger.info("🔒 AppContext shutdown complete")

# Module-level instance. Not a singleton pattern, just a managed lifecycle object.
app_context = AppContext()
