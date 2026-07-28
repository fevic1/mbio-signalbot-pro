from .document import MemoryDocument


class SemanticMemory:

    def __init__(self):
        self._documents: dict[str, MemoryDocument] = {}

    def add(self, document: MemoryDocument):
        self._documents[document.id] = document
        return document

    def remove(self, document_id: str):
        return self._documents.pop(document_id, None)

    def get(self, document_id: str):
        return self._documents[document_id]

    def search(self, query: str):
        query = query.lower()
        return [
            document
            for document in self._documents.values()
            if query in document.text.lower()
        ]

    def clear(self):
        self._documents.clear()

    def __contains__(self, document_id):
        return document_id in self._documents

    def __len__(self):
        return len(self._documents)
