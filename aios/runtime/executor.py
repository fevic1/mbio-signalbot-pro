from datetime import datetime


class AgentExecutor:

    def __init__(
        self,
        audit=None,
        max_retries=3
    ):
        self.audit = audit
        self.max_retries = max_retries


    def run(
        self,
        agent,
        task
    ):

        attempts = 0


        while attempts < self.max_retries:

            try:

                result = agent.analyze(task)


                if self.audit:

                    self.audit.record(
                        agent.name,
                        task,
                        "success"
                    )


                return result


            except Exception as error:

                attempts += 1


                if self.audit:

                    self.audit.record(
                        agent.name,
                        task,
                        f"failed attempt {attempts}: {error}"
                    )


        return {
            "status": "failed",
            "reason": "maximum retries reached"
        }
