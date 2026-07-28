from aios.core.identifiable import Identifiable

from .mailbox import AgentMailbox


class AgentCommunicationManager(Identifiable):


    def __init__(
        self,
        event_bus=None,
    ):

        self.event_bus = event_bus

        self.mailboxes = {}



    def register(
        self,
        agent_name,
    ):

        self.mailboxes[
            agent_name
        ] = AgentMailbox()



    def send(
        self,
        message,
    ):

        mailbox = self.mailboxes.get(
            message.receiver
        )

        if mailbox:

            mailbox.receive(
                message
            )


        if self.event_bus:

            from aios.events import Event

            self.event_bus.publish(
                Event(
                    event_type="agent.message",
                    source=message.sender,
                    payload=message.describe(),
                )
            )



    def history(
        self,
        agent_name,
    ):

        mailbox = self.mailboxes.get(
            agent_name
        )

        if not mailbox:
            return []

        return mailbox.history()
