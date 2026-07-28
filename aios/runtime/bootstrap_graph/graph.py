class RuntimeBootstrapGraph:

    def __init__(self):
        self._nodes = {}
        self._dependencies = {}

    def register(self, name: str, action, depends_on=None):
        self._nodes[name] = action
        self._dependencies[name] = set(
            depends_on or []
        )

    def resolve(self):
        ordered = []
        visited = set()
        visiting = set()

        def visit(name):
            if name in visited:
                return

            if name in visiting:
                raise RuntimeError(
                    f"Bootstrap dependency cycle: {name}"
                )

            visiting.add(name)

            for dependency in self._dependencies.get(
                name,
                set(),
            ):
                visit(dependency)

            visiting.remove(name)
            visited.add(name)
            ordered.append(name)

        for name in self._nodes:
            visit(name)

        return tuple(ordered)

    def execute(self):
        results = {}

        for name in self.resolve():
            results[name] = self._nodes[name]()

        return results

    def nodes(self):
        return tuple(sorted(self._nodes))

    def clear(self):
        self._nodes.clear()
        self._dependencies.clear()
