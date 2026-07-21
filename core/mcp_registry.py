"""
Multi-MCP Registry Manager
Dynamically manages multiple MCP server configurations and tool modules.
"""
import asyncio
import logging
from typing import Dict, Optional, Callable, Any
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPServerConfig(BaseModel):
    """Configuration for a registered MCP server/plugin."""
    server_id: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-z0-9_-]+$")
    name: str
    description: str
    api_key: str = Field(..., min_length=16) # Enforce strong API keys
    rate_limit_per_min: int = Field(default=60, ge=10, le=1000)
    is_active: bool = True

class MCPRegistry:
    """
    Thread-safe registry for managing multiple MCP server configurations.
    """
    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._tools: Dict[str, Dict[str, Callable]] = {}  # server_id -> {tool_name: func}
        self._lock = asyncio.Lock() # MANDATORY: Protects state mutations

    async def register_server(self, config: MCPServerConfig) -> bool:
        """Register a new MCP server configuration."""
        async with self._lock:
            if config.server_id in self._servers:
                logger.warning(f"MCP Server '{config.server_id}' already exists.")
                return False
            
            self._servers[config.server_id] = config
            self._tools[config.server_id] = {}
            logger.info(f"✅ MCP Server registered: {config.name} ({config.server_id})")
            return True

    async def unregister_server(self, server_id: str) -> bool:
        """Remove an MCP server and its tools."""
        async with self._lock:
            if server_id not in self._servers:
                return False
            
            del self._servers[server_id]
            del self._tools[server_id]
            logger.info(f"🗑️ MCP Server unregistered: {server_id}")
            return True

    async def register_tool(self, server_id: str, tool_name: str, func: Callable) -> bool:
        """Dynamically register a tool to a specific MCP server."""
        async with self._lock:
            if server_id not in self._servers:
                logger.error(f"Cannot register tool: Server '{server_id}' not found.")
                return False
            
            if not self._servers[server_id].is_active:
                logger.warning(f"Cannot register tool: Server '{server_id}' is inactive.")
                return False

            self._tools[server_id][tool_name] = func
            return True

    async def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Retrieve server config (read-only, no lock needed for dict get, but safe)."""
        async with self._lock:
            return self._servers.get(server_id)

    async def get_all_active_servers(self) -> list[MCPServerConfig]:
        """List all active MCP servers."""
        async with self._lock:
            return [srv for srv in self._servers.values() if srv.is_active]

    async def get_tools_for_server(self, server_id: str) -> Dict[str, Callable]:
        """Get all tools for a specific server."""
        async with self._lock:
            return self._tools.get(server_id, {})
            
    async def verify_api_key(self, server_id: str, api_key: str) -> bool:
        """Verify API key for a specific server."""
        async with self._lock:
            server = self._servers.get(server_id)
            return server and server.api_key == api_key

# Global singleton instance
mcp_registry = MCPRegistry()
