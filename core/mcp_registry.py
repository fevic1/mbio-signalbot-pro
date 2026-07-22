"""MCP Registry for dynamic tool discovery and management."""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    server_id: str
    name: str
    description: Optional[str] = None
    api_key: Optional[str] = None
    rate_limit_per_min: int = 60
    endpoint: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None


class MCPRegistry:
    """Registry for Model Context Protocol servers and their tools."""

    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        logger.info("[INIT] MCP Registry initialized")

    async def register_server(self, config: MCPServerConfig) -> bool:
        """Register a new MCP server with its configuration."""
        async with self._lock:
            if config.server_id in self._servers:
                logger.warning(f"[DUPLICATE] MCP Server already registered: {config.server_id}")
                return False

            self._servers[config.server_id] = config
            self._tools[config.server_id] = {}
            logger.info(f"[OK] MCP Server registered: {config.name} ({config.server_id})")
            return True

    async def unregister_server(self, server_id: str) -> bool:
        """Remove an MCP server and its tools."""
        async with self._lock:
            if server_id not in self._servers:
                return False

            del self._servers[server_id]
            del self._tools[server_id]
            logger.info(f"[REMOVED] MCP Server unregistered: {server_id}")
            return True

    async def register_tool(self, server_id: str, tool_name: str, tool_schema: Dict[str, Any]) -> bool:
        """Register a tool from an MCP server."""
        async with self._lock:
            if server_id not in self._servers:
                logger.error(f"[ERROR] Cannot register tool: server {server_id} not found")
                return False

            self._tools[server_id][tool_name] = tool_schema
            logger.debug(f"[TOOL] Registered tool '{tool_name}' for server {server_id}")
            return True

    async def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Get server configuration by ID."""
        async with self._lock:
            return self._servers.get(server_id)

    async def get_tools(self, server_id: str) -> Dict[str, Any]:
        """Get all tools for a specific server."""
        async with self._lock:
            return self._tools.get(server_id, {})

    async def get_all_servers(self) -> List[MCPServerConfig]:
        """Get all registered servers."""
        async with self._lock:
            return list(self._servers.values())

    async def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all tools across all servers."""
        async with self._lock:
            return dict(self._tools)

    async def update_heartbeat(self, server_id: str) -> bool:
        """Update heartbeat timestamp for a server."""
        async with self._lock:
            if server_id not in self._servers:
                return False

            self._servers[server_id].last_heartbeat = datetime.utcnow()
            return True

    async def is_server_alive(self, server_id: str, timeout_seconds: int = 60) -> bool:
        """Check if a server is alive based on heartbeat."""
        async with self._lock:
            if server_id not in self._servers:
                return False

            server = self._servers[server_id]
            if server.last_heartbeat is None:
                return False

            elapsed = (datetime.utcnow() - server.last_heartbeat).total_seconds()
            return elapsed < timeout_seconds


# Singleton instance
mcp_registry = MCPRegistry()
