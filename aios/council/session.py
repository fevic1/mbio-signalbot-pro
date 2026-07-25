from datetime import datetime, timezone
import uuid


class CouncilSession:


    def __init__(
        self,
        question,
    ):

        self.id = str(
            uuid.uuid4()
        )

        self.question = question

        self.status = "created"

        self.participants = []

        self.assignments = []

        self.messages = []

        self.artifacts = []

        self.responses = []

        self.decision = None

        self.context = {}

        self.created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


    def add_participant(
        self,
        agent,
    ):

        if agent not in self.participants:

            self.participants.append(
                agent
            )


    def add_assignment(
        self,
        assignment,
    ):

        self.assignments.append(
            assignment
        )


    def add_message(
        self,
        message,
    ):

        self.messages.append(
            message
        )


    def add_artifact(
        self,
        artifact,
    ):

        self.artifacts.append(
            artifact
        )


    def add_response(
        self,
        response,
    ):

        self.responses.append(
            response
        )


    def set_context(
        self,
        context,
    ):

        self.context = context



    def set_decision(
        self,
        decision,
    ):

        self.decision = decision

        self.status = "completed"



    def describe(
        self,
    ):

        return {

            "id":
                self.id,

            "question":
                self.question,

            "status":
                self.status,

            "participants":
                self.participants,

            "assignments":
                [
                    a.describe()
                    if hasattr(a, "describe")
                    else a
                    for a in self.assignments
                ],

            "messages":
                [
                    m.describe()
                    if hasattr(m, "describe")
                    else m
                    for m in self.messages
                ],

            "artifacts":
                [
                    a.describe()
                    if hasattr(a, "describe")
                    else a
                    for a in self.artifacts
                ],

            "responses":
                self.responses,

            "context":
                self.context,

            "decision":
                self.decision,

            "created_at":
                self.created_at,
        }
