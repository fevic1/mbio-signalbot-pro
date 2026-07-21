from datetime import datetime


class DecisionManager:

    def __init__(
        self,
        memory=None
    ):
        self.memory = memory
        self.reports = []


    def collect(
        self,
        report
    ):
        self.reports.append(report)


    def decide(
        self,
        subject
    ):

        decision = {

            "subject": subject,

            "timestamp":
                datetime.utcnow().isoformat(),

            "agents":
                self.reports,

            "decision":
                "REVIEW_REQUIRED",

            "confidence":
                0.0,

            "reason":
                "Awaiting final human approval"
        }


        if self.memory:

            self.memory.remember(
                "decision",
                f"{subject} Decision",
                str(decision),
                {
                    "system":
                    "AI Investment Committee"
                }
            )


        return decision
