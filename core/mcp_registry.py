"""Provider-agnostic MCP server registry.

The registry stores configuration and discovered tool metadata. Transport and
protocol operations live in ``core.mcp_client`` so providers are never encoded
into the registry.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for a remote MCP server."""

    server_id: str
    name: str
    description: Optional[str] = None
    endpoint: Optional[str] = None
    transport: str = "auto"
    auth_type: str = "none"
    api_key: Optional[str] = None
    auth_header: str = "X-API-Key"
    auth_token: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit_per_min: int = 60
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: Optional[datetime] = None
    last_status: str = "unknown"
    last_error: Optional[str] = None


class MCPRegistry:
    """Concurrency-safe registry for MCP servers and discovered tools."""

    def __init__(self) -> None:
        self._servers: Dict[str, MCPServerConfig] = {}
        self._tools: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
        logger.info("[INIT] MCP Registry initialized")

    async def register_server(self, config: MCPServerConfig) -> bool:
        async with self._lock:
            if config.server_id in self._servers:
                logger.warning("[DUPLICATE] MCP server already registered: %s", config.server_id)
                return False
            self._servers[config.server_id] = config
            self._tools[config.server_id] = {}
            return True

    async def update_server(self, server_id: str, config: MCPServerConfig) -> bool:
        async with self._lock:
            existing = self._servers.get(server_id)
            if existing is None:
                return False
            if config.server_id != server_id:
                raise ValueError("server_id cannot be changed during an update")
            if not config.api_key:
                config.api_key = existing.api_key
            if not config.auth_token:
                config.auth_token = existing.auth_token
            if not config.headers:
                config.headers = dict(existing.headers)
            config.registered_at = existing.registered_at
            config.last_heartbeat = existing.last_heartbeat
            config.last_status = existing.last_status
            config.last_error = existing.last_error
            self._servers[server_id] = config
            return True

    async def unregister_server(self, server_id: str) -> bool:
        async with self._lock:
            if server_id not in self._servers:
                return False
            self._servers.pop(server_id, None)
            self._tools.pop(server_id, None)
            return True

    async def register_tool(self, server_id: str, tool_name: str, tool_schema: Dict[str, Any]) -> bool:
        async with self._lock:
            if server_id not in self._servers:
                return False
            self._tools.setdefault(server_id, {})[tool_name] = tool_schema
            return True

    async def register_tools(self, server_id: str, tools: List[Dict[str, Any]]) -> int:
        async with self._lock:
            if server_id not in self._servers:
                return 0
            bucket = self._tools.setdefault(server_id, {})
            for tool in tools:
                name = str(tool.get("name", "")).strip()
                if name:
                    bucket[name] = tool
            return len(bucket)

    async def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        async with self._lock:
            return self._servers.get(server_id)

    async def get_tools(self, server_id: str) -> Dict[str, Dict[str, Any]]:
        async with self._lock:
            return dict(self._tools.get(server_id, {}))

    async def get_all_servers(self) -> List[MCPServerConfig]:
        async with self._lock:
            return list(self._servers.values())

    async def get_all_active_servers(self) -> List[MCPServerConfig]:
        async with self._lock:
            return [server for server in self._servers.values() if server.enabled]

    async def get_all_tools(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        async with self._lock:
            return {server_id: dict(tools) for server_id, tools in self._tools.items()}

    async def update_health(self, server_id: str, status: str, error: Optional[str] = None) -> bool:
        async with self._lock:
            server = self._servers.get(server_id)
            if server is None:
                return False
            server.last_status = status
            server.last_error = error
            if status in {"healthy", "ready"}:
                server.last_heartbeat = datetime.now(timezone.utc)
            return True

    async def update_heartbeat(self, server_id: str) -> bool:
        return await self.update_health(server_id, "healthy")

    async def is_server_alive(self, server_id: str, timeout_seconds: int = 60) -> bool:
        async with self._lock:
            server = self._servers.get(server_id)
            if server is None or server.last_heartbeat is None:
                return False
            elapsed = (datetime.now(timezone.utc) - server.last_heartbeat).total_seconds()
            return elapsed < timeout_seconds


mcp_registry = MCPRegistry()
