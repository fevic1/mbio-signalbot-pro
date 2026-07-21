from datetime import datetime


class DecisionEngine:

    def __init__(
        self,
        approval_manager=None,
        audit=None,
        event_bus=None,
    ):

        self.approval_manager = approval_manager
        self.audit = audit
        self.event_bus = event_bus

        self.decisions = []


    def decide(
        self,
        proposal,
        deliberation,
        context=None,
    ):

        confidence = deliberation.get(
            "confidence",
            0
        )


        if confidence >= 0.85:

            decision = "approved"


        elif confidence >= 0.60:

            decision = "review_required"


        else:

            decision = "rejected"



        result = {

            "proposal": proposal.title,

            "proposal_id": proposal.id,

            "decision": decision,

            "confidence": confidence,

            "timestamp":
                datetime.utcnow().isoformat(),

            "approval_required": False,

            "approval_id": None,

            "approval_status": None,
        }



        if (
            decision == "approved"
            and self.approval_manager
        ):

            approval = self.approval_manager.create_request(

                action=proposal.title,

                requested_by="DecisionEngine",

                payload={

                    "proposal_id": proposal.id,

                    "confidence": confidence,

                    "category": proposal.category,
                }
            )


            result["approval_required"] = True

            result["approval_id"] = approval["id"]

            result["approval_status"] = approval["status"]



        self.decisions.append(
            result
        )


        if context:


            context.emit(
                "decision_created",
                result,
            )



        if self.audit:

            self.audit.record(

                "DecisionEngine",

                proposal.title,

                decision,
            )



        return result



    def history(self):

        return self.decisions
