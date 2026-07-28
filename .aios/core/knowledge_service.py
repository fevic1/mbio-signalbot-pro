#!/usr/bin/env python3

import json
from pathlib import Path


class KnowledgeService:

    def __init__(self):
        self.root = Path(".aios/knowledge")
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, collection):
        return self.root / f"{collection}.json"

    def load(self, collection):
        path = self._path(collection)

        if not path.exists():
            return []

        with path.open() as f:
            return json.load(f)

    def save(self, collection, documents):
        with self._path(collection).open("w") as f:
            json.dump(documents, f, indent=2)

    def add(self, collection, title, content, metadata=None):
        docs = self.load(collection)

        docs.append({
            "id": len(docs) + 1,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        })

        self.save(collection, docs)

    def search(self, collection, query):
        query = query.lower()

        return [
            doc for doc in self.load(collection)
            if query in doc["title"].lower()
            or query in doc["content"].lower()
        ]

    def collections(self):
        return sorted(
            p.stem
            for p in self.root.glob("*.json")
        )


knowledge = KnowledgeService()


if __name__ == "__main__":

    knowledge.add(
        "research",
        "Hyperliquid",
        "Institutional perpetual exchange",
        {"source": "manual"}
    )

    knowledge.add(
        "research",
        "AIOS",
        "AI Operating System",
        {"source": "manual"}
    )

    print(knowledge.search("research", "hyper"))
    print(knowledge.collections())
