class RuntimeState:

    def snapshot(self, context):

        return {
            "status": "ready",
            "tool_count": len(
                context.get(
                    "tool_results",
                    [],
                )
            ),
            "workflow_nodes": len(
                context.get(
                    "workflow",
                    {},
                ).get(
                    "workflow",
                    [],
                )
            ),
            "verified": (
                context.get(
                    "verification",
                    {},
                ).get(
                    "passed",
                    False,
                )
            ),
        }
