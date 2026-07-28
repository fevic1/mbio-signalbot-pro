from aios.core.repository import Repository

from dataclasses import dataclass, field
from typing import Any

from aios.core.models import Node
from aios.core.collections.node_store import NodeStore


@dataclass(slots=True)
class TaskNode(Node):
    capability: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None


@dataclass(slots=True)
class TaskGraph(Repository):
    project_id: str
    nodes: NodeStore[TaskNode] = field(default_factory=NodeStore)

    def add(self, node: TaskNode):
        self.nodes[node.name] = node

    def get(self, name: str):
        return self.nodes.get(name)

    def runnable(self):
        from aios.core.graph import runnable
        return runnable(self.nodes)
