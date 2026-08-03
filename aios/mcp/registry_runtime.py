from importlib import import_module
from pathlib import Path

import yaml


class MCPRegistry:

    def __init__(self, registry_file="aios/mcp/registry.yaml"):
        self.registry_file = Path(registry_file)
        self._servers = {}

    def load(self):

        self._servers.clear()

        data = yaml.safe_load(
            self.registry_file.read_text()
        ) or {}

        for name in data.get("servers", {}):

            package = import_module(
                f"aios.mcp.servers.{name}"
            )

            server_cls = None

            for obj in package.__dict__.values():

                if (
                    isinstance(obj, type)
                    and obj.__name__.endswith("Server")
                ):
                    server_cls = obj
                    break

            if server_cls is None:
                raise RuntimeError(
                    f"No Server class exported by {name}"
                )

            self._servers[name] = server_cls()

        return self._servers

    def servers(self):
        return self._servers

    async def list_tools(self):

        tools = []

        for server_name, server in self._servers.items():

            for tool in await server.list_tools():

                item = dict(tool)
                item["server"] = server_name

                tools.append(item)

        return tools


registry = MCPRegistry()
