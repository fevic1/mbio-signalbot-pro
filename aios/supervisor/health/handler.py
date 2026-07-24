class SupervisorHealthHandler:


    def __init__(
        self,
        supervisor=None,
    ):

        self.supervisor = supervisor



    def handle(
        self,
        event,
    ):

        health = event.payload


        status = health.get(
            "status",
            "unknown",
        )


        decision = {
            "source":
            "runtime_health",

            "status":
            status,

            "action":
            self._action_for(
                status
            ),
        }


        if self.supervisor and hasattr(
            self.supervisor,
            "receive_health",
        ):

            self.supervisor.receive_health(
                decision
            )


        return decision



    def _action_for(
        self,
        status,
    ):

        if status == "ok":

            return "continue"


        if status == "warning":

            return "inspect"


        if status == "failed":

            return "escalate"


        return "unknown"
