from .semantic import SemanticSearch


class MemoryRetriever:


    def __init__(
        self,
        memory_router,
    ):

        self.router = memory_router

        self.search = SemanticSearch()



    def search_memory(
        self,
        query,
        memory_type=None,
    ):

        if memory_type:

            records = (
                self.router.retrieve(
                    memory_type
                )
            )

        else:

            records = []


            for store_type in (
                self.router.stores
            ):

                records.extend(
                    self.router.retrieve(
                        store_type
                    )
                )


        return self.search.rank(
            query,
            records,
        )
