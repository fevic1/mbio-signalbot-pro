from aios.runtime.chat import ChatGateway


class ChatRouter:

    def __init__(self):
        self.gateway = ChatGateway()


    async def send(
        self,
        session_id,
        agent,
        message,
    ):

        return await self.gateway.send(
            session_id=session_id,
            agent=agent,
            message=message,
        )
