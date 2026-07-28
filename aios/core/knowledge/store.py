from aios.core.collections.node_store import NodeStore
from aios.memory.graph.relations import Relation
from aios.core.serialization import serialize


class KnowledgeStore:
    def __init__(self):
        self.entities = NodeStore()
        self.relations: list[Relation] = []

    def add(self, entity):
        self.entities.add(entity)
        return entity

    def connect(self, source, relation, target):
        link = Relation(
            source=source.id,
            target=target.id,
            kind=relation,
        )
        self.relations.append(link)
        return link

    def related(self, entity_id):
        return [
            r
            for r in self.relations
            if r.source == entity_id or r.target == entity_id
        ]

    def describe(self):
        return {
            "entities": [
                serialize(e)
                for e in self.entities.values()
            ],
            "relations": [
                serialize(r)
                for r in self.relations
            ],
        }
