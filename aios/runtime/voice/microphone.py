from typing import AsyncIterator


class MicrophoneStream:

    def __init__(self):
        self.active = False

    async def start(self):
        self.active = True

    async def stop(self):
        self.active = False

    async def stream(self) -> AsyncIterator[bytes]:
        while self.active:
            yield b""
