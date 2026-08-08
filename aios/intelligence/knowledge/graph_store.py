from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Iterable, List, Optional, Protocol, Tuple

from .models import EntityType, GraphEdge, RelationType, ResolvedEntity

logger = logging.getLogger(__name__)


class GraphStore(Protocol):
    """Protocol for knowledge graph storage backends."""
    
    def save_entity(self, entity: ResolvedEntity) -> None:
        """Save or update an entity."""
        ...
    
    def save_entities(self, entities: Iterable[ResolvedEntity]) -> int:
        """Bulk save entities. Returns count saved."""
        ...
    
    def load_entity(self, entity_id: str) -> Optional[ResolvedEntity]:
        """Load an entity by ID."""
        ...
    
    def load_all_entities(self) -> List[ResolvedEntity]:
        """Load all entities."""
        ...
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity. Returns True if existed."""
        ...
    
    def save_edge(self, edge: GraphEdge) -> None:
        """Save or update an edge."""
        ...
    
    def save_edges(self, edges: Iterable[GraphEdge]) -> int:
        """Bulk save edges. Returns count saved."""
        ...
    
    def load_edges_for_entity(self, entity_id: str, direction: str = "outgoing") -> List[GraphEdge]:
        """Load edges for an entity."""
        ...
    
    def load_all_edges(self) -> List[GraphEdge]:
        """Load all edges."""
        ...
    
    def delete_edge(self, source_id: str, target_id: str, relation_type: RelationType) -> bool:
        """Delete an edge. Returns True if existed."""
        ...
    
    def clear(self) -> None:
        """Clear all data."""
        ...


class InMemoryGraphStore:
    """In-memory graph store for testing and development."""

    __slots__ = ("_entities", "_edges")
    
    def __init__(self):
        self._entities: Dict[str, ResolvedEntity] = {}
        self._edges: List[GraphEdge] = []
    
    def save_entity(self, entity: ResolvedEntity) -> None:
        self._entities[entity.entity_id] = entity
    
    def save_entities(self, entities: Iterable[ResolvedEntity]) -> int:
        count = 0
        for entity in entities:
            self._entities[entity.entity_id] = entity
            count += 1
        return count
    
    def load_entity(self, entity_id: str) -> Optional[ResolvedEntity]:
        return self._entities.get(entity_id)
    
    def load_all_entities(self) -> List[ResolvedEntity]:
        return list(self._entities.values())
    
    def delete_entity(self, entity_id: str) -> bool:
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False
    
    def save_edge(self, edge: GraphEdge) -> None:
        # Remove existing edge with same source/target/relation
        self._edges = [
            e for e in self._edges
            if not (e.source_id == edge.source_id and 
                    e.target_id == edge.target_id and 
                    e.relation_type == edge.relation_type)
        ]
        self._edges.append(edge)
    
    def save_edges(self, edges: Iterable[GraphEdge]) -> int:
        count = 0
        for edge in edges:
            self.save_edge(edge)
            count += 1
        return count
    
    def load_edges_for_entity(self, entity_id: str, direction: str = "outgoing") -> List[GraphEdge]:
        if direction == "outgoing":
            return [e for e in self._edges if e.source_id == entity_id]
        elif direction == "incoming":
            return [e for e in self._edges if e.target_id == entity_id]
        else:
            raise ValueError(f"Invalid direction: {direction}")
    
    def load_all_edges(self) -> List[GraphEdge]:
        return self._edges.copy()
    
    def delete_edge(self, source_id: str, target_id: str, relation_type: RelationType) -> bool:
        initial_count = len(self._edges)
        self._edges = [
            e for e in self._edges
            if not (e.source_id == source_id and 
                    e.target_id == target_id and 
                    e.relation_type == relation_type)
        ]
        return len(self._edges) < initial_count
    
    def clear(self) -> None:
        self._entities.clear()
        self._edges.clear()


class JsonFileGraphStore:
    """JSON file-based graph store for simple persistence."""

    __slots__ = ("filepath", "_store")
    
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self._store = InMemoryGraphStore()
        self._load()
    
    def _load(self) -> None:
        """Load graph from JSON file."""
        if not self.filepath.exists():
            logger.info(f"Graph file {self.filepath} does not exist, starting fresh")
            return
        
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            
            # Load entities
            for entity_data in data.get('entities', []):
                entity = self._deserialize_entity(entity_data)
                self._store.save_entity(entity)
            
            # Load edges
            for edge_data in data.get('edges', []):
                edge = self._deserialize_edge(edge_data)
                self._store.save_edge(edge)
            
            logger.info(f"Loaded {len(self._store._entities)} entities and {len(self._store._edges)} edges from {self.filepath}")
        
        except Exception as e:
            logger.error(f"Failed to load graph from {self.filepath}: {e}")
            raise
    
    def _save(self) -> None:
        """Save graph to JSON file."""
        try:
            data = {
                'version': '1.0',
                'saved_at': datetime.now(timezone.utc).isoformat(),
                'entities': [self._serialize_entity(e) for e in self._store._entities.values()],
                'edges': [self._serialize_edge(e) for e in self._store._edges],
            }
            
            # Ensure directory exists
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write atomically
            temp_path = self.filepath.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.filepath)
            
            logger.debug(f"Saved graph to {self.filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save graph to {self.filepath}: {e}")
            raise
    
    def _serialize_entity(self, entity: ResolvedEntity) -> Dict:
        """Serialize entity to dict."""
        return {
            'entity_id': entity.entity_id,
            'name': entity.name,
            'entity_type': entity.entity_type.value,
            'aliases': list(entity.aliases),
            'metadata': entity.metadata,
            'created_at': entity.created_at.isoformat(),
            'updated_at': entity.updated_at.isoformat(),
        }
    
    def _deserialize_entity(self, data: Dict) -> ResolvedEntity:
        """Deserialize entity from dict."""
        return ResolvedEntity(
            entity_id=data['entity_id'],
            name=data['name'],
            entity_type=EntityType(data['entity_type']),
            aliases=tuple(data['aliases']),
            metadata=MappingProxyType(dict(data['metadata'])),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
        )
    
    def _serialize_edge(self, edge: GraphEdge) -> Dict:
        """Serialize edge to dict."""
        return {
            'source_id': edge.source_id,
            'target_id': edge.target_id,
            'relation_type': edge.relation_type.value,
            'weight': edge.weight,
            'evidence_count': edge.evidence_count,
            'first_seen': edge.first_seen.isoformat(),
            'last_seen': edge.last_seen.isoformat(),
        }
    
    def _deserialize_edge(self, data: Dict) -> GraphEdge:
        """Deserialize edge from dict."""
        return GraphEdge(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=RelationType(data['relation_type']),
            weight=data['weight'],
            evidence_count=data['evidence_count'],
            first_seen=datetime.fromisoformat(data['first_seen']),
            last_seen=datetime.fromisoformat(data['last_seen']),
        )
    
    # Delegate all methods to internal store, with auto-save
    
    def save_entity(self, entity: ResolvedEntity) -> None:
        self._store.save_entity(entity)
        self._save()
    
    def save_entities(self, entities: Iterable[ResolvedEntity]) -> int:
        count = self._store.save_entities(entities)
        self._save()
        return count
    
    def load_entity(self, entity_id: str) -> Optional[ResolvedEntity]:
        return self._store.load_entity(entity_id)
    
    def load_all_entities(self) -> List[ResolvedEntity]:
        return self._store.load_all_entities()
    
    def delete_entity(self, entity_id: str) -> bool:
        result = self._store.delete_entity(entity_id)
        if result:
            self._save()
        return result
    
    def save_edge(self, edge: GraphEdge) -> None:
        self._store.save_edge(edge)
        self._save()
    
    def save_edges(self, edges: Iterable[GraphEdge]) -> int:
        count = self._store.save_edges(edges)
        self._save()
        return count
    
    def load_edges_for_entity(self, entity_id: str, direction: str = "outgoing") -> List[GraphEdge]:
        return self._store.load_edges_for_entity(entity_id, direction)
    
    def load_all_edges(self) -> List[GraphEdge]:
        return self._store.load_all_edges()
    
    def delete_edge(self, source_id: str, target_id: str, relation_type: RelationType) -> bool:
        result = self._store.delete_edge(source_id, target_id, relation_type)
        if result:
            self._save()
        return result
    
    def clear(self) -> None:
        self._store.clear()
        self._save()
