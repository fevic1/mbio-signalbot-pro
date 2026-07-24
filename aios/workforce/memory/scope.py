class AgentMemoryScope:


    DEFAULT_SCOPES = {

        "Architect": [
            "decision",
            "project",
            "knowledge",
        ],


        "Planner": [
            "project",
            "decision",
            "knowledge",
        ],


        "Coder": [
            "knowledge",
            "execution",
            "decision",
        ],


        "Reviewer": [
            "execution",
            "decision",
            "operational",
        ],


        "Tester": [
            "execution",
            "operational",
            "knowledge",
        ],


        "Security Auditor": [
            "operational",
            "decision",
            "knowledge",
        ],


        "Risk Manager": [
            "operational",
            "decision",
            "project",
        ],

    }



    def layers_for(
        self,
        role,
    ):

        return self.DEFAULT_SCOPES.get(
            role,
            [
                "knowledge",
                "execution",
            ],
        )
