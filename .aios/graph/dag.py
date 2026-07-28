from collections import defaultdict


class DAG:

    def __init__(self):
        self.graph = defaultdict(set)

    def add_edge(self, parent, child):
        self.graph[parent].add(child)

    def children(self, node):
        return sorted(self.graph[node])

    def nodes(self):

        result = set(self.graph)

        for values in self.graph.values():
            result.update(values)

        return sorted(result)
