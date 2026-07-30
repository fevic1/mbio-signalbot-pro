from .session import ChatSession
from .message import ChatMessage
from .context_builder import ChatContextBuilder


class ChatGateway:

    def __init__(self):

        self.sessions = {}

        self.context_builder = (
            ChatContextBuilder()
        )


    def session(
        self,
        session_id,
    ):

        if session_id not in self.sessions:

            self.sessions[session_id] = (
                ChatSession(session_id)
            )

        return self.sessions[session_id]


    async def send(
        self,
        session_id,
        agent,
        message,
    ):

        session = self.session(
            session_id
        )

        user_message = ChatMessage(
            role="user",
            content=message,
            agent=agent,
        )

        session.add(
            user_message
        )

        context = self.context_builder.build(
            agent,
            session.history(),
        )

        return {
            "session_id": session_id,
            "agent": agent,
            "context": context,
            "status": "READY_FOR_LLM",
        }
