from .models import Node, Edge


class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def neighbors(self, node_id):

        return [
            e.target
            for e in self.edges
            if e.source == node_id
        ]

    def node_count(self):
        return len(self.nodes)

    def edge_count(self):
        return len(self.edges)
