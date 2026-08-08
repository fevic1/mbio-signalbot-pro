from __future__ import annotations

import json
import logging
from difflib import SequenceMatcher
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import EntityType

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class AliasEntry:
    """A single alias mapping with metadata."""
    alias: str
    canonical_name: str
    entity_type: EntityType
    confidence: float = 1.0
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = field(default_factory=dict)


class AliasIndex:
    """
    Dynamic, persistent alias management for entity resolution.
    """
    __slots__ = ("_aliases", "_lock", "_version", "_last_modified")
    
    def __init__(self, initial_aliases: Optional[Dict[str, Tuple[str, EntityType]]] = None):
        self._aliases: Dict[str, AliasEntry] = {}
        self._lock = threading.RLock()
        self._version = 1
        self._last_modified = datetime.now(timezone.utc)
        
        if initial_aliases:
            for alias, (canonical_name, entity_type) in initial_aliases.items():
                self.add_alias(alias, canonical_name, entity_type, source="initial")
    
    def lookup(self, raw_string: str) -> Optional[Tuple[str, EntityType]]:
        normalized = self._normalize(raw_string)
        with self._lock:
            entry = self._aliases.get(normalized)
            if entry:
                return (entry.canonical_name, entry.entity_type)
            return None
    
    def fuzzy_lookup(self, raw_string: str, threshold: float = 0.8) -> Optional[Tuple[str, EntityType, float]]:
        normalized = self._normalize(raw_string)
        with self._lock:
            best_match = None
            best_score = 0.0
            for alias, entry in self._aliases.items():
                score = self._calculate_similarity(normalized, alias)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = (entry.canonical_name, entry.entity_type, score)
            return best_match
    
    def add_alias(self, alias: str, canonical_name: str, entity_type: EntityType, confidence: float = 1.0, source: str = "manual", metadata: Optional[Dict[str, str]] = None) -> AliasEntry:
        normalized = self._normalize(alias)
        with self._lock:
            now = datetime.now(timezone.utc)
            if normalized in self._aliases:
                existing = self._aliases[normalized]
                entry = AliasEntry(
                    alias=normalized, canonical_name=canonical_name, entity_type=entity_type,
                    confidence=confidence, source=source, created_at=existing.created_at,
                    updated_at=now, metadata=metadata or existing.metadata,
                )
            else:
                entry = AliasEntry(
                    alias=normalized, canonical_name=canonical_name, entity_type=entity_type,
                    confidence=confidence, source=source, created_at=now, updated_at=now,
                    metadata=metadata or {},
                )
            self._aliases[normalized] = entry
            self._version += 1
            self._last_modified = now
            return entry
    
    def remove_alias(self, alias: str) -> bool:
        normalized = self._normalize(alias)
        with self._lock:
            if normalized in self._aliases:
                del self._aliases[normalized]
                self._version += 1
                self._last_modified = datetime.now(timezone.utc)
                return True
            return False
    
    def get_alias(self, alias: str) -> Optional[AliasEntry]:
        normalized = self._normalize(alias)
        with self._lock:
            return self._aliases.get(normalized)
    
    def get_all_aliases(self) -> Tuple[AliasEntry, ...]:
        with self._lock:
            return tuple(self._aliases.values())
    
    def add_aliases_batch(self, aliases: List[Tuple[str, str, EntityType]]) -> int:
        count = 0
        with self._lock:
            for alias, canonical_name, entity_type in aliases:
                self.add_alias(alias, canonical_name, entity_type)
                count += 1
        return count
    
    def merge(self, other: "AliasIndex", overwrite: bool = False) -> int:
        count = 0
        with self._lock:
            for entry in other.get_all_aliases():
                if entry.alias not in self._aliases or overwrite:
                    self._aliases[entry.alias] = entry
                    count += 1
            if count > 0:
                self._version += 1
                self._last_modified = datetime.now(timezone.utc)
        return count
    
    def export_json(self) -> str:
        with self._lock:
            data = {
                "version": self._version,
                "last_modified": self._last_modified.isoformat(),
                "aliases": [
                    {
                        "alias": entry.alias, "canonical_name": entry.canonical_name,
                        "entity_type": entry.entity_type.value, "confidence": entry.confidence,
                        "source": entry.source, "created_at": entry.created_at.isoformat(),
                        "updated_at": entry.updated_at.isoformat(), "metadata": entry.metadata,
                    }
                    for entry in self._aliases.values()
                ],
            }
            return json.dumps(data, indent=2)
    
    def import_json(self, json_str: str, overwrite: bool = False) -> int:
        data = json.loads(json_str)
        count = 0
        with self._lock:
            for alias_data in data.get("aliases", []):
                alias = alias_data["alias"]
                if alias not in self._aliases or overwrite:
                    entry = AliasEntry(
                        alias=alias, canonical_name=alias_data["canonical_name"],
                        entity_type=EntityType(alias_data["entity_type"]),
                        confidence=alias_data.get("confidence", 1.0),
                        source=alias_data.get("source", "import"),
                        created_at=datetime.fromisoformat(alias_data["created_at"]),
                        updated_at=datetime.fromisoformat(alias_data["updated_at"]),
                        metadata=alias_data.get("metadata", {}),
                    )
                    self._aliases[alias] = entry
                    count += 1
            if count > 0:
                self._version += 1
                self._last_modified = datetime.now(timezone.utc)
        return count
    
    def save(self, filepath: str | Path) -> None:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        json_str = self.export_json()
        temp_path = filepath.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            f.write(json_str)
        temp_path.rename(filepath)
    
    def load(self, filepath: str | Path) -> int:
        filepath = Path(filepath)
        if not filepath.exists():
            return 0
        with open(filepath, 'r') as f:
            json_str = f.read()
        return self.import_json(json_str, overwrite=True)
    
    def version(self) -> int:
        with self._lock:
            return self._version
    
    def size(self) -> int:
        with self._lock:
            return len(self._aliases)
    
    def stats(self) -> Dict[str, int]:
        with self._lock:
            type_counts: Dict[str, int] = {}
            for entry in self._aliases.values():
                type_name = entry.entity_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            return {"total_aliases": len(self._aliases), "version": self._version, "by_type": type_counts}
    
    def _normalize(self, text: str) -> str:
        normalized = text.strip().lower()
        normalized = re.sub(r'^\$|[.,;:!?\"\']+$', '', normalized)
        return normalized
    
    def _calculate_similarity(self, a: str, b: str) -> float:
        """
        Returns a similarity score between 0.0 and 1.0.
        Uses difflib SequenceMatcher for robust typo tolerance.
        """
        return SequenceMatcher(None, a, b).ratio()
