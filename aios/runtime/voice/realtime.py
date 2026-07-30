class RealtimeVoice:

    def __init__(
        self,
        microphone,
        stt,
        tts,
        chat_gateway,
    ):
        self.microphone = microphone
        self.stt = stt
        self.tts = tts
        self.chat = chat_gateway


    async def process(
        self,
        session_id,
        agent,
        audio,
    ):

        text = await self.stt.transcribe(
            audio
        )

        response = await self.chat.send(
            session_id=session_id,
            agent=agent,
            message=text,
        )

        await self.tts.synthesize(
            str(response)
        )

        return response
