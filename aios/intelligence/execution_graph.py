from collections import defaultdict


class ExecutionGraph:

    def build(self, context):

        graph = defaultdict(list)

        pipeline = (
            context.get("workflow", {})
            .get("workflow", [])
        )

        previous = None

        for node in pipeline:

            name = node["stage"]

            if previous:
                graph[previous].append(name)

            previous = name

        return dict(graph)
