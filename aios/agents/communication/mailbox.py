from aios.core.identifiable import Identifiable

class AgentMailbox(Identifiable):


    def __init__(self):

        self.messages = []



    def receive(
        self,
        message,
    ):

        self.messages.append(
            message
        )



    def history(self):

        return [
            message.describe()
            for message
            in self.messages
        ]
