from datetime import datetime


class AuditLogger:


    def __init__(self):
        self.logs = []


    def record(
        self,
        agent,
        action,
        result
    ):

        self.logs.append(
            {
                "time":
                    datetime.utcnow().isoformat(),

                "agent":
                    agent,

                "action":
                    action,

                "result":
                    result
            }
        )


        return True


    def history(self):
        return self.logs
