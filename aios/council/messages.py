from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CouncilMessage:

    sender: str

    receiver: str

    content: str

    message_type: str = "discussion"

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(
        self,
    ):

        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.message_type,
            "timestamp": self.timestamp,
        }



class CouncilCommunication:


    def __init__(self):

        self.messages = []



    def send(
        self,
        sender,
        receiver,
        content,
        message_type="discussion",
    ):

        message = CouncilMessage(
            sender,
            receiver,
            content,
            message_type,
        )

        self.messages.append(
            message
        )

        return message



    def history(
        self,
    ):

        return [
            msg.describe()
            for msg
            in self.messages
        ]
