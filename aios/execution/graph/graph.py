from collections import deque

from .node import ExecutionNode


class ExecutionGraph:

    def __init__(self):
        self._nodes: dict[str, ExecutionNode] = {}

    def add_node(self, node: ExecutionNode):
        self._nodes[node.id] = node
        return node

    def add_dependency(self, parent: str, child: str):
        self._nodes[parent].dependents.add(child)
        self._nodes[child].dependencies.add(parent)

    def get(self, node_id: str):
        return self._nodes[node_id]

    def ready(self):
        return [
            n
            for n in self._nodes.values()
            if not n.dependencies
        ]

    def topological_order(self):
        deps = {
            k: set(v.dependencies)
            for k, v in self._nodes.items()
        }

        queue = deque(
            [
                n.id
                for n in self.ready()
            ]
        )

        order = []

        while queue:
            current = queue.popleft()
            order.append(self._nodes[current])

            for nxt in self._nodes[current].dependents:
                deps[nxt].discard(current)
                if not deps[nxt]:
                    queue.append(nxt)

        if len(order) != len(self._nodes):
            raise ValueError("Cycle detected")

        return order

    def __len__(self):
        return len(self._nodes)
