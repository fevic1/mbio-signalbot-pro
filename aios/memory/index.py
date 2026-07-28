from aios.core.identifiable import Identifiable

import uuid
from datetime import datetime, timezone


class MemoryIndex(Identifiable):


    def __init__(self):

        self.items = []



    def add(
        self,
        category,
        data,
    ):

        item = {

            "id":
                str(uuid.uuid4()),

            "category":
                category,

            "data":
                data,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        self.items.append(
            item
        )

        return item



    def all(
        self,
    ):

        return self.items
