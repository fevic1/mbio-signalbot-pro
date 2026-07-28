
class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, name, handler, permissions=None):
        self.tools[name] = {
            "handler": handler,
            "permissions": permissions or [],
        }

    def execute(self, name, *args, **kwargs):
        tool = self.tools[name]

        return tool["handler"](
            *args,
            **kwargs
        )

    def get(self, name):
        return self.tools.get(name)

    def list(self):
        return tuple(self.tools)

    def remove(self, name):
        return self.tools.pop(
            name,
            None
        )
