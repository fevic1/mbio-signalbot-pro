from datetime import datetime, timezone
import uuid


class ImprovementProposer:


    def propose(
        self,
        pattern,
    ):

        return {

            "proposal_id":
                str(uuid.uuid4()),

            "pattern":
                pattern,

            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "status":
                "pending_review",

        }
