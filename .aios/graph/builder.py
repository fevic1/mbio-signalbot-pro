from .graph import Graph


class GraphBuilder:

    def __init__(self):
        self.graph = Graph()

    def add(self, node):
        self.graph.add_node(node)

    def connect(self, edge):
        self.graph.add_edge(edge)

    def build(self):
        return self.graph
