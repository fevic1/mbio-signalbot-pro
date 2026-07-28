from .tool import Tool


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        return tool

    def unregister(self, name: str):
        return self._tools.pop(name, None)

    def get(self, name: str):
        return self._tools[name]

    def exists(self, name: str):
        return name in self._tools

    def list(self):
        return tuple(sorted(self._tools))

    def invoke(self, name: str, *args, **kwargs):
        return self.get(name)(*args, **kwargs)

    def __contains__(self, name):
        return name in self._tools

    def __len__(self):
        return len(self._tools)
