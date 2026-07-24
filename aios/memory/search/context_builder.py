class MemoryContextBuilder:


    def build(
        self,
        results,
        limit=5,
    ):

        context = []


        for item in results[:limit]:

            record = item["record"]


            context.append(
                {
                    "type":
                        record.memory_type.value,

                    "importance":
                        record.importance.value,

                    "content":
                        record.content,

                    "relevance":
                        item["score"],
                }
            )


        return {
            "memories": context
        }
