from fastapi import APIRouter, Request
from aios.memory.intelligence.query import MemoryQuery

router = APIRouter()


@router.get("/aios/memory")
async def list_memory(request: Request):
    system = request.app.state.aios

    memory = system.get(
        "memory_intelligence"
    )

    result = memory.query(
        MemoryQuery(
            text="",
            limit=10,
        )
    )

    return result
