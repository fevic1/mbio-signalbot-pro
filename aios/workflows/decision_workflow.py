from aios.decision import (
    ProposalBuilder,
    DeliberationEngine,
    DecisionEvaluator,
    DecisionEngine,
    DecisionResult,
    PolicyResult,
)


class DecisionWorkflow:

    def __init__(
        self,
        system,
    ):

        self.system = system

        self.builder = ProposalBuilder()

        self.evaluator = DecisionEvaluator()

        self.deliberation = DeliberationEngine(
            evaluator=self.evaluator
        )

        self.decision_engine = DecisionEngine(
            approval_manager=system.approval_manager,
            audit=system.audit_logger,
            event_bus=system.event_bus,
        )


    def run(
        self,
        task,
        context,
    ):

        return self.execute(
            task,
            context,
        )


    def execute(
        self,
        task,
        context,
    ):

        results = context.results


        proposal = self.builder.build(
            task,
            results,
        )


        deliberation = self.deliberation.evaluate(
            proposal
        )


        raw_decision = self.decision_engine.decide(
            proposal,
            deliberation,
            context=context,
        )


        policy = self.system.decision_policy.validate(
            deliberation
        )


        decision = DecisionResult(
            proposal_id=raw_decision["proposal_id"],
            decision=raw_decision["decision"],
            confidence=raw_decision["confidence"],
            policy=PolicyResult(
                allowed=policy["allowed"],
                issues=policy["issues"],
            ),
            timestamp=raw_decision["timestamp"],
            approval_required=raw_decision["approval_required"],
            approval_id=raw_decision["approval_id"],
            approval_status=raw_decision["approval_status"],
        )


        project = self.system.project_manager.create(
            title=task["name"],
            description=task.get("description", "")
        )

        context.metadata["project"] = project

        context.metadata["decision"] = decision.to_dict()

        return {
           "proposal": proposal.summary(),
           "deliberation": deliberation,
           "decision": decision.to_dict(),
           "project": project,
        }
