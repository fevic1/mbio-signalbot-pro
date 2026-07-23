from aios.project.graph import TaskGraphManager


class ExecutionPlanner:


    def __init__(self):

        self.graph_manager = TaskGraphManager()


        self.requirements = {

            "research": [

                {
                    "name": "research",
                    "capability": "research",
                    "depends_on": [],
                },

                {
                    "name": "reasoning",
                    "capability": "reasoning",
                    "depends_on": [
                        "research"
                    ],
                },

                {
                    "name": "verification",
                    "capability": "verification",
                    "depends_on": [
                        "reasoning"
                    ],
                },

            ],


            "engineering": [

                {
                    "name": "architecture",
                    "capability": "architecture",
                    "depends_on": [],
                },

                {
                    "name": "coding",
                    "capability": "coding",
                    "depends_on": [
                        "architecture"
                    ],
                },

                {
                    "name": "testing",
                    "capability": "testing",
                    "depends_on": [
                        "coding"
                    ],
                },

            ],

        }



    def create_graph(
        self,
        project_id,
        category,
    ):

        tasks = self.requirements.get(
            category,
            self.requirements["research"]
        )


        return self.graph_manager.create(
            project_id,
            tasks,
        )



    def register_requirements(
        self,
        category,
        tasks,
    ):

        self.requirements[
            category
        ] = tasks
