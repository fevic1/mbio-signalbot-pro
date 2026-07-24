from ..search import MemoryRetriever
from ..activation import MemoryRanker
from ..context import MemoryContextAssembler


class MemoryIntelligenceEngine:


    def __init__(
        self,
        router,
        registry,
        graph=None,
    ):

        self.router = router

        self.registry = registry

        self.graph = graph

        self.retriever = MemoryRetriever(
            router
        )

        self.ranker = MemoryRanker()

        self.context = MemoryContextAssembler(
            registry
        )



    def query(
        self,
        memory_query,
    ):

        results = (
            self.retriever.search_memory(
                memory_query.text
            )
        )


        ranked = self.ranker.rank(
            [
                item["record"]
                for item in results
            ]
        )


        response = {

            "query":
                memory_query.text,

            "memories":
                [
                    memory.describe()
                    for memory in ranked[
                        :memory_query.limit
                    ]
                ],
        }


        if memory_query.include_context:

            response[
                "context"
            ] = self.context.build()


        if (
            memory_query.include_graph
            and self.graph
        ):

            response[
                "graph"
            ] = self.graph.describe()


        return response
