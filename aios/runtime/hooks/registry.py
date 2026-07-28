class RuntimeHookRegistry:

    def __init__(self):
        self._hooks: dict[str, object] = {}

    def register(self, name: str, hook):
        self._hooks[name] = hook

    def unregister(self, name: str):
        self._hooks.pop(name, None)

    def get(self, name: str, default=None):
        return self._hooks.get(name, default)

    def names(self):
        return tuple(sorted(self._hooks))

    def export(self):
        return {
            name: type(hook).__name__
            for name, hook in self._hooks.items()
        }

    def __contains__(self, name):
        return name in self._hooks

    def __len__(self):
        return len(self._hooks)
