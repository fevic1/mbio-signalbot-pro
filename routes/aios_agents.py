from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/aios/agents")
async def list_agents(request: Request):
    system = request.app.state.aios
    services = getattr(system, "services", {})
    agent_manager = services.get("agent_manager")

    if agent_manager is None:
        return {
            "success": False,
            "agents": [],
            "error": "Agent manager unavailable",
        }

    agents = agent_manager.describe()

    return {
        "success": True,
        "agents": agents if isinstance(agents, list) else [],
    }
