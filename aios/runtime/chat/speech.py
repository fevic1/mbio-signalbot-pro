class SpeechPipeline:

    async def transcribe(
        self,
        audio_stream,
    ):
        raise NotImplementedError


    async def synthesize(
        self,
        text,
    ):
        raise NotImplementedError
