import inspect
from abc import ABC, abstractmethod
from typing import Any


class MCPClient(ABC):
    @abstractmethod
    async def initialize(self):
        ...

    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        ...


class InProcessMCPClient(MCPClient):
    """Expose selected in-process MCP servers to AIOS."""

    def __init__(
        self,
        registry,
        allowed_servers: set[str] | None = None,
    ):
        self.registry = registry
        self.allowed_servers = (
            set(allowed_servers)
            if allowed_servers is not None
            else None
        )

    async def initialize(self):
        return True

    def _is_allowed(self, server_id: str) -> bool:
        return (
            self.allowed_servers is None
            or server_id in self.allowed_servers
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        tools = await self.registry.get_all_tools()
        definitions = []

        for server_id, server_tools in tools.items():
            if not self._is_allowed(server_id):
                continue

            for tool_name, handler in server_tools.items():
                definitions.append({
                    "name": f"{server_id}__{tool_name}",
                    "description": (
                        inspect.getdoc(handler)
                        or f"{tool_name} from {server_id}"
                    ),
                    "inputSchema": self._input_schema(handler),
                })

        return definitions

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        if "__" not in name:
            raise ValueError(f"Namespaced MCP tool required: {name}")

        server_id, tool_name = name.split("__", 1)

        if not self._is_allowed(server_id):
            raise PermissionError(
                f"MCP server '{server_id}' is not enabled for AIOS"
            )

        return await self.registry.invoke_tool(
            server_id,
            tool_name,
            arguments or {},
        )

    @staticmethod
    def _input_schema(handler) -> dict[str, Any]:
        properties = {}
        required = []

        for parameter in inspect.signature(handler).parameters.values():
            if parameter.name == "self":
                continue

            annotation = parameter.annotation
            json_type = "string"

            if annotation is float:
                json_type = "number"
            elif annotation is int:
                json_type = "integer"
            elif annotation is bool:
                json_type = "boolean"

            properties[parameter.name] = {"type": json_type}

            if parameter.default is inspect.Parameter.empty:
                required.append(parameter.name)

        schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema
