from .models import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
)


class BaseMemoryStore:


    def __init__(self):

        self.records = []



    def save(
        self,
        memory: MemoryRecord,
    ):

        self.records.append(
            memory
        )

        return memory



    def all(self):

        return self.records



    def recent(
        self,
        limit=10,
    ):

        return self.records[-limit:]



    def find_by_importance(
        self,
        importance,
    ):

        return [
            record
            for record in self.records
            if record.importance == importance
        ]



    def search_tag(
        self,
        tag,
    ):

        return [
            record
            for record in self.records
            if tag in record.metadata.tags
        ]



class ProjectMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.PROJECT



class AgentMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.AGENT



class DecisionMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.DECISION



class KnowledgeMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.KNOWLEDGE



class OperationalMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.OPERATIONAL



class FeedbackMemoryStore(BaseMemoryStore):


    memory_type = MemoryType.FEEDBACK
