class WorkflowPlanner:

    def build(
        self,
        task_plan,
        reflection,
        evidence,
    ):

        workflow = []

        for stage in task_plan["pipeline"]:

            workflow.append(
                {
                    "stage": stage,
                    "enabled": True,
                    "status": "pending",
                }
            )

        return {
            "workflow": workflow,
            "tools": task_plan["tools"],
            "servers": task_plan["servers"],
            "reflection": reflection,
            "confidence": evidence.get(
                "confidence",
                0.0,
            ),
        }
