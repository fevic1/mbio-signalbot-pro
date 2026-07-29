from .entities import Entity
from .relations import Relation


__all__ = [
    "Entity",
    "Relation",
    "KnowledgeGraph",
]


def __getattr__(name):
    if name == "KnowledgeGraph":
        from .knowledge_graph import KnowledgeGraph
        return KnowledgeGraph

    raise AttributeError(name)
