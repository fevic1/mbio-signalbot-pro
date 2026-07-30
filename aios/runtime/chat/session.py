from .message import ChatMessage


class ChatSession:

    def __init__(
        self,
        session_id: str,
    ):

        self.id = session_id

        self.messages: list[ChatMessage] = []


    def add(
        self,
        message: ChatMessage,
    ):

        self.messages.append(
            message
        )


    def history(self):

        return tuple(
            self.messages
        )
