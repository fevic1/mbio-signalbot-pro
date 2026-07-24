from typing import List, Dict


class TaskGraphBuilder:


    def build(
        self,
        milestones: List[Dict],
    ) -> List[Dict]:

        graph = []


        previous = None


        for milestone in milestones:

            node = {
                "milestone": milestone["name"],
                "depends_on": previous,
                "tasks": [
                    {
                        "name": (
                            f"{milestone['name']} task"
                        ),
                        "status": "pending",
                    }
                ],
            }


            graph.append(
                node
            )


            previous = milestone["name"]


        return graph
