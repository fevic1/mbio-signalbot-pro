class ProjectTracker:


    def progress(
        self,
        project,
    ):

        total = len(
            project.milestones
        )

        if total == 0:

            return {
                "progress": 0,
                "status": project.status,
            }


        completed = len(
            [
                milestone
                for milestone in project.milestones
                if milestone.get(
                    "status"
                )
                == "completed"
            ]
        )


        return {
            "progress": (
                completed / total
            ),
            "status": project.status,
        }
