import sqlite3
from pathlib import Path


class MemoryDatabase:


    def __init__(
        self,
        path="aios_memory.db",
    ):

        self.path = Path(path)

        self.connection = (
            sqlite3.connect(
                self.path
            )
        )

        self._initialize()



    def _initialize(
        self,
    ):

        cursor = self.connection.cursor()


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (

                id TEXT PRIMARY KEY,

                memory_type TEXT NOT NULL,

                importance TEXT NOT NULL,

                content TEXT NOT NULL,

                metadata TEXT NOT NULL,

                created_at TEXT NOT NULL

            )
            """
        )


        self.connection.commit()



    def execute(
        self,
        query,
        params=(),
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            query,
            params,
        )

        self.connection.commit()

        return cursor
