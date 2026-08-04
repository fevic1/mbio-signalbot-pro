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
        
        self._runtime_servers = {}
        self._runtime_registry = {}
        self._tool_schemas = {}
        
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

    
    async def invoke_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any] | None = None,
    ):

        arguments = arguments or {}

        runtime = getattr(
            self,
            "_runtime_servers",
            {},
        )

        if server_id in runtime:

            return await runtime[server_id].call_tool(
                tool_name,
                arguments,
            )

        async with self._lock:

            tools = self._tools.get(
                server_id,
                {},
            )

            tool = tools.get(
                tool_name,
            )

        if tool is None:
            raise KeyError(
                f"Tool '{tool_name}' not found on server '{server_id}'"
            )

        result = tool(**arguments)

        if asyncio.iscoroutine(result):
            result = await result

        return result


    async def get_tools_for_server(self, server_id: str):
        """Compatibility alias used by the MCP gateway."""
        return await self.get_tools(server_id)

    async def verify_api_key(self, server_id: str, api_key: str) -> bool:
        """Validate the configured API key for a registered server."""
        server = await self.get_server(server_id)
        return bool(server and server.enabled and server.api_key == api_key)

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


    def load_yaml_registry(self):

        from pathlib import Path
        import yaml

        registry = Path("aios/mcp/registry.yaml")

        if not registry.exists():
            return {}

        data = yaml.safe_load(
            registry.read_text()
        ) or {}

        self._runtime_registry = data.get(
            "servers",
            {},
        )

        return self._runtime_registry


    def discover_servers(self):

        from importlib import import_module

        self.load_yaml_registry()

        discovered = {}

        for name in self._runtime_registry:

            try:

                package = import_module(
                    f"aios.mcp.servers.{name}"
                )

                server_cls = None

                for obj in package.__dict__.values():

                    if (
                        isinstance(obj, type)
                        and obj.__name__.endswith(
                            "Server"
                        )
                    ):
                        server_cls = obj
                        break

                if server_cls is None:
                    logger.warning(f"[MCP] No Server exported: {name}")
                    continue

                discovered[name] = server_cls()

            except Exception as exc:

                logger.warning(f"[MCP] Failed loading {name}: {exc}")

        self._runtime_servers = discovered

        return discovered


    async def register_runtime_tools_async(self):

        self._tools = {}

        for server_name, server in self._runtime_servers.items():

            self._tools[server_name] = {}

            try:

                server_tools = await server.list_tools()

                for tool in server_tools:

                    tool_name = tool["name"]
                    
                    # Store the actual schema for the ParameterPlanner
                    self._tool_schemas[server_name][tool_name] = tool

                    async def _call(
                        arguments=None,
                        *,
                        _server=server,
                        _tool=tool_name,
                    ):
                        return await _server.call_tool(
                            _tool,
                            arguments or {},
                        )

                    self._tools[server_name][tool_name] = _call

            except Exception as exc:

                logger.warning(
                    f"[MCP] Failed registering tools for {server_name}: {exc}"
                )


    def register_runtime_server(
        self,
        name,
        server,
    ):

        self._runtime_servers[name] = server


    def list_runtime_servers(self):

        return dict(
            getattr(
                self,
                "_runtime_servers",
                {},
            )
        )


    async def runtime_tools(self):

        tools = []

        for server_name, server in self._runtime_servers.items():

            try:

                server_tools = await server.list_tools()

                for tool in server_tools:

                    item = dict(tool)
                    item["server"] = server_name
                    tools.append(item)

            except Exception as exc:

                logger.warning(f"[MCP] {server_name}: {exc}")

        return tools


    async def call_tool(
        self,
        server,
        tool,
        arguments=None,
    ):

        arguments = arguments or {}

        runtime = self._runtime_servers[
            server
        ]

        return await runtime.call_tool(
            tool,
            arguments,
        )


    async def get_tool_schema_async(
        self,
        server,
        tool,
    ):
        # First, check the explicitly stored schemas
        if server in getattr(self, "_tool_schemas", {}):
            schema = self._tool_schemas[server].get(tool)
            if schema:
                return schema
                
        # Fallback to runtime list_tools if needed
        runtime = self._runtime_servers.get(server)
        if runtime is not None:
            tools = await runtime.list_tools()
            for item in tools:
                if item.get("name") == tool:
                    return item

        return None

mcp_registry = MCPRegistry()
