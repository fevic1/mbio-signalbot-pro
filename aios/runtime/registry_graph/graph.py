class RuntimeRegistryGraph:

    def __init__(self):
        self._nodes = {}
        self._edges = {}

    def add(self, name: str, value):
        self._nodes[name] = value
        self._edges.setdefault(name, set())
        return value

    def connect(self, source: str, target: str):
        self._edges.setdefault(source, set()).add(target)

    def remove(self, name: str):
        self._nodes.pop(name, None)
        self._edges.pop(name, None)

        for targets in self._edges.values():
            targets.discard(name)

    def get(self, name: str):
        return self._nodes.get(name)

    def dependencies(self, name: str):
        return tuple(
            sorted(
                self._edges.get(name, set())
            )
        )

    def nodes(self):
        return tuple(sorted(self._nodes))

    def export(self):
        return {
            "nodes": list(self.nodes()),
            "edges": {
                key: sorted(value)
                for key, value in self._edges.items()
            },
        }

    def clear(self):
        self._nodes.clear()
        self._edges.clear()

    def __contains__(self, name):
        return name in self._nodes

    def __len__(self):
        return len(self._nodes)
