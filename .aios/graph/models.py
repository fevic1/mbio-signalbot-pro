from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Node:
    id: str
    kind: str
    name: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    relation: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class GraphDocument:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
