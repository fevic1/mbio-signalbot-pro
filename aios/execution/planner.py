from aios.project.graph import TaskGraphManager


class ExecutionPlanner:


    def __init__(
        self,
        optimizer=None,
    ):

        self.graph_manager = TaskGraphManager()

        self.optimizer = optimizer


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


            "trading": [

                {
                    "name": "market_analysis",
                    "capability": "market_analysis",
                    "depends_on": [],
                },

                {
                    "name": "risk_analysis",
                    "capability": "risk_analysis",
                    "depends_on": [
                        "market_analysis"
                    ],
                },

                {
                    "name": "verification",
                    "capability": "verification",
                    "depends_on": [
                        "risk_analysis"
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

    def get_pipeline(
        self,
        category,
    ):
        tasks = self.requirements.get(category)

        if tasks is None:
            return None

        return [
            task["capability"]
            for task in tasks
        ]


    def register_pipeline(
        self,
        category,
        pipeline,
    ):

        tasks = []

        previous = None

        for capability in pipeline:

            tasks.append(
                {
                    "name": capability,
                    "capability": capability,
                    "depends_on": (
                        []
                        if previous is None
                        else [previous]
                    ),
                }
            )

            previous = capability

        self.requirements[
            category
        ] = tasks


    def list_pipelines(
        self,
    ):
        return sorted(
            self.requirements.keys()
        )


    def get_capabilities(
        self,
        category,
    ):
        tasks = self.requirements.get(
            category,
            self.requirements["research"],
        )

        return [
            task["capability"]
            for task in tasks
        ]

    def resolve(
        self,
        system,
        category,
    ):
        skill = system.skill_registry.get(category)

        if skill is not None:
            return {
                "type": "skill",
                "target": skill,
            }

        return {
            "type": "capability",
            "target": self.get_capabilities(category),
        }


    def get_recommendations(
        self,
    ):

        if self.optimizer:

            return self.optimizer.get_recommendations()

        return []
