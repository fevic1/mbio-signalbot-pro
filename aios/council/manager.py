from .session import CouncilSession
from .delegation import DelegationManager
from .messages import CouncilCommunication
from .artifacts import ArtifactStore
from .governance import CouncilGovernance
from aios.audit.logger import AuditLogger
from aios.audit.decision_records import DecisionRecordStore
from aios.governance.runtime.decision_builder import DecisionRecordBuilder


class CouncilManager:


    def __init__(
        self,
        agent_manager=None,
        event_bus=None,
        communication=None,
        delegation=None,
        artifacts=None,
        audit=None,
    ):

        self.agent_manager = agent_manager

        self.event_bus = event_bus

        self.delegation = (
            delegation
            if delegation
            else DelegationManager()
        )

        self.communication = (
            communication
            if communication
            else CouncilCommunication()
        )

        self.artifacts = (
            artifacts
            if artifacts
            else ArtifactStore()
        )

        from .report import CouncilReportBuilder
        from .consensus_adapter import ConsensusAdapter

        self.report_builder = CouncilReportBuilder()

        self.consensus_adapter = ConsensusAdapter()

        self.governance = CouncilGovernance()

        self.audit = (
            audit
            if audit
            else AuditLogger()
        )

        self.decision_builder = DecisionRecordBuilder()

        self.decision_records = DecisionRecordStore()

        from .memory import CouncilMemory
        from .memory_bridge import CouncilMemoryBridge

        self.memory = CouncilMemory()

        self.memory_bridge = CouncilMemoryBridge(
            self.memory
        )

        self.sessions = []



    def create_session(
        self,
        question,
    ):

        session = CouncilSession(
            question
        )

        self.sessions.append(
            session
        )

        return session



    def assign_agents(
        self,
        session,
        agents,
    ):

        assignments = []


        for agent in agents:

            session.add_participant(
                agent
            )


            assignment = (
                self.delegation.assign(
                    agent,
                    session.question,
                )
            )


            session.add_assignment(
                assignment
            )


            assignments.append(
                assignment
            )


        return assignments



    def send_message(
        self,
        session,
        sender,
        receiver,
        content,
    ):

        message = (
            self.communication.send(
                sender,
                receiver,
                content,
            )
        )

        session.add_message(
            message
        )

        return message



    def add_response(
        self,
        session,
        agent,
        response,
    ):

        item = {
            "agent": agent,
            "response": response,
        }


        session.add_response(
            item
        )


        return item



    def add_artifact(
        self,
        session,
        artifact,
    ):

        self.artifacts.add(
            artifact
        )

        session.add_artifact(
            artifact
        )

        return artifact



    def get_previous_context(
        self,
        question,
    ):

        return self.memory_bridge.get_context(
            question
        )


    def finalize(
        self,
        session,
        consensus,
    ):

        report = self.report_builder.build(
            session
        )

        normalized = self.consensus_adapter.build(
            report
        )

        decision = consensus.vote(
            normalized
        )

        governance = self.governance.validate(
            normalized
        )

        decision["governance"] = governance

        if not governance["passed"]:

            decision["approved"] = False


        decision_record = self.decision_builder.build(
            decision,
            session,
            governance,
        )

        decision["record_id"] = decision_record["id"]

        self.decision_records.append(
            decision_record
        )


        session.set_decision(
            decision
        )

        self.audit.record(
            session,
            decision,
        )

        self.memory.store(
            session
        )

        if self.event_bus:
            from aios.events.models import AIOSDomainEvent

            self.event_bus.publish(
                AIOSDomainEvent(
                    "council.decision.created",
                    source="council_manager",
                    payload={
                        "decision": decision,
                        "session": session.id,
                    },
                )
            )

        return decision
