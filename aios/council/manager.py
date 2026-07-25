from .session import CouncilSession

from .validator import PlanValidator
from .critic import Critic
from .auditor import Auditor
from .policy import PolicyEngine
from .consensus import Consensus
from .memory import CouncilMemory

from aios.events import Event


class CouncilManager:


    def __init__(
        self,
        event_bus=None,
        agent_manager=None,
        communication=None,
    ):

        self.event_bus = event_bus

        self.agent_manager = agent_manager

        self.communication = communication

        self.validator = PlanValidator()

        self.critic = Critic()

        self.auditor = Auditor()

        self.policy = PolicyEngine()

        self.consensus = Consensus()

        self.memory = CouncilMemory()

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



    def assign(
        self,
        session,
        agents,
    ):

        assignments = []

        for agent in agents:

            assignments.append(
                {
                    "agent": agent,
                    "question": session.question,
                    "status": "assigned",
                }
            )


        return assignments



    def add_response(
        self,
        session,
        agent,
        response,
    ):

        session.add_response(
            {
                "agent": agent,
                "response": response,
            }
        )



    def review(
        self,
        plan,
    ):

        if self.event_bus:

            self.event_bus.publish(
                Event(
                    "council_review_started",
                    source="council",
                    payload={
                        "plan": plan,
                    },
                )
            )


        validation_issues = (
            self.validator.validate(
                plan
            )
        )


        validator = {
            "valid":
                len(validation_issues) == 0,

            "issues":
                validation_issues,
        }


        critic = self.critic.review(
            plan
        )


        policy = self.policy.review(
            plan
        )


        report = {

            "validator":
                validator,

            "critic":
                critic,

            "policy":
                policy,
        }


        report["consensus"] = (
            self.consensus.vote(
                report
            )
        )


        self.memory.store(
            report
        )


        if self.event_bus:

            self.event_bus.publish(
                Event(
                    "council_review_completed",
                    source="council",
                    payload=report,
                )
            )


        return report



    def audit(
        self,
        execution,
    ):

        report = self.auditor.audit(
            execution
        )


        self.memory.store(
            report
        )


        return report




    def finalize(
        self,
        session,
    ):

        plan = {
            "question":
                session.question,

            "responses":
                session.responses,
        }


        validation_issues = (
            self.validator.validate(
                plan
            )
        )


        validator = {
            "valid":
                len(validation_issues) == 0,

            "issues":
                validation_issues,
        }


        critic = self.critic.review(
            plan
        )


        policy = self.policy.review(
            plan
        )


        report = {

            "validator":
                validator,

            "critic":
                critic,

            "policy":
                policy,

            "responses":
                session.responses,
        }


        decision = self.consensus.vote(
            report
        )


        session.set_decision(
            decision
        )


        self.memory.store(
            {
                "type":
                    "council_decision",

                "session":
                    session.describe(),
            }
        )


        if self.event_bus:

            self.event_bus.publish(
                Event(
                    "council_decision_created",
                    source="council",
                    payload={
                        "session":
                            session.describe()
                    },
                )
            )


        return decision


    def history(self):

        return [
            session.describe()
            for session
            in self.sessions
        ]
