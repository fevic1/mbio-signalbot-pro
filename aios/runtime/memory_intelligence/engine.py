
from datetime import datetime, timezone
import uuid


class MemoryIntelligence:

    def __init__(self):
        self.memories = {}

    def store(
        self,
        content,
        category="general",
        metadata=None,
    ):
        memory_id = str(uuid.uuid4())

        memory = {
            "id": memory_id,
            "content": content,
            "category": category,
            "metadata": metadata or {},
            "created": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.memories[memory_id] = memory

        return memory

    def get(self, memory_id):
        return self.memories.get(memory_id)

    def search(self, query):
        query = query.lower()

        return tuple(
            memory
            for memory in self.memories.values()
            if query in str(
                memory["content"]
            ).lower()
        )

    def list(self):
        return tuple(
            self.memories.values()
        )

    def remove(self, memory_id):
        return self.memories.pop(
            memory_id,
            None
        )

    def clear(self):
        self.memories.clear()
