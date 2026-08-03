class TaskPlanner:

    DEFAULT_PIPELINE = [
        "capability_selection",
        "tool_execution",
        "evidence_fusion",
        "reasoning",
        "verification",
        "decision",
        "reflection",
        "memory",
    ]

    def build(
        self,
        request,
        capability_plan,
    ):

        return {
            "request": request,
            "pipeline": list(self.DEFAULT_PIPELINE),
            "tools": [
                x["tool"]
                for x in capability_plan
            ],
            "servers": sorted({
                x["server"]
                for x in capability_plan
            }),
        }
