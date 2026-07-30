from aios.tools import (
    ToolRegistry as CanonicalToolRegistry,
    Tool,
)


class ToolRegistryAdapter:

    def __init__(self):
        self.registry = CanonicalToolRegistry()

    def register(
        self,
        name,
        handler,
        permissions=None,
    ):

        tool = Tool(
            name=name,
            handler=handler,
            metadata={
                "permissions": permissions or []
            },
        )

        return self.registry.register(tool)


    def execute(
        self,
        name,
        *args,
        **kwargs,
    ):

        return self.registry.invoke(
            name,
            *args,
            **kwargs
        )


    def get(self, name):

        return self.registry.get(name)


    def list(self):

        return self.registry.list()


    def remove(self, name):

        return self.registry.unregister(name)
