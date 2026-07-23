from dataclasses import dataclass, field
from typing import List
from uuid import uuid4


@dataclass
class TaskNode:

    name: str

    capability: str

    depends_on: List[str] = field(
        default_factory=list
    )

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: str = "pending"

    result: object = None



@dataclass
class TaskGraph:

    project_id: str

    nodes: dict[str, TaskNode] = field(
        default_factory=dict
    )


    def add(
        self,
        node: TaskNode,
    ):

        self.nodes[node.name] = node


    def get(
        self,
        name,
    ):

        return self.nodes.get(name)


    def runnable(self):

        ready = []

        for node in self.nodes.values():

            if node.status != "pending":
                continue


            completed = all(
                self.nodes[d].status == "completed"
                for d in node.depends_on
            )


            if completed:
                ready.append(node)


        return ready
