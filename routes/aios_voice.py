from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest

router = APIRouter()


@router.websocket("/ws/aios/voice")
async def aios_voice(websocket: WebSocket):

    await websocket.accept()

    system = websocket.app.state.aios

    executor = CapabilityExecutor(system)

    try:
        while True:
            message = await websocket.receive_text()

            request = CapabilityRequest(
                capability="reasoning",
                context={
                    "message": message,
                    "source": "voice",
                },
            )

            result = await executor.execute(request)

            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass
