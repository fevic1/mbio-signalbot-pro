from aios.decision import (
    ProposalBuilder,
    DeliberationEngine,
    DecisionEvaluator,
    DecisionEngine,
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

        decision = self.decision_engine.decide(
            proposal,
            deliberation,
            context=context,
        )

        return {
            "proposal": proposal.summary(),
            "deliberation": deliberation,
            "decision": decision,
        }
