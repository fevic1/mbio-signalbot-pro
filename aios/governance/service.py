from .detector import IssueDetector
from .council_trigger import CouncilTrigger
from .review_runner import CouncilReviewRunner


class GovernanceService:


    def __init__(
        self,
        council,
        consensus,
    ):

        self.detector = IssueDetector()

        self.trigger = CouncilTrigger(
            council
        )

        self.runner = CouncilReviewRunner(
            council,
            consensus,
        )


    async def report_issue(
        self,
        title,
        description,
        severity,
        source,
    ):

        issue = self.detector.detect(
            title,
            description,
            severity,
            source,
        )


        trigger = self.trigger.evaluate(
            issue
        )


        if trigger["action"] == "council_review":

            return await self.runner.review(
                issue
            )


        return {
            "issue": issue.describe(),
            "action": "auto_fix",
        }
