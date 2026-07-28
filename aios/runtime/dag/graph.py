
from collections import defaultdict, deque


class ExecutionGraph:

    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(set)

    def add_node(self, name, handler):
        self.nodes[name] = handler

    def connect(self, source, target):
        self.edges[source].add(target)

    def resolve(self):
        incoming = {
            node: 0
            for node in self.nodes
        }

        for targets in self.edges.values():
            for target in targets:
                incoming[target] += 1

        queue = deque(
            node
            for node, count in incoming.items()
            if count == 0
        )

        order = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for target in self.edges[node]:
                incoming[target] -= 1

                if incoming[target] == 0:
                    queue.append(target)

        if len(order) != len(self.nodes):
            raise RuntimeError(
                "Execution graph contains cycle"
            )

        return order

    def execute(self, context=None):
        context = context or {}

        for node in self.resolve():
            context = self.nodes[node](context)

        return context
