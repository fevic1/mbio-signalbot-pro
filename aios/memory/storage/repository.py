from aios.core.identifiable import Identifiable

import json

from ..models import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    MemoryMetadata,
)


class MemoryRepository(Identifiable):


    def __init__(
        self,
        database,
    ):

        self.db = database



    def save(
        self,
        memory: MemoryRecord,
    ):

        self.db.execute(
            """
            INSERT OR REPLACE INTO memories

            VALUES (?, ?, ?, ?, ?, ?)

            """,
            (
                memory.id,

                memory.memory_type.value,

                memory.importance.value,

                json.dumps(
                    memory.content
                ),

                json.dumps(
                    {
                        "source":
                            memory.metadata.source,

                        "tags":
                            memory.metadata.tags,

                        "confidence":
                            memory.metadata.confidence,

                        "access_count":
                            memory.metadata.access_count,
                    }
                ),

                memory.created_at,
            ),
        )


        return memory



    def all(
        self,
    ):

        cursor = self.db.execute(
            """
            SELECT *
            FROM memories
            ORDER BY created_at
            """
        )


        results = []


        for row in cursor.fetchall():

            results.append(
                self._convert(row)
            )


        return results



    def _convert(
        self,
        row,
    ):

        return MemoryRecord(

            content=json.loads(
                row[3]
            ),

            memory_type=MemoryType(
                row[1]
            ),

            importance=MemoryImportance(
                row[2]
            ),

            metadata=MemoryMetadata(
                **json.loads(
                    row[4]
                )
            ),

            id=row[0],

            created_at=row[5],
        )
